"""
app/views/leave_schedule_view.py
"""

import tkinter as tk
import app.config.constants as c


class _UIColors:
    BG = "#0b1326"
    CARD = "#ffffff"
    BORDER = "#5e85b1"

    BASE = "#dae2fd"

    TEXT_SUB = "#6b7280"
    TEXT_SUB_B = "#00285d"

    ACCENT = "#4d8eff"
    ACCENT_DARK = "#2d3449"

    SELECT_BG = "#e0f2fe"


class LeaveScheduleView(tk.Toplevel):
    """
    FocusLoop - Leave Schedule Overlay

    2 modes:
    - warning: 5 minutes before leave time (dismissible)
    - block: leave time reached (non-dismissible)
    """

    MODE_WARNING = "warning"
    MODE_BLOCK = "block"

    def __init__(self, root: tk.Tk, mode: str = MODE_WARNING) -> None:
        super().__init__(root)

        self.mode = mode

        self.title("FocusLoop")

        self._setup_view()

        # =========================
        # Main container
        # =========================

        self.container = tk.Frame(self, bg=_UIColors.BG)
        self.container.pack(expand=True, fill="both")

        # =========================
        # Message
        # =========================

        if mode == self.MODE_WARNING:
            main_text = "あと5分で作業終了です"
            sub_text = "保存や中断準備をしてください"
        else:
            main_text = "作業終了です"
            sub_text = "PCを休止状態にして席を立ちましょう"

        self.title_label = tk.Label(
            self.container,
            text=main_text,
            font=(c.FONT_FAMILY, 22, "bold"),
            bg=_UIColors.BG,
            fg=_UIColors.BASE,
        )
        self.title_label.pack(pady=(120, 10))

        self.sub_label = tk.Label(
            self.container,
            text=sub_text,
            font=(c.FONT_FAMILY, 12),
            bg=_UIColors.BG,
            fg=_UIColors.TEXT_SUB,
        )
        self.sub_label.pack(pady=(0, 20))

        # =========================
        # Button (only warning mode)
        # =========================

        if mode == self.MODE_WARNING:
            self.ok_button = tk.Button(
                self.container,
                text="OK",
                bg=_UIColors.ACCENT,
                fg=_UIColors.TEXT_SUB_B,
                font=(c.FONT_FAMILY, 12, "bold"),
                relief="flat",
                padx=24,
                pady=10,
                command=self.destroy,
                activebackground=_UIColors.SELECT_BG,
            )
            self.ok_button.pack()

        # =========================
        # Block mode behavior
        # =========================

        if mode == self.MODE_BLOCK:
            self.overrideredirect(True)
            self.attributes("-topmost", True)

            # Esc無効化（逃げ防止）
            self.bind("<Escape>", lambda e: None)

        # warningは閉じられる
        if mode == self.MODE_WARNING:
            self.bind("<Escape>", lambda e: self.destroy())

    # =========================
    # setup
    # =========================

    def _setup_view(self) -> None:
        self.configure(bg=_UIColors.BG)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        self.update_idletasks()

        w = c.WINDOW_WIDTH
        h = c.WINDOW_HEIGHT

        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
