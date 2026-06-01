"""
app/controllers/app_controller.py

Application controller module.

This module defines AppController, which is responsible for:
- Initializing core application services (TaskManager, TimerManager)
- Managing application windows (task selection / task manager)
- Handling application lifecycle (restart, exit)
- Integrating system tray operations
"""

import os
import sys
import tkinter as tk
import tkinter.font as tkfont

from pathlib import Path

from app.models.task_manager import TaskManager

from app.models.timer_manager import TimerManager

from app.views.task_selection_window import TaskSelectionWindow
from app.views.task_manager_window import TaskManagerWindow

from app.controllers.task_selection_controller import TaskSelectionController

from app.controllers.task_manager_controller import TaskManagerController

from app.config.paths import TASK_DATA_FILE

from app.infrastructure.tray_manager import TrayManager

import app.config.constants as c


class AppController:
    """
    Central application controller.

    Responsibilities:
    - Manage application state and core services
    - Control window lifecycle (open/close/switch views)
    - Coordinate between UI (views), controllers, and services
    - Handle application restart and shutdown logic

    This class acts as the entry point and orchestrator of the application.
    """

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        self.root = root

        self.root.withdraw()

        self.tray_manager = TrayManager(
            on_restart=self.restart_app, on_exit=self.exit_app
        )

        self.tray_manager.run()

        self.task_manager = TaskManager(Path(TASK_DATA_FILE))

        self.timer_manager = TimerManager(
            root,
        )

        self.task_selection_window = None
        self.task_manager_window = None

        default_font = tkfont.nametofont("TkDefaultFont")

        default_font.configure(
            family=c.FONT_FAMILY,
            size=10,
        )

    def start(self) -> None:
        """
        Start the application by opening the initial window.
        """

        self.open_task_selection_window()

    def open_task_selection_window(self) -> None:
        """
        Open the task selection window.

        If an existing window is open, it will be destroyed and replaced.
        """

        if self.task_selection_window:
            self.task_selection_window.destroy()

        self.task_selection_window = TaskSelectionWindow(
            root=self.root,
        )

        TaskSelectionController(
            window=self.task_selection_window,
            task_manager=self.task_manager,
            timer_manager=self.timer_manager,
            reopen_callback=self.open_task_selection_window,
            open_task_manager_callback=self.open_task_manager_window,
        )

    def open_task_manager_window(self) -> None:
        """
        Open the task manager window.

        If an existing window is open, it will be destroyed and replaced.
        """

        if self.task_manager_window:
            self.task_manager_window.destroy()

        self.task_manager_window = TaskManagerWindow(
            root=self.root,
        )

        TaskManagerController(
            window=self.task_manager_window,
            task_manager=self.task_manager,
            open_task_selection_callback=self.open_task_selection_window,
        )

    def restart_app(self) -> None:
        """
        Restart the application by re-executing the current Python process.
        """

        python = sys.executable

        os.execl(python, python, *sys.argv)

    def exit_app(self) -> None:
        """
        Request application shutdown via Tkinter event loop.
        """

        self.root.after(0, self._shutdown)

    def _shutdown(self) -> None:
        """
        Perform graceful application shutdown.

        Stops the Tkinter event loop and destroys root window.
        """

        self.root.quit()

        self.root.destroy()
