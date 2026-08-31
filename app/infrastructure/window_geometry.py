"""
app/infrastructure/window_geometry.py

Helper for centering a Toplevel window.

On a multi-monitor Linux setup, winfo_screenwidth()/screenheight() report
the combined virtual screen spanning all monitors, so centering against
them can place a window on the wrong monitor or straddling the boundary
between two monitors. To avoid that:

- The very first window of the app centers on the monitor currently under
  the mouse pointer (via screeninfo), falling back to the full screen if
  monitor detection is unavailable.
- Every later window centers over the previously shown window's actual
  on-screen rectangle, keeping it on the same monitor as the window it
  replaces.
"""

import tkinter as tk


def _active_monitor_bounds(window: tk.Toplevel) -> tuple[int, int, int, int]:
    """
    Return (x, y, width, height) of the monitor under the mouse pointer.

    Falls back to the full (possibly multi-monitor) screen area if the
    screeninfo package is unavailable or no monitor matches.
    """

    fallback = (0, 0, window.winfo_screenwidth(), window.winfo_screenheight())

    try:
        from screeninfo import get_monitors

        monitors = get_monitors()

        if not monitors:
            return fallback

        pointer_x = window.winfo_pointerx()
        pointer_y = window.winfo_pointery()

        for monitor in monitors:

            if (
                monitor.x <= pointer_x < monitor.x + monitor.width
                and monitor.y <= pointer_y < monitor.y + monitor.height
            ):
                return (monitor.x, monitor.y, monitor.width, monitor.height)

        primary = next(
            (m for m in monitors if getattr(m, "is_primary", False)),
            monitors[0],
        )

        return (primary.x, primary.y, primary.width, primary.height)

    except Exception:
        return fallback


def center_window(
    window: tk.Toplevel,
    width: int,
    height: int,
) -> None:
    """
    Size and position `window` at (width x height), centered over the
    last window shown on the same root. Falls back to centering on the
    monitor under the mouse pointer when no previous window position has
    been recorded yet (i.e. the very first window of the app).
    """

    root = window.master

    rect = getattr(root, "_last_window_rect", None)

    if rect:
        ref_x, ref_y, ref_w, ref_h = rect

    else:
        ref_x, ref_y, ref_w, ref_h = _active_monitor_bounds(window)

    x = ref_x + (ref_w - width) // 2
    y = ref_y + (ref_h - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")

    root._last_window_rect = (x, y, width, height)
