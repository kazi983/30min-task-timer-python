from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Callable

from app.models.timer_service import TimerService


@dataclass
class LeaveSchedule:
    leave_time: datetime
    buffer_minutes: int

    @property
    def stop_work_time(self):
        return self.leave_time - timedelta(minutes=self.buffer_minutes)

    @property
    def warning_time(self):
        return self.stop_work_time - timedelta(minutes=5)
        # return self.stop_work_time - timedelta(minutes=1)  # #test


class LeaveScheduleService:
    def __init__(self, timer_service: TimerService):
        self.timer = timer_service
        self.schedule: Optional[LeaveSchedule] = None

        self._warning_callback: Optional[Callable[[], None]] = None
        self._stop_callback: Optional[Callable[[], None]] = None

        self._warning_timer_id: Optional[str] = None
        self._stop_timer_id: Optional[str] = None

    # -------------------------
    # public API
    # -------------------------

    def set_callbacks(
        self,
        on_warning: Callable[[], None],
        on_stop: Callable[[], None],
    ):
        self._warning_callback = on_warning
        self._stop_callback = on_stop

    def schedule_leave(
        self,
        leave_time: datetime,
        buffer_minutes: int,
    ):
        self.cancel()

        # buffer_minutes = 1  # #test

        self.schedule = LeaveSchedule(
            leave_time=leave_time,
            buffer_minutes=buffer_minutes,
        )

        now = datetime.now()

        warning_in = (self.schedule.warning_time - now).total_seconds()
        stop_in = (self.schedule.stop_work_time - now).total_seconds()

        # 過去時刻ガード
        if warning_in < 0:
            warning_in = 0
        if stop_in < 0:
            stop_in = 0

        # warning
        if self._warning_callback:
            self._warning_timer_id = self.timer.start(
                delay_seconds=warning_in,
                callback=self._warning_callback,
            )

        # stop work
        if self._stop_callback:
            self._stop_timer_id = self.timer.start(
                delay_seconds=stop_in,
                callback=self._stop_callback,
            )

    def cancel(self):
        if self._warning_timer_id:
            self.timer.cancel(self._warning_timer_id)
            self._warning_timer_id = None

        if self._stop_timer_id:
            self.timer.cancel(self._stop_timer_id)
            self._stop_timer_id = None

        self.schedule = None

    # -------------------------
    # debug / helper
    # -------------------------

    def get_status(self) -> Optional[LeaveSchedule]:
        return self.schedule
