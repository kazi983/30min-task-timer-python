"""タスクリポジトリモジュール."""

from pathlib import Path
from typing import List, Dict


class TaskRepository:
    """タスクデータの読み書きを担当するリポジトリ。"""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path

    def load(self) -> List[Dict]:
        return []

    def save(self, tasks: List[Dict]) -> None:
        pass
