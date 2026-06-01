# app/controllers/task_selection_controller.py

from tkinter import messagebox

import app.config.constants as c
from app.views.task_selection_window import TaskSelectionWindow
from app.models.task_manager import TaskManager


class TaskSelectionController:

    def __init__(
        self,
        window: TaskSelectionWindow,
        task_manager: TaskManager,
        timer_manager,
        reopen_callback,
        open_task_manager_callback,
    ) -> None:

        self.window = window

        self.task_manager = task_manager

        self.timer_manager = timer_manager

        self.reopen_callback = reopen_callback
        self.open_task_manager_callback = open_task_manager_callback

        self.refresh_task_list()

        self.window.open_task_manager_button.config(
            command=self.on_open_task_manager_button,
        )

        self.window.snooze_button.config(
            command=self.on_snooze_click,
        )

        self.window.decide_button.config(
            command=self.on_decide_click,
        )

        self.window.set_complete_callback(self.on_complete_task)

    def refresh_task_list(self) -> None:

        tasks = self.task_manager.get_incomplete_tasks()

        self.window.update_task_list(tasks)

    def on_open_task_manager_button(self) -> None:

        self.window.destroy()

        self.open_task_manager_callback()

    def on_snooze_click(self) -> None:

        self.window.destroy()

        self.timer_manager.set_timeout(
            c.TIME_MS_SNOOZE,
            self.reopen_callback,
        )

    def on_decide_click(self) -> None:

        selected_task = self.window.get_selected_task()

        if not selected_task:

            messagebox.showwarning(
                "未選択", "タスクを選択してください", parent=self.window
            )

            return

        if selected_task:

            if not messagebox.askokcancel(
                "選択完了", f"{selected_task.name} を開始しますか？", parent=self.window
            ):
                return

        selected_task.last_selected = True

        self.window.destroy()

        self.timer_manager.set_timeout(
            c.TIME_MS_INTERVAL,
            self.reopen_callback,
        )

    def on_complete_task(self) -> None:
        selected_task = self.window.get_selected_task()

        if not selected_task:
            return

        if selected_task:

            if not messagebox.askokcancel(
                "タスク完了",
                f"{selected_task.name} を完了済みタスクに登録しますか？",
                parent=self.window,
            ):
                return

        self.task_manager.complete_task(selected_task)

        self.refresh_task_list()
