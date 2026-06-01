from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Task:
    name: str
    completed: bool = False
    priority: str = "なし"
    created: str = ""
    last_selected: bool = False
    deleted: bool = False

    @staticmethod
    def from_dict(data: dict) -> "Task":
        return Task(
            name=data["text"],
            completed=data.get("completed", False),
            priority=data.get("priority", "なし"),
            created=data.get("created", ""),
            last_selected=data.get("last_selected", False),
            deleted=data.get("deleted", False),
        )

    def to_dict(self) -> dict:
        return {
            "text": self.name,
            "completed": self.completed,
            "priority": self.priority,
            "created": self.created,
            "last_selected": self.last_selected,
            "deleted": self.deleted,
        }
