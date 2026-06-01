"""
app/controllers/task_manager_controller.py

Task manager controller module.

This controller connects TaskManager (service layer) with
TaskManagerWindow (view), handling user interactions such as
adding, editing, completing, and deleting tasks.

It acts as a mediator between UI events and application business logic.
"""

from tkinter import messagebox

import app.config.constants as c
from app.views.task_manager_window import TaskManagerWindow
from app.models.task_manager import TaskManager


class TaskManagerController:
    """
    Controller for task management UI.

    Responsibilities:
    - Handle user actions from TaskManagerWindow
    - Invoke TaskManager service methods
    - Update UI state after data changes
    - Display confirmation and warning dialogs

    This class contains application flow logic but no data persistence logic.
    """

    def __init__(
        self,
        window: TaskManagerWindow,
        task_manager: TaskManager,
        open_task_selection_callback,
    ) -> None:

        self.window = window

        self.task_manager = task_manager

        self.open_task_selection_callback = open_task_selection_callback

        self.refresh_task_list()

        self.window.add_button.config(
            command=self.on_add_task_click,
        )

        self.window.edit_button.config(
            command=self.on_edit_task_click,
        )

        self.window.open_task_selection_button.config(
            command=self.on_open_task_selection_button,
        )

        self.window.set_complete_callback(self.on_complete_task)
        self.window.set_delete_callback(self.on_delete_task)

    def refresh_task_list(self) -> None:
        """
        Refresh the task list displayed in the UI.

        Fetches incomplete tasks from TaskManager and updates the view.
        """

        tasks = self.task_manager.get_incomplete_tasks()

        self.window.update_task_list(tasks)

    def on_open_task_selection_button(self) -> None:
        """
        Close current window and return to task selection screen.
        """

        self.window.destroy()

        self.open_task_selection_callback()

    def on_add_task_click(self) -> None:
        """
        Create a new task from user input and refresh the task list.

        Shows warning if input is invalid.
        """

        input_value = self.window.get_input_value()

        if not input_value:

            messagebox.showwarning(
                "未入力", "タスクを入力してください", parent=self.window
            )

            return

        self.task_manager.add_task(input_value["name"], input_value["priority"])

        self.refresh_task_list()

    def on_edit_task_click(self) -> None:
        """
        Edit selected task with new values from input fields.

        Prompts user for confirmation before applying changes.
        """

        selected_task = self.window.get_selected_task()
        input_value = self.window.get_input_value()

        if not selected_task or not input_value:
            return
        if (
            selected_task.priority != input_value["priority"]
        ) and selected_task.name != input_value["name"]:
            messagebox.showwarning(
                "変更なし", "変更内容を入力してください", parent=self.window
            )

        if selected_task:

            message = "更新しますか？"
            if selected_task.name != input_value["name"]:
                message += f"\n\t{selected_task.name}\t ➤ {input_value['name']}"
            if selected_task.priority != input_value["priority"]:
                message += f"\n\t{selected_task.priority}\t ➤ {input_value['priority']}"

            if not messagebox.askokcancel(
                "タスク完了",
                message,
                parent=self.window,
            ):
                return

        self.task_manager.edit_task(
            selected_task, input_value["name"], input_value["priority"]
        )

        self.refresh_task_list()

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

    def on_delete_task(self) -> None:
        """
        Mark the selected task as deleted after user confirmation.
        """

        selected_task = self.window.get_selected_task()

        if not selected_task:
            return

        if selected_task:

            if not messagebox.askokcancel(
                "タスク削除",
                f"{selected_task.name} を削除しますか？",
                parent=self.window,
            ):
                return

        self.task_manager.delete_task(selected_task)

        self.refresh_task_list()
