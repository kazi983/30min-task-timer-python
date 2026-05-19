"""システムトレイ管理モジュール."""

import tkinter as tk


class TraySystem:
    """アプリケーショントレイの振る舞いを管理するクラス。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def minimize_to_tray(self) -> None:
        self.root.withdraw()
