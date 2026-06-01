"""
app/models/timer_manager.py
"""
from __future__ import annotations

import tkinter as tk
from collections.abc import Callable


class TimerManager:
    """
    A simple timer utility wrapper for Tkinter's after() method.

    This class provides a centralized way to schedule delayed execution
    of callbacks using the Tkinter event loop.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def schedule(
        self,
        milliseconds: int,
        callback: Callable[[], None],
    ) -> None:
        """
        Schedule a callback to be executed after a specified delay.

        Args:
            milliseconds: Delay in milliseconds before execution.
            callback: Function to execute after the delay.
        """

        self.root.after(milliseconds, callback)
