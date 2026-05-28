import tkinter as tk
from collections.abc import Callable


class TimerManager:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def set_timeout(
        self,
        milliseconds: int,
        callback: Callable[[], None],
    ) -> None:

        self.root.after(milliseconds, callback)