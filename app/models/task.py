"""
app/models/task.py

Task domain model.

Represents a single task entity used across the application.
Provides serialization and deserialization helpers for JSON persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dataclasses import field

LOCAL_TZ = ZoneInfo("America/Vancouver")


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
    memo: str = ""
    completed: bool = False
    priority: str = "なし"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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

        created_at_str = data.get("created_at", datetime.now(timezone.utc))
        created_at = (
            datetime.fromisoformat(created_at_str)
            if created_at_str
            else datetime.now(timezone.utc)
        )

        return Task(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            memo=data.get("memo", ""),
            completed=data.get("completed", False),
            priority=data.get("priority", ""),
            created_at=created_at,
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
            "id": self.id,
            "name": self.name,
            "memo": self.memo,
            "completed": self.completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "last_selected": self.last_selected,
            "deleted": self.deleted,
        }

    def created_local(self) -> str:
        return self.created_at.astimezone(LOCAL_TZ).strftime("%Y-%m-%d")
