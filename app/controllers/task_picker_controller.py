"""
app/controllers/task_picker_controller.py

Task picker controller module.

This controller manages the task picker UI flow, including:
- Displaying incomplete tasks
- Handling task picker and confirmation
- Snooze functionality (delayed reopening of picker window)
- Navigation to task management screen

It coordinates between TaskPickerView, TaskService, and TimerService.
"""

from tkinter import messagebox
from datetime import datetime

import app.config.constants as c
from app.models.session_service import SessionService
from app.views.task_picker_view import TaskPickerView
from app.models.task_service import TaskService
from app.models.timer_service import TimerService
from app.models.leave_schedule_service import LeaveScheduleService


class TaskPickerController:
    """
    Controller for task picker screen.

    Responsibilities:
    - Manage task picker UI interactions
    - Handle user decisions (select, complete, snooze, navigate)
    - Coordinate TaskService and TimerService operations
    - Control navigation between application windows

    This class contains application flow logic and user interaction handling.
    """

    def __init__(
        self,
        window: TaskPickerView,
        task_service: TaskService,
        timer_service: TimerService,
        session_service: SessionService,
        reopen_callback,
        open_task_management_callback,
        interrupt_overlay,
    ) -> None:

        self.window = window
        self.task_service = task_service
        self.timer_service = timer_service
        self.session_service = session_service
        self.leave_service = LeaveScheduleService(self.timer_service)
        self.leave_service.set_callbacks(
            on_warning=self.on_leave_warning,
            on_stop=self.on_leave_stop,
        )
        self.reopen_callback = reopen_callback
        self.open_task_management_callback = open_task_management_callback
        self.interrupt_overlay = interrupt_overlay
        self._current_task_id = None
        self._started_at = None
        self._leave_blocked = False

        self.refresh_task_list()

        # buttons
        self.window.add_button.config(command=self.on_add_task)
        self.window.start_button.config(command=self.on_start_session)
        self.window.snooze_button.config(command=self.on_snooze)
        self.window.management_button.config(command=self.on_open_management)

        # optional callbacks
        self.window.set_complete_callback(self.on_complete_task)

    # =========================
    # data
    # =========================

    def refresh_task_list(self):
        tasks = self.task_service.get_incomplete_tasks()
        self.window.update_task_list(tasks)

    # =========================
    # actions
    # =========================

    def on_add_task(self):
        name = self.window.task_input.get().strip()

        if not name:
            return

        new_task = self.task_service.add_task(
            text=name,
            priority="NOW",
        )

        self.window.task_input.delete(0, "end")

        tasks = self.task_service.get_incomplete_tasks()
        self.refresh_task_list()

        for i, task in enumerate(tasks):
            if task.id == new_task.id:
                self.window.select_task_by_index(i)
                break

    def on_start_session(self):
        task = self.window.get_selected_task()

        if not task:
            messagebox.showwarning(
                "未選択",
                "タスクを選んでください",
                parent=self.window,
            )
            return

        if not messagebox.askokcancel(
            "開始",
            f"{task.name} を開始しますか？",
            parent=self.window,
        ):
            return

        # =========================
        # Leave schedule start
        # =========================

        leave_input = self.window.get_leave_schedule_input()

        # #fix 日付け跨ぎ未対応
        leave_time = datetime.strptime(
            leave_input["leave_time"],
            "%H:%M",
        )

        # 今日の日付に補正
        now = datetime.now()
        leave_time = leave_time.replace(
            year=now.year,
            month=now.month,
            day=now.day,
        )

        self.leave_service.schedule_leave(
            leave_time=leave_time,
            buffer_minutes=leave_input["buffer_minutes"],
        )

        # =========================
        # session start
        # =========================

        self.task_service.mark_task_as_last_selected(task)

        self.window.destroy()

        self.session_service.start(task.id)

        self.interrupt_overlay.show()

        self.timer_service.schedule(
            c.TIME_MS_INTERVAL,
            self.safe_reopen,
        )

    def safe_reopen(self):
        if self._leave_blocked:
            return

        self.reopen_callback()

    def on_snooze(self):
        self.window.destroy()

        self.timer_service.schedule(
            c.TIME_MS_SNOOZE,
            self.reopen_callback,
        )

    def on_open_management(self):
        self.window.destroy()
        self.open_task_management_callback()

    def on_complete_task(self):
        task = self.window.get_selected_task()

        if not task:
            return

        if not messagebox.askokcancel(
            "完了",
            f"{task.name} を完了にしますか？",
            parent=self.window,
        ):
            return

        self.task_service.mark_task_as_complete(task)
        self.refresh_task_list()

    def on_leave_warning(self):
        from app.views.leave_schedule_view import LeaveScheduleView

        self._leave_blocked = True

        self.window.destroy()

        LeaveScheduleView(self.timer_service.root, mode="warning")

    def on_leave_stop(self):
        from app.views.leave_schedule_view import LeaveScheduleView

        self.interrupt_overlay.hide()

        self.task_service.record_session(self.session_service.finish())

        self.timer_service.cancel_all()

        self._leave_blocked = True

        self.window.destroy()

        LeaveScheduleView(self.timer_service.root, mode="block")
