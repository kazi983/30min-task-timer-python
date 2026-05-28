from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Task:
    text: str
    completed: bool
    priority: str = "なし"
    created: str = ""
    last_selected: bool = False