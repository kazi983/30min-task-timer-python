"""タスク関連サービスモジュール."""

from pathlib import Path
from typing import List, Dict


class TaskService:
    """タスク操作を提供するサービスクラス。"""

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file
        self.tasks: List[Dict] = []

    def load_tasks(self) -> None:
        pass

    def save_tasks(self) -> None:
        pass
