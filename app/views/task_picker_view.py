"""
app/views/task_picker_view.py
"""

import tkinter as tk
from collections.abc import Callable

from app.models.task import Task
import app.config.constants as c


class _UIColors:
    # base
    BG = "#0b1326"
    CARD = "#ffffff"
    BORDER = "#5e85b1"

    BASE = "#dae2fd"

    TEXT_SUB = "#6b7280"
    TEXT_SUB_B = "#00285d"

    # accent
    ACCENT = "#4d8eff"  # modern blue
    ACCENT_DARK = "#2d3449"

    SELECT_BG = "#e0f2fe"


class TaskPickerView(tk.Toplevel):
    """
    A task picker view that displays a list of tasks and allows the user
    to select, complete, delete, or snooze tasks.

    This view uses a Treeview to present task information such as priority,
    name, and creation date. It supports keyboard and mouse interactions and
    delegates task actions (complete/delete) via callbacks provided by the
    controller.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)

        self.title("Quick Start")

        self._setup_view()

        self.on_complete_task: Callable | None = None

        self.tasks: list[Task] = []

        # =========================
        # Header
        # =========================

        self.title_label = tk.Label(
            self,
            text="今から何をやる？",
            font=(c.FONT_FAMILY, 20, "bold"),
            bg=_UIColors.BG,
            fg=_UIColors.BASE,
        )
        self.title_label.pack(pady=(50, 5))

        self.last_selected_label = tk.Label(
            self,
            text="",
            font=(c.FONT_FAMILY, 11),
            bg=_UIColors.BG,
            fg=_UIColors.TEXT_SUB,
        )
        self.last_selected_label.pack(pady=(0, 10))

        # =========================
        # Leave Schedule Input
        # =========================

        leave_frame = tk.Frame(self, bg=_UIColors.BG)
        leave_frame.pack(pady=(5, 10))

        self.leave_time_final = tk.Label(
            leave_frame,
            text="⏰",
            font=(c.FONT_FAMILY, 12),
            bg=_UIColors.BG,
            fg=_UIColors.TEXT_SUB,
        )
        self.leave_time_final.pack(side=tk.LEFT, padx=0)

        self.leave_time_entry = tk.Entry(
            leave_frame,
            font=(c.FONT_FAMILY, 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground=_UIColors.ACCENT_DARK,
            highlightcolor=_UIColors.ACCENT,
            bg="#31394d",
            fg="#fafafa",
            width=10,
        )
        self.leave_time_entry.insert(0, "23:30")
        self.leave_time_entry.pack(side=tk.LEFT, padx=6)

        self.leave_time = tk.Label(
            leave_frame,
            text="💨",
            font=(c.FONT_FAMILY, 12),
            bg=_UIColors.BG,
            fg=_UIColors.TEXT_SUB,
        )
        self.leave_time.pack(side=tk.LEFT, padx=0)

        self.buffer_var = tk.StringVar(value="15")
        self.buffer_menu = tk.OptionMenu(
            leave_frame,
            self.buffer_var,
            "5",
            "10",
            "15",
            "20",
            "25",
            "30",
        )
        self.buffer_menu.config(
            bg=_UIColors.ACCENT_DARK,
            fg=_UIColors.BASE,
            relief="flat",
            highlightthickness=0,
            font=(c.FONT_FAMILY, 10),
        )
        self.buffer_menu.pack(side=tk.LEFT)

        # =========================
        # Input
        # =========================

        input_frame = tk.Frame(self, bg=_UIColors.BG)
        input_frame.pack(pady=10)

        self.task_input = tk.Entry(
            input_frame,
            font=(c.FONT_FAMILY, 12),
            relief="flat",
            highlightthickness=1,
            highlightbackground=_UIColors.ACCENT_DARK,
            highlightcolor=_UIColors.ACCENT,
            bg="#31394d",
            fg="#fafafa",
            width=35,
        )
        self.task_input.pack(side=tk.LEFT, padx=6, ipady=6)

        self.add_button = tk.Button(
            input_frame,
            text="+ 追加",
            bg=_UIColors.ACCENT,
            fg=_UIColors.TEXT_SUB_B,
            relief="flat",
            activebackground=_UIColors.SELECT_BG,
            padx=12,
            pady=6,
        )
        self.add_button.pack(side=tk.LEFT)

        # =========================
        # Listbox
        # =========================

        list_frame = tk.Frame(self, bg=_UIColors.BG)
        list_frame.pack(pady=15)

        self.task_listbox = tk.Listbox(
            list_frame,
            font=(c.FONT_FAMILY, 12),
            activestyle="none",
            width=45,
            height=15,
            bg="#131b2e",
            fg=_UIColors.BASE,
            relief="flat",
            highlightthickness=0,
            highlightbackground="#adc6ff",
            selectbackground="#adc6ff",
            selectforeground="black",
            selectborderwidth=0,
        )
        self.task_listbox.pack()

        # =========================
        # Buttons
        # =========================

        bottom_frame = tk.Frame(self, bg=_UIColors.BG)
        bottom_frame.pack(pady=18)

        # primary
        self.start_button = tk.Button(
            bottom_frame,
            text="▶ はじめる",
            bg=_UIColors.ACCENT,
            fg=_UIColors.TEXT_SUB_B,
            font=(c.FONT_FAMILY, 11, "bold"),
            relief="flat",
            padx=18,
            pady=10,
            activebackground=_UIColors.SELECT_BG,
        )
        self.start_button.pack(pady=(0, 10))

        # secondary row
        sub_frame = tk.Frame(bottom_frame, bg=_UIColors.BG)
        sub_frame.pack()

        self.snooze_button = self._secondary_button(sub_frame, "あとで")
        self.snooze_button.pack(side=tk.LEFT, padx=8)

        self.management_button = self._secondary_button(sub_frame, "編集")
        self.management_button.pack(side=tk.LEFT, padx=8)

        # =========================
        # bindings
        # =========================

        self.bind("<Escape>", lambda e: self.snooze_button.invoke())

        self.task_input.bind(
            "<Return>",
            lambda e: self.add_button.invoke(),
        )

        self.task_listbox.bind(
            "<Return>",
            lambda e: self.start_button.invoke(),
        )

        self.task_listbox.bind(
            "<BackSpace>",
            lambda e: self.on_complete_task,
        )

        self.task_listbox.bind(
            "<Double-1>",
            lambda e: self.start_button.invoke(),
        )

    # =========================
    # API
    # =========================

    def update_task_list(self, tasks: list[Task]) -> None:
        """
        Refresh the task list displayed in the Treeview.

        Args:
            tasks: A list of Task objects to display.
        """

        self.tasks = tasks

        self.task_listbox.delete(0, tk.END)

        selected_index = 0
        last_task_name = ""

        for i, task in enumerate(tasks):

            prefix = ""
            if task.priority == "NOW":
                prefix = " 🔥 "
            elif task.priority == "SOONER":
                prefix = " ⭐ "
            elif task.priority == "ANYTIME":
                prefix = " 📝 "

            self.task_listbox.insert(
                tk.END,
                f"{prefix}{task.name}",
            )

            if task.last_selected:
                selected_index = i
                last_task_name = task.name

        if tasks:
            self.task_listbox.selection_set(selected_index)
            self.task_listbox.activate(selected_index)
            self.task_listbox.see(selected_index)

        if last_task_name:
            self.last_selected_label.config(text=f"前回の続き: {last_task_name}")

        self.task_input.focus_set()

    def select_task_by_index(self, index: int) -> None:
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(index)
        self.task_listbox.activate(index)
        self.task_listbox.see(index)

    def get_selected_task(self) -> Task | None:
        """
        Return the currently selected task in the Treeview.

        Returns:
            The selected Task object, or None if nothing is selected.
        """

        selection = self.task_listbox.curselection()
        if not selection:
            return None
        return self.tasks[selection[0]]

    def set_complete_callback(self, callback: Callable):
        self.on_complete_task = callback

    def get_leave_schedule_input(self):
        return {
            "leave_time": self._normalize_time_input(self.leave_time_entry.get()),
            "buffer_minutes": int(self.buffer_var.get()),
        }

    def _setup_view(self) -> None:

        self.configure(bg=_UIColors.BG)

        self.overrideredirect(True)  # #test

        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        self.update_idletasks()

        w = c.WINDOW_WIDTH
        h = c.WINDOW_HEIGHT

        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")

    def _secondary_button(self, parent, text):
        return tk.Button(
            parent,
            text=text,
            bg=_UIColors.ACCENT_DARK,
            fg=_UIColors.BASE,
            relief="flat",
            font=(c.FONT_FAMILY, 10),
            padx=16,
            pady=8,
            width=8,  # ← 幅固定
            activebackground=_UIColors.SELECT_BG,
        )

    def _normalize_time_input(self, value: str) -> str:
        """
        Accepts:
            "400" -> "04:00"
            "930" -> "09:30"
            "1830" -> "18:30"
            "04:00" -> "04:00"
        """

        value = value.strip()

        # already formatted
        if ":" in value:
            h, m = value.split(":")
            return f"{int(h):02d}:{int(m):02d}"

        # numeric only
        if not value.isdigit():
            raise ValueError("Invalid time format")

        if len(value) <= 2:
            # "9" -> "09:00"
            hour = int(value)
            return f"{hour:02d}:00"

        if len(value) == 3:
            # "930" -> 9:30
            hour = int(value[0])
            minute = int(value[1:])
            return f"{hour:02d}:{minute:02d}"

        if len(value) == 4:
            # "1830" -> 18:30
            hour = int(value[:2])
            minute = int(value[2:])
            return f"{hour:02d}:{minute:02d}"

        raise ValueError("Invalid time format length")
