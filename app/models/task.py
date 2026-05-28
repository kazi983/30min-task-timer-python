from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Task:
    name: str
    completed: bool = False
    priority: str = "なし"
    created: str = ""
    last_selected: bool = False
