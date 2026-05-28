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

        for index, task in enumerate(tasks):

            self.task_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    task.priority,
                    task.text,
                    task.created,
                ),
                tags=(task.priority,),
            )

    def get_selected_task(self) -> Task | None:

        selection = self.task_tree.selection()

        if not selection:
            return None

        item_id = selection[0]

        index = int(item_id)

        return self.display_tasks[index]
