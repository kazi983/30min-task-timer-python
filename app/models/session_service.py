from dataclasses import dataclass
from datetime import datetime


@dataclass
class SessionResult:
    task_id: str
    elapsed_minutes: int


class SessionService:
    def __init__(self):
        self._task_id: str = None
        self._started_at: datetime = None

    def start(self, task_id: str):
        self._task_id = task_id
        self._started_at = datetime.now()
        print("sessionservice start1", self)
        print("sessionservice start2", self._task_id)
        print("sessionservice start3", self._started_at)

    def finish(self) -> SessionResult:
        if self._task_id is None:
            return

        elapsed = datetime.now() - self._started_at
        print(elapsed)

        return SessionResult(
            task_id=self._task_id, elapsed_minutes=int(elapsed.total_seconds() / 60)
        )
