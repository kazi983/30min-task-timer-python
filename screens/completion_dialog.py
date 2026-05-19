"""完了ダイアログモジュール."""

import tkinter as tk


class CompletionDialog:
    """タスク完了確認ダイアログ。"""

    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent

    def show(self) -> None:
        dialog = tk.Toplevel(self.parent)
        dialog.title("完了")
        dialog.geometry("360x200")
        dialog.transient(self.parent)
        dialog.grab_set()
