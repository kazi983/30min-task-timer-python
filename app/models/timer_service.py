"""
app/models/timer_service.py
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Dict


class TimerService:
    """
    A simple timer utility wrapper for Tkinter's after() method.

    This class provides a centralized way to schedule delayed execution
    of callbacks using the Tkinter event loop.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._timers: Dict[str, str] = {}
        self._counter = 0

    # -------------------------
    # public API
    # -------------------------

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

    def start(
        self,
        delay_seconds: float,
        callback: Callable[[], None],
    ) -> str:
        """
        Start a cancellable timer.

        Returns:
            timer_id: str
        """
        timer_id = self._generate_id()

        ms = int(delay_seconds * 1000)

        after_id = self.root.after(ms, lambda: self._execute(timer_id, callback))

        self._timers[timer_id] = after_id

        return timer_id

    def cancel(self, timer_id: str) -> None:
        """
        Cancel a running timer.
        """
        after_id = self._timers.get(timer_id)

        if after_id is not None:
            try:
                self.root.after_cancel(after_id)
            except Exception:
                pass

            del self._timers[timer_id]

    def cancel_all(self) -> None:
        """
        Cancel all running timers.
        """
        for timer_id in list(self._timers.keys()):
            self.cancel(timer_id)

    # -------------------------
    # internal
    # -------------------------
    def _execute(self, timer_id: str, callback: Callable[[], None]) -> None:
        """
        Execute callback and cleanup timer registry
        """
        if timer_id in self._timers:
            del self._timers[timer_id]

        callback()

    def _generate_id(self) -> str:
        self._counter += 1
        return f"t_{self._counter}"
