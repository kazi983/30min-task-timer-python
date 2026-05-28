from __future__ import annotations

from pathlib import Path
from datetime import datetime
import json

from app.models.task import Task


class TaskManager:

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.tasks: list[Task] = []
        self.load_tasks()

    def add_task(self, text: str, priority: str) -> dict:
        if not text:
            raise ValueError("タスク名が空です")

        task = Task(
            name=text,
            priority=priority,
            created=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        self.tasks.append(task)
        self.save_tasks()

        return task

    def complete_task(self, task: Task) -> None:

        task.completed = True

        self.save_tasks()

    def delete_task(self, task: Task) -> None:

        self.tasks.remove(task)

        self.save_tasks()

    def get_incomplete_tasks(self) -> list[Task]:
        return [task for task in self.tasks if not task.completed]

    def get_last_selected_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.last_selected]

    def save_tasks(self) -> None:
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except IOError as error:

            raise IOError(f"タスクの保存に失敗: {error}") from error

    def load_tasks(self) -> None:
        if not self.data_file.exists():
            self.tasks = []
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                json_tasks = json.load(file)

            self.tasks = []

            for task_date in json_tasks:

                task = Task(
                    name=task_date["text"],
                    completed=task_date.get("completed", "なし"),
                    priority=task_date.get("priority", "なし"),
                    created=task_date.get("created", ""),
                    last_selected=task_date.get("last_selected", False),
                )

                self.tasks.append(task)

        except (json.JSONDecodeError, IOError) as error:
            raise RuntimeError(f"読み込みエラー: {error}")
