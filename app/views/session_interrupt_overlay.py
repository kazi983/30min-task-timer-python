import tkinter as tk


class SessionInterruptOverlay:
    COLLAPSED_WIDTH = 28
    EXPANDED_WIDTH = 180
    HEIGHT = 60

    def __init__(
        self,
        command,
    ) -> None:
        self.command = command

        root = tk.Tk()
        root.withdraw()
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.65)

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        self.y = int(self.screen_height * 0.3)

        self.frame = tk.Frame(
            self.window,
            bg="#111111",
        )
        self.frame.pack(fill="both", expand=True)

        self.label = tk.Label(
            self.frame,
            text="タスク完了",
            fg="white",
            bg="#111111",
            font=("Yu Gothic UI", 10, "bold"),
        )

        self._collapse()

        for widget in (
            self.window,
            self.frame,
            self.label,
        ):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def show(self):
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()

    def destroy(self):
        self.window.destroy()

    def _collapse(self):
        x = self.screen_width - self.COLLAPSED_WIDTH

        self.window.geometry(f"{self.COLLAPSED_WIDTH}x{self.HEIGHT}+{x}+{self.y}")

        self.label.pack_forget()

    def _expand(self):
        x = self.screen_width - self.EXPANDED_WIDTH

        self.window.geometry(f"{self.EXPANDED_WIDTH}x{self.HEIGHT}+{x}+{self.y}")

        self.label.pack(
            side="left",
            padx=12,
            pady=10,
        )

    def _on_enter(self, _):
        self._expand()

    def _on_leave(self, _):
        self._collapse()

    def _on_click(self, _):
        if self.command:
            self.command()
