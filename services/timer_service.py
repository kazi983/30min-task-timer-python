"""タイマー関連サービスモジュール."""

from typing import Callable, Optional


class TimerService:
    """タイマー処理を管理するサービスクラス。"""

    def __init__(self) -> None:
        self._timer_id: Optional[str] = None

    def start(self, callback: Callable[[], None], interval_ms: int) -> None:
        pass

    def stop(self) -> None:
        pass
