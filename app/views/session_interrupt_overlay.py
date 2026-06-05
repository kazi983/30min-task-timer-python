import tkinter as tk


class SessionInterruptOverlay:
    WIDTH_COLLAPSED = 70
    WIDTH_EXPANDED = 80
    HEIGHT = 42

    BG = "#1f2937"
    TEXT = "#f9fafb"
    ACCENT = "#22c55e"

    def __init__(self, command):
        self.command = command

        root = tk.Tk()
        root.withdraw()
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.82)

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        self.y = int(self.screen_height * 0.2)

        self.frame = tk.Frame(
            self.window,
            bg="#554E4E",
        )
        self.frame.pack(fill="both", expand=True)

        self.label = tk.Label(self.frame)
        self.is_expanded = False
        self._collapse()
        self._bind()

    # -------------------------
    # public
    # -------------------------
    def show(self):
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()

    def destroy(self):
        self.window.destroy()

    # -------------------------
    # render
    # -------------------------
    def _render(self, width: int, expanded: bool):
        if expanded:
            # "完了 →"
            self.label = tk.Label(
                self.frame,
                text="完了 ▶",
                fg="white",
                bg="#554E4E",
                font=("Yu Gothic UI", 10, "bold"),
            )

        else:
            # collapsed: just ">"
            self.label = tk.Label(
                self.frame,
                text="▶",
                fg="white",
                bg="#554E4E",
                font=("Yu Gothic UI", 10, "bold"),
            )

        self.label.pack(
            side="left",
            padx=12,
            pady=10,
        )

    # -------------------------
    # state
    # -------------------------
    def _collapse(self):
        w = self.WIDTH_COLLAPSED
        x = self.screen_width - w // 2

        self.window.geometry(f"{w}x{self.HEIGHT}+{x}+{self.y}")
        self.label.pack_forget()
        self._render(w, expanded=False)

    def _expand(self):
        w = self.WIDTH_EXPANDED
        x = self.screen_width - w

        self.window.geometry(f"{w}x{self.HEIGHT}+{x}+{self.y}")
        self.label.pack_forget()
        self._render(w, expanded=True)

    # -------------------------
    # events
    # -------------------------
    def _bind(self):
        for w in (
            self.window,
            self.frame,
            self.label,
        ):
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self._expand()

    def _on_leave(self, _):
        self._collapse()

    def _on_click(self, _):
        if self.command:
            self.command()
