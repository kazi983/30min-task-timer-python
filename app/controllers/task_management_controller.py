"""
app/controllers/task_management_controller.py

task management controller module.

This controller connects TaskService (service layer) with
TaskManagementView (view), handling user interactions such as
adding, editing, completing, and deleting tasks.

It acts as a mediator between UI events and application business logic.
"""

from tkinter import messagebox

import app.config.constants as c
from app.views.task_management_view import TaskManagementView
from app.models.task_service import TaskService


class TaskManagementController:
    """
    Controller for task management UI.

    Responsibilities:
    - Handle user actions from TaskManagementView
    - Invoke TaskService service methods
    - Update UI state after data changes
    - Display confirmation and warning dialogs

    This class contains application flow logic but no data persistence logic.
    """

    def __init__(
        self,
        window: TaskManagementView,
        task_service: TaskService,
        open_task_picker_callback,
    ) -> None:

        self.window = window

        self.task_service = task_service

        self.open_task_picker_callback = open_task_picker_callback

        self.refresh_task_list()

        self.window.add_button.config(
            command=self.on_add_task,
        )

        self.window.complete_button.config(
            command=self.on_complete_task,
        )

        self.window.delete_button.config(
            command=self.on_delete_task,
        )

        self.window.edit_button.config(
            command=self.on_edit_task,
        )

        self.window.back_button.config(
            command=self.on_open_task_picker,
        )

    def refresh_task_list(self) -> None:
        """
        Refresh the task list displayed in the UI.

        Fetches incomplete tasks from TaskService and updates the view.
        """

        tasks = self.task_service.get_all_tasks()

        self.window.update_task_list(tasks)

    def on_open_task_picker(self) -> None:
        """
        Close current window and return to task picker screen.
        """

        self.window.destroy()

        self.open_task_picker_callback()

    def on_add_task(self) -> None:
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

        self.task_service.add_task(input_value["name"], input_value["priority"])

        self.refresh_task_list()

    def on_edit_task(self) -> None:
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
                message += f"\n  {selected_task.name} \
                    ➤ {input_value['name']}"
            if selected_task.priority != input_value["priority"]:
                message += f"\n  {selected_task.priority} \
                    ➤ {input_value['priority']}"

            if not messagebox.askokcancel(
                "タスク完了",
                message,
                parent=self.window,
            ):
                return

        self.task_service.edit_task(
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

        self.task_service.mark_task_as_complete(selected_task)

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

        self.task_service.mark_task_as_delete(selected_task)

        self.refresh_task_list()
