# app/controllers/task_select_controller.py

from tkinter import messagebox

from app.views.task_select_window import (
    TaskSelectWindow,
)

from app.models.task_manager import (
    TaskManager,
)

import os

class TaskSelectController:

    SNOOZE_MS = 5 * 60 * 1000
    INTERVAL_MS = 5000 if os.getenv("TASK_MODE", "production") == "test" else 30 * 60 * 1000

    def __init__(
        self,
        window: TaskSelectWindow,
        task_manager: TaskManager,
        timer_manager,
        reopen_callback,
    ) -> None:

        self.window = window

        self.task_manager = task_manager

        self.timer_manager = timer_manager

        self.reopen_callback = reopen_callback

        self.refresh_task_list()

        self.window.snooze_button.config(
            command=self.on_snooze_click,
        )

        self.window.decide_button.config(
            command=self.on_decide_click,
        )

    def refresh_task_list(self) -> None:

        tasks = (
            self.task_manager
            .get_incomplete_tasks()
        )

        self.window.update_task_list(tasks)

    def on_snooze_click(self) -> None:

        self.window.destroy()

        self.timer_manager.set_timeout(
            self.SNOOZE_MS,
            self.reopen_callback,
        )

    def on_decide_click(self) -> None:

        selected_task = (
            self.window.get_selected_task()
        )

        if not selected_task:

            messagebox.showwarning(
                "未選択",
                "タスクを選択してください",
                parent=self.window
            )

            return

        if selected_task:

            if not messagebox.askokcancel(
                "選択完了",
                f"{selected_task.text} を開始しますか？",
                parent=self.window
            ):
                return

        selected_task.last_selected = True

        self.window.destroy()

        self.timer_manager.set_timeout(
            self.INTERVAL_MS,
            self.reopen_callback,
        )