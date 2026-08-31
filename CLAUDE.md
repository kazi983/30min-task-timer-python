# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Windows/Linux desktop app (Tkinter) that nags the user every 30 minutes to pick a task and
tracks time spent per task. It also supports a "leave time" schedule that warns/force-stops
work sessions before the user needs to leave.

## Coding Conventions

Write comments, commit messages, and identifiers in English.

## Running

Create the virtual environment and install dependencies (first time only):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

Run the app:

```bash
source .venv/bin/activate
python main.pyw
```

On Ubuntu, additional system packages are required (Tkinter is not bundled, and the tray icon
needs AppIndicator/GI bindings):

```bash
sudo apt install python3-tk fonts-noto-cjk gir1.2-ayatanaappindicator3-0.1 python3-gi
```

Without the GNOME "AppIndicator and KStatusNotifierItem Support" extension, no tray icon will
appear, but the app still runs — `TrayManager.run()` swallows the failure. There is no
build/lint/test tooling configured in this repo (no pytest, no linter config, no CI).

### Test mode

Set `TASK_MODE=test` to shrink timer intervals (30min→5s, snooze 5min→10s) and redirect task
storage to `tasks_test.json` instead of `tasks.json` (see `app/config/constants.py` and
`app/config/paths.py`). Task data lives under the OS app-data dir (`%APPDATA%` on Windows,
`$XDG_CONFIG_HOME` or `~/.30min-task-timer` on Linux).

### Single-instance behavior

`main.pyw` is the entry point, not a module under `app/`. On startup it checks a lock file
(`<tempdir>/30min-task-timer.lock`) containing a port number for a loopback TCP IPC server. If
an instance is already running, the user is asked whether to replace it (sends `SHUTDOWN` over
the socket) or abort; a `FOCUS` command brings the existing window to front. Keep this dance in
mind when changing startup/shutdown logic — killing the process externally (e.g. `kill -9`)
leaves a stale lock file behind.

## Architecture

MVC-ish layering, all wired together imperatively in `AppController` — there is no DI
container or event bus, just constructor injection of callbacks:

- **`app/controllers/app_controller.py`** — top-level orchestrator. Owns all long-lived
  services (`TaskService`, `TimerService`, `SessionService`, `LeaveScheduleService`) and the
  `TrayManager`. Opens/destroys `Toplevel` windows and passes itself down as a set of
  callbacks (`exit_callback`, `open_task_management_callback`, etc.) rather than passing
  itself as an object. When adding a new screen or a new way to exit/restart, wire the
  callback here.
- **`app/controllers/*_controller.py`** — one controller per screen. Each takes its `*View`,
  the relevant service(s), and a handful of navigation/lifecycle callbacks; it binds
  `view.some_button.config(command=self.on_x)` and contains all `messagebox` confirmation
  logic. Views never call services directly.
- **`app/views/*_view.py`** — `tk.Toplevel` subclasses that only build widgets and expose
  them as `self.foo_button` / getter methods (`get_selected_task()`, `get_input_value()`).
  No business logic, no service imports beyond the domain model for typing.
- **`app/models/*_service.py`** — plain Python classes, no Tkinter imports (except
  `TimerService`, which wraps `root.after`/`after_cancel` and is the only sanctioned way
  other code schedules delayed work — don't call `root.after` directly elsewhere).
  - `TaskService` is the persistence layer: in-memory list + full-file JSON read/write on
    every mutation (`app/models/task.py` for the `Task` dataclass and its JSON
    (de)serialization). Deletes are soft (`deleted` flag, filtered out on load).
  - `SessionService` tracks the currently-running (task_id, started_at) pair and produces a
    `SessionResult` (elapsed minutes) on `finish()`. `AppController` always routes
    `session_service.finish()` results through `task_service.record_session()` — do this
    from any new exit/restart/complete path too, or session time silently vanishes.
  - `LeaveScheduleService` schedules two `TimerService` callbacks (a warning and a hard
    stop) relative to a user-entered leave time; `TaskPickerController` wires these to show
    `LeaveScheduleView` in "warning" vs "block" mode.
- **`app/infrastructure/`** — OS integration with no domain knowledge:
  - `tray_manager.py` wraps `pystray`. **Important**: pystray's tray icon runs on a
    non-daemon thread (`icon.run_detached()`). Any code path that terminates the process
    (exit button, tray "終了", IPC `SHUTDOWN`) must call `TrayManager.stop()` or the
    interpreter can hang after `root.destroy()` instead of returning control to the
    terminal. `main.pyw` additionally calls `os._exit(0)` after cleanup as a last-resort
    safety net, since that thread can fail to join even after `stop()` on some Linux setups
    (missing AppIndicator/dbus support).
  - `window_geometry.py`'s `center_window()` keeps every subsequently-opened window on the
    same monitor as the previous one (via a `root._last_window_rect` breadcrumb), only
    falling back to "monitor under the mouse pointer" (via `screeninfo`) for the very first
    window — plain `winfo_screenwidth()` would span all monitors on multi-monitor Linux
    setups and mis-center the window.

### Screen flow

Picker (`TaskPickerView`, "Quick Start") ⇄ Management (`TaskManagementView`) ⇄ Leave-schedule
interstitial (`LeaveScheduleView`). Starting a session destroys the picker window, shows the
floating `SessionInterruptOverlay` (small always-on-top widget, expands on hover, click fires
the "complete session" callback), and schedules the picker to reopen via `TimerService` after
`TIME_MS_INTERVAL`. See the mermaid diagram in `README.md` for the (partly aspirational —
several nodes are marked "coming soon") full screen map.

## Conventions actually in force here

- Every window/controller constructor takes its dependencies (services + navigation
  callbacks) explicitly; nothing is looked up from a global/singleton.
- `_setup_view()` on each view sets `-topmost`, `lift()`, `focus_force()`, and calls
  `center_window()` — copy this pattern for any new `Toplevel`.
- Destructive actions in controllers (`delete`, `complete`, `exit`) go through
  `messagebox.askokcancel(...)` before mutating state.
- Widget styling is per-view, hardcoded hex colors in a local `_UIColors` class at the top of
  each view file — there is no shared theme module.
