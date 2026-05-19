"""メイン画面モジュール."""

import tkinter as tk


class MainScreen:
    """アプリのメイン画面を管理するクラス。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def show(self) -> None:
        self.root.deiconify()
