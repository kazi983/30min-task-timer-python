"""
app/controllers/task_selection_controller.py

Task selection controller module.

This controller manages the task selection UI flow, including:
- Displaying incomplete tasks
- Handling task selection and confirmation
- Snooze functionality (delayed reopening of selection window)
- Navigation to task management screen

It coordinates between TaskSelectionWindow, TaskManager, and TimerManager.
"""

from tkinter import messagebox

import app.config.constants as c
from app.views.task_selection_window import TaskSelectionWindow
from app.models.task_manager import TaskManager


class TaskSelectionController:
    """
    Controller for task selection screen.

    Responsibilities:
    - Manage task selection UI interactions
    - Handle user decisions (select, complete, snooze, navigate)
    - Coordinate TaskManager and TimerManager operations
    - Control navigation between application windows

    This class contains application flow logic and user interaction handling.
    """

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
        """
        Refresh the task list in the selection window.

        Loads incomplete tasks from TaskManager and updates the UI.
        """

        tasks = self.task_manager.get_incomplete_tasks()

        self.window.update_task_list(tasks)

    def on_open_task_manager_button(self) -> None:
        """
        Close selection window and open task manager window.
        """

        self.window.destroy()

        self.open_task_manager_callback()

    def on_snooze_click(self) -> None:
        """
        Temporarily close the window and reopen it after a delay.
        """

        self.window.destroy()

        self.timer_manager.set_timeout(
            c.TIME_MS_SNOOZE,
            self.reopen_callback,
        )

    def on_decide_click(self) -> None:
        """
        Confirm task selection and mark it as last selected.

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

        selected_task.last_selected = True

        self.window.destroy()

        self.timer_manager.set_timeout(
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

        self.task_manager.complete_task(selected_task)

        self.refresh_task_list()
