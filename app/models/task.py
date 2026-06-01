"""
app/models/task.py

Task domain model.

Represents a single task entity used across the application.
Provides serialization and deserialization helpers for JSON persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
import uuid


@dataclass
class Task:
    """
    Represents a task in the system.

    Attributes:
        name: Task title.
        completed: Whether the task is completed.
        priority: Priority level of the task.
        created: Creation timestamp (string format).
        last_selected: Whether this task was last selected in UI.
        deleted: Soft delete flag.
    """

    id: str
    name: str
    completed: bool = False
    priority: str = "なし"
    created: str = ""
    last_selected: bool = False
    deleted: bool = False

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """
        Create a Task instance from a dictionary.

        Args:
            data: Dictionary containing task data.

        Returns:
            Task instance.
        """
        return Task(
            id=data.get("id", str(uuid.uuid4())),
            name=data["text"],
            completed=data.get("completed", False),
            priority=data.get("priority", "なし"),
            created=data.get("created", ""),
            last_selected=data.get("last_selected", False),
            deleted=data.get("deleted", False),
        )

    def to_dict(self) -> dict:
        """
        Convert Task instance to dictionary format for JSON storage.

        Returns:
            Dictionary representation of the task.
        """
        return {
            "index": self.id,
            "text": self.name,
            "completed": self.completed,
            "priority": self.priority,
            "created": self.created,
            "last_selected": self.last_selected,
            "deleted": self.deleted,
        }
