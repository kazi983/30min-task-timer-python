"""
app/controllers/app_controller.py

Application controller module.

This module defines AppController, which is responsible for:
- Initializing core application services (TaskManager, TimerManager)
- Managing application windows (task picker / task management)
- Handling application lifecycle (restart, exit)
- Integrating system tray operations
"""

import os
import sys
import tkinter as tk
import tkinter.font as tkfont

from pathlib import Path

from app.models.task_service import TaskService
from app.models.timer_service import TimerService
from app.models.session_service import SessionService

from app.views.session_interrupt_overlay import SessionInterruptOverlay
from app.views.task_picker_view import TaskPickerView
from app.views.task_management_view import TaskManagementView

from app.controllers.task_picker_controller import TaskPickerController

from app.controllers.task_management_controller import TaskManagementController

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

        self.task_service = TaskService(Path(TASK_DATA_FILE))

        self.timer_service = TimerService(root)

        self.session_service = SessionService()

        self.interrupt_overlay = SessionInterruptOverlay(
            command=self.complete_work_session
        )

        self.task_picker_view = None
        self.task_management_view = None

        default_font = tkfont.nametofont("TkDefaultFont")

        default_font.configure(
            family=c.FONT_FAMILY,
            size=10,
        )

    def start(self) -> None:
        """
        Start the application by opening the initial window.
        """

        self.open_task_picker_view()

    def complete_work_session(self) -> None:

        self.interrupt_overlay.hide()

        self.task_service.record_session(self.session_service.finish())

        self.open_task_picker_view()

    def open_task_picker_view(self) -> None:
        """
        Open the task picker view.

        If an existing window is open, it will be destroyed and replaced.
        """

        if self.task_picker_view:
            self.task_picker_view.destroy()

        self.task_picker_view = TaskPickerView(
            root=self.root,
        )

        TaskPickerController(
            window=self.task_picker_view,
            task_service=self.task_service,
            timer_service=self.timer_service,
            session_service=self.session_service,
            reopen_callback=self.complete_work_session,
            open_task_management_callback=self.open_task_management_view,
            interrupt_overlay=self.interrupt_overlay,
        )

    def open_task_management_view(self) -> None:
        """
        Open the task management view.

        If an existing window is open, it will be destroyed and replaced.
        """

        if self.task_management_view:
            self.task_management_view.destroy()

        self.task_management_view = TaskManagementView(root=self.root)

        TaskManagementController(
            window=self.task_management_view,
            task_service=self.task_service,
            open_task_picker_callback=self.open_task_picker_view,
        )

    def restart_app(self) -> None:
        """
        Restart the application by re-executing the current Python process.
        """

        self.task_service.record_session(self.session_service.finish())

        python = sys.executable

        os.execl(python, python, *sys.argv)

    def exit_app(self) -> None:
        """
        Request application shutdown via Tkinter event loop.
        """

        self.task_service.record_session(self.session_service.finish())

        self.root.after(0, self._shutdown)

    def _shutdown(self) -> None:
        """
        Perform graceful application shutdown.

        Stops the Tkinter event loop and destroys root window.
        """

        self.task_service.record_session(self.session_service.finish())

        self.root.quit()

        self.root.destroy()
