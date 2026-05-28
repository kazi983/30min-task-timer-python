# app/views/task_select_window.py

import tkinter as tk
from tkinter import ttk

from app.models.task import Task
import app.config.constants as c


class TaskSelectWindow(tk.Toplevel):

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        super().__init__(root)

        self.attributes("-topmost", True)

        self.lift()

        self.focus_force()

        self.title("タスク選択")

        self.geometry("500x600")

        title_label = ttk.Label(
            self,
            text="次のタスクを選択してください",
        )
        title_label.pack(pady=10)

        # ========================
        # Treeview
        # ========================

        columns = ("priority", "text", "created")

        self.task_tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=10,
        )

        self.task_tree.heading(
            "priority",
            text="優先度",
        )

        self.task_tree.heading("text", text="タスク")

        self.task_tree.heading(
            "created",
            text="作成日時",
        )

        self.task_tree.column(
            "priority",
            width=80,
            anchor=tk.CENTER,
        )

        self.task_tree.column(
            "text",
            width=400,
        )

        self.task_tree.column(
            "created",
            width=180,
        )

        self.task_tree.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=10,
        )

        # ========================
        # scrollbar
        # ========================

        scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.task_tree.yview,
        )

        self.task_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        # ========================
        # buttons
        # ========================

        button_frame = ttk.Frame(self)

        button_frame.pack(pady=10)

        self.snooze_button = ttk.Button(
            button_frame,
            text="5分後再通知",
        )

        self.snooze_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        self.decide_button = ttk.Button(
            button_frame,
            text="決定",
        )

        self.decide_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        # ========================
        # bind
        # ========================
        self.task_tree.bind("<Return>", self._on_enter)
        self.snooze_button.bind("<Return>", self._on_enter)
        self.decide_button.bind("<Return>", self._on_enter)

        self.bind("<Escape>", self._on_escape)

        self.task_tree.bind("<Double-1>", self._on_double_click)

        self.display_tasks: list[Task] = []

    def update_task_list(
        self,
        tasks: list[Task],
    ) -> None:

        for item_id in self.task_tree.get_children():
            self.task_tree.delete(item_id)

        self.display_tasks = tasks

        for priority, color in c.PRIORITY_COLORS.items():

            self.task_tree.tag_configure(
                priority,
                background=color,
            )

        selected_item_id = None
        for index, task in enumerate(tasks):
            iid_str = str(index)

            self.task_tree.insert(
                "",
                tk.END,
                iid=iid_str,
                values=(
                    task.priority,
                    task.name,
                    task.created,
                ),
                tags=(task.priority,),
            )
            if selected_item_id is None and task.last_selected:
                selected_item_id = iid_str

        if selected_item_id is None:
            selected_item_id = "0"

        self.task_tree.selection_set(selected_item_id)
        self.task_tree.focus(selected_item_id)
        self.task_tree.see(selected_item_id)

        self.task_tree.focus_set()

    def get_selected_task(self) -> Task | None:

        selection = self.task_tree.selection()

        if not selection:
            return None

        item_id = selection[0]

        index = int(item_id)

        return self.display_tasks[index]

    def _on_tree_activate(self):
        self.decide_button.invoke()

    def _on_snooze_activate(self):
        self.snooze_button.invoke()

    def _on_decide_activate(self):
        self.decide_button.invoke()

    def _on_enter(self, event=None) -> None:
        widget = self.focus_get()

        if widget == self.task_tree:
            self._on_tree_activate()

        elif widget == self.snooze_button:
            self._on_snooze_activate()

        elif widget == self.decide_button:
            self._on_decide_activate()

    def _on_escape(self, event=None) -> None:
        self._on_snooze_activate()

    def _on_double_click(self, event=None) -> None:
        self._on_decide_activate()
