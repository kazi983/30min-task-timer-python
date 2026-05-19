"""タスクモデルモジュール."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: str
    title: str
    priority: str
    completed: bool = False
    created: datetime = datetime.now()
    updated: datetime = datetime.now()
