"""ウィンドウ関連サービスモジュール."""

import tkinter as tk


class WindowService:
    """ウィンドウ表示やフォーカス移動を扱うサービスクラス。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def bring_to_front(self) -> None:
        self.root.lift()

    def hide(self) -> None:
        self.root.withdraw()
