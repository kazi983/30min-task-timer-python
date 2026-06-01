# app/views/task_selection_window.py

import tkinter as tk
from tkinter import ttk

from app.models.task import Task
import app.config.constants as c


class TaskSelectionWindow(tk.Toplevel):

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        super().__init__(root)

        self.attributes("-topmost", True)

        self.lift()

        self.focus_force()

        self.title("タスク選択")

        self.geometry(f"{c.WINDOW_WIDTH}x{c.WINDOW_HEIGHT}")

        title_label = ttk.Label(
            self,
            text="次のタスクを選択してください",
        )
        title_label.pack(pady=10)

        # ========================
        # Treeview
        # ========================

        columns = ("priority", "name", "created")

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

        self.task_tree.heading("name", text="タスク")

        self.task_tree.heading(
            "created",
            text="作成日時",
        )

        self.task_tree.column(
            "priority",
            width=c.TR_WIDTH_PRIORITY,
            anchor=tk.CENTER,
        )

        self.task_tree.column(
            "name",
            width=c.TR_WIDTH_NAME,
        )

        self.task_tree.column(
            "created",
            width=c.TR_WIDTH_DATE,
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

        button_frame_main = ttk.Frame(self)
        button_frame_sub = ttk.Frame(self)

        button_frame_main.pack(pady=10, before=self.task_tree)
        button_frame_sub.pack(pady=10)

        self.snooze_button = ttk.Button(
            button_frame_sub,
            text="5分後再通知",
        )

        self.snooze_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        self.decide_button = ttk.Button(
            button_frame_main,
            text="決定",
        )

        self.decide_button.pack(
            side=tk.LEFT,
            padx=30,
        )

        self.open_task_manager_button = ttk.Button(
            button_frame_sub,
            text="管理画面",
        )

        self.open_task_manager_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        # ========================
        # bind
        # ========================
        self.task_tree.bind("<Return>", self._on_enter)
        self.task_tree.bind("<BackSpace>", self._on_backspace)
        self.task_tree.bind("<Delete>", self._on_delete)

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

            tags = (task.priority,)
            if task.completed:
                tags += ("completed",)

            self.task_tree.insert(
                "",
                tk.END,
                iid=iid_str,
                values=(
                    task.priority,
                    task.name,
                    task.created,
                ),
                tags=tags,
            )
            if selected_item_id is None and task.last_selected:
                selected_item_id = iid_str

        if selected_item_id is None:
            selected_item_id = "0"

        self.task_tree.tag_configure("NOW", background=c.COLOR_HIGH)
        self.task_tree.tag_configure("SOONER", background=c.COLOR_MEDIUM)
        self.task_tree.tag_configure("ANYTIME", background=c.COLOR_MEDIUM)
        self.task_tree.tag_configure("SOMEDAY", background=c.COLOR_MEDIUM)
        self.task_tree.tag_configure("completed", background="gray")

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

    def set_complete_callback(self, callback):
        self.complete_callback = callback

    def set_delete_callback(self, callback):
        self.delete_callback = callback

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

    def _on_backspace(self, event=None) -> None:
        self.complete_callback()

    def _on_delete(self, event=None) -> None:
        self.delete_callback()
