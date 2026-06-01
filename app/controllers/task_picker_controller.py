"""
app/controllers/task_picker_controller.py

Task picker controller module.

This controller manages the task picker UI flow, including:
- Displaying incomplete tasks
- Handling task picker and confirmation
- Snooze functionality (delayed reopening of picker window)
- Navigation to task management screen

It coordinates between TaskPickerView, TaskService, and TimerService.
"""

from tkinter import messagebox

import app.config.constants as c
from app.views.task_picker_view import TaskPickerView
from app.models.task_service import TaskService


class TaskPickerController:
    """
    Controller for task picker screen.

    Responsibilities:
    - Manage task picker UI interactions
    - Handle user decisions (select, complete, snooze, navigate)
    - Coordinate TaskService and TimerService operations
    - Control navigation between application windows

    This class contains application flow logic and user interaction handling.
    """

    def __init__(
        self,
        window: TaskPickerView,
        task_service: TaskService,
        timer_service,
        reopen_callback,
        open_task_management_callback,
    ) -> None:

        self.window = window

        self.task_service = task_service

        self.timer_service = timer_service

        self.reopen_callback = reopen_callback
        self.open_task_management_callback = open_task_management_callback

        self.refresh_task_list()

        self.window.task_management_button.config(
            command=self.on_open_task_management_button,
        )

        self.window.snooze_button.config(
            command=self.on_snooze_click,
        )

        self.window.confirm_button.config(
            command=self.on_confirm_click,
        )

        self.window.set_complete_callback(self.on_complete_task)

    def refresh_task_list(self) -> None:
        """
        Refresh the task list in the picker view.

        Loads incomplete tasks from TaskService and updates the UI.
        """

        tasks = self.task_service.get_incomplete_tasks()

        self.window.update_task_list(tasks)

    def on_open_task_management_button(self) -> None:
        """
        Close picker window and open task management view.
        """

        self.window.destroy()

        self.open_task_management_callback()

    def on_snooze_click(self) -> None:
        """
        Temporarily close the window and reopen it after a delay.
        """

        self.window.destroy()

        self.timer_service.schedule(
            c.TIME_MS_SNOOZE,
            self.reopen_callback,
        )

    def on_confirm_click(self) -> None:
        """
        Confirm task picker and mark it as last selected.

        If confirmed, the window is closed and will reopen after a delay.
        """

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

        self.task_service.mark_task_as_last_selected(selected_task)

        self.window.destroy()

        self.timer_service.schedule(
            c.TIME_MS_INTERVAL,
            self.reopen_callback,
        )

    def on_complete_task(self) -> None:
        """
        Mark the selected task as completed after user confirmation.
        """

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

        self.task_service.mark_task_as_complete(selected_task)

        self.refresh_task_list()
