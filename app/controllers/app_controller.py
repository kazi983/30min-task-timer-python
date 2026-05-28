# app/controllers/app_controller.py

import tkinter as tk
import tkinter.font as tkfont

from pathlib import Path

from app.models.task_manager import (
    TaskManager,
)

from app.models.timer_manager import (
    TimerManager,
)

from app.views.task_select_window import (
    TaskSelectWindow,
)

from app.controllers.task_select_controller import (
    TaskSelectController,
)

from app.config.paths import (
    TASK_DATA_FILE,
)

import app.config.constants as c

class AppController:

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        self.root = root

        self.root.withdraw()

        self.task_manager = TaskManager(
            Path(TASK_DATA_FILE)
        )

        self.timer_manager = TimerManager(
            root,
        )

        default_font = tkfont.nametofont(
            "TkDefaultFont"
        )

        default_font.configure(
            family=c.FONT_FAMILY,
            size=10,
        )

    def start(self) -> None:

        self.open_task_select_window()

    def open_task_select_window(self) -> None:

        window = TaskSelectWindow(
            root=self.root,
        )

        TaskSelectController(
            window=window,
            task_manager=self.task_manager,
            timer_manager=self.timer_manager,
            reopen_callback=(
                self.open_task_select_window
            ),
        )



