"""タスク選択ダイアログモジュール."""

import tkinter as tk


class TaskSelectionDialog:
    """タスク選択用ダイアログを表示するクラス。"""

    def __init__(self, parent: tk.Tk) -> None:
        self.parent = parent

    def show(self) -> None:
        dialog = tk.Toplevel(self.parent)
        dialog.title("タスク選択")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
