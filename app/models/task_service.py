"""
app/models/task_service.py

Task management service layer.

This module provides TaskService, which is responsible for:
- Creating, editing, completing, and deleting tasks
- Persisting tasks to a JSON file
- Loading tasks from persistent storage

The class acts as a simple domain/service layer
between the UI and data storage.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from app.models.session_service import SessionResult
from app.models.task import Task
import uuid


class TaskService:
    """
    Manages application tasks and handles persistence to a JSON file.

    Responsibilities:
    - Maintain an in-memory list of Task objects
    - Provide CRUD operations for tasks
    - Save and load tasks from disk

    This class acts as a lightweight service layer
    and does not handle UI logic.
    """

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.tasks: list[Task] = []
        self.load_tasks()

    def add_task(self, text: str, priority: str) -> Task:
        """
        Create a new task and persist it.

        Args:
            text: Task name.
            priority: Priority level of the task.

        Returns:
            The created Task object.

        Raises:
            ValueError: If task name is empty.
        """

        if not text:
            raise ValueError("タスク名が空です")

        task = Task(
            id=str(uuid.uuid4()),
            name=text,
            priority=priority,
            created_at=datetime.now(timezone.utc),
        )

        self.tasks.append(task)
        self.save_tasks()

        return task

    def edit_task(self, task: Task, name: str, priority: str) -> None:
        """
        Update an existing task's name and priority.

        Args:
            task: Task to update.
            name: New task name.
            priority: New priority level.
        """

        task.name = name
        task.priority = priority

        self.save_tasks()

    def mark_task_as_complete(self, task: Task) -> None:
        """
        Mark a task as completed.

        Args:
            task: Task to mark as completed.
        """
        task.completed = True

        self.save_tasks()

    def mark_task_as_delete(self, task: Task) -> None:
        """
        Mark a task as deleted (soft delete).

        Args:
            task: Task to delete.
        """

        task.deleted = True

        self.save_tasks()

    def mark_task_as_last_selected(self, task: Task) -> None:
        """
        Mark a task as last selected.

        Args:
            task: Task to mark as last selected.
        """
        for t in self.tasks:
            t.last_selected = False

        task.last_selected = True

        self.save_tasks()

    def record_session(self, session_result: SessionResult) -> None:

        for t in self.tasks:
            if t.id == session_result.task_id:
                t.completed_sessions += 1
                t.total_minutes += session_result.elapsed_minutes

        self.save_tasks()

    def save_tasks(self) -> None:
        """
        Save all tasks to the JSON file.

        Raises:
            IOError: If writing to file fails.
        """

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(
                    [task.to_dict() for task in self.tasks],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except IOError as error:

            raise IOError(f"タスクの保存に失敗: {error}") from error

    def get_all_tasks(self) -> list[Task]:
        """
        Get all tasks.

        Returns:
            A list of Task objects.
        """

        self.load_tasks()

        return [task for task in self.tasks]

    def get_incomplete_tasks(self) -> list[Task]:
        """
        Get all tasks that are not completed.

        Returns:
            A list of Task objects where completed is False.
        """

        self.load_tasks()

        return [task for task in self.tasks if not task.completed]

    def get_last_selected_tasks(self) -> list[Task]:
        """
        Get tasks that were last selected by the user.

        Returns:
            A list of Task objects marked as last_selected.
        """

        self.load_tasks()

        return [task for task in self.tasks if task.last_selected]

    def load_tasks(self) -> None:
        """
        Load tasks from the JSON file into memory.

        Invalid or deleted tasks are filtered out.

        Raises:
            RuntimeError: If file reading or JSON parsing fails.
        """

        if not self.data_file.exists():
            self.tasks = []
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                json_tasks = json.load(file)

            self.tasks = [
                Task.from_dict(task_data)
                for task_data in json_tasks
                if not task_data.get("deleted", False)
            ]

        except (json.JSONDecodeError, IOError) as error:
            raise RuntimeError(f"読み込みエラー: {error}") from error
