"""
app/views/task_manager_window.py
"""

import tkinter as tk
from tkinter import ttk

from app.models.task import Task
import app.config.constants as c
from collections.abc import Callable


class TaskManagerWindow(tk.Toplevel):
    """
    Task management UI window built with Tkinter.

    Responsibilities:
    - Present a list of tasks using a Treeview
    - Provide inputs for creating and updating tasks
    - Delegate task operations (add/edit/delete/complete) via callbacks

    This class is a view component and does not contain business logic.
    """

    def __init__(
        self,
        root: tk.Tk,
    ) -> None:

        super().__init__(root)

        self._setup_window(
            title="タスク管理", geometry=f"{c.WINDOW_WIDTH}x{c.WINDOW_HEIGHT}"
        )

        self.on_delete_task = None
        self.on_complete_task = None

        # ========================
        # Title
        # ========================

        title_label = ttk.Label(
            self,
            text="タスク管理",
        )
        title_label.pack(pady=10)

        # ========================
        # Treeview
        # ========================

        columns = ("completed", "priority", "name", "created")

        self.task_tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=10,
        )

        self.task_tree.heading(
            "completed",
            text="完了",
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
            "completed",
            width=40,
            anchor=tk.CENTER,
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
        # textbox
        # ========================

        self.new_task_frame = ttk.Frame(self)
        self.new_task_frame.pack(
            pady=10,
            padx=10,
            after=title_label,
        )

        self.new_task_box = ttk.Entry(self.new_task_frame, width=30)
        self.new_task_box.pack(side=tk.LEFT, padx=10)

        self.new_task_priority_combo = ttk.Combobox(
            self.new_task_frame,
            width=15,
            state="readonly",
            values=["NOW", "SOONER", "ANYTIME", "SOMEDAY"],
        )
        self.new_task_priority_combo.pack(side=tk.LEFT, padx=10)

        # ========================
        # buttons
        # ========================

        self.button_frame_top = ttk.Frame(self)
        self.button_frame_top.pack(pady=10, after=self.new_task_frame)
        self.button_frame_middle = ttk.Frame(self)
        self.button_frame_middle.pack(pady=10, after=self.button_frame_top)
        self.button_frame_bottom = ttk.Frame(self)
        self.button_frame_bottom.pack(pady=10)

        self.add_button = ttk.Button(
            self.button_frame_top,
            text="新規登録",
        )

        self.add_button.pack(
            side=tk.LEFT,
            padx=10,
        )

        self.edit_button = ttk.Button(
            self.button_frame_middle,
            text="上書き",
        )

        self.edit_button.pack(
            side=tk.LEFT,
            padx=10,
        )

        self.back_button = ttk.Button(
            self.button_frame_bottom,
            text="戻る",
        )

        self.back_button.pack(
            side=tk.LEFT,
            padx=5,
        )

        # ========================
        # bind
        # ========================
        self.task_tree.bind("<Return>", self._on_enter)
        self.task_tree.bind("<BackSpace>", self._on_backspace)
        self.task_tree.bind("<Delete>", self._on_delete)

        self.bind("<Escape>", self._on_escape)

        self.task_tree.bind("<Double-1>", self._on_double_click)

        self.task_tree.bind("<<TreeviewSelect>>", self._on_select_task_tree)

        self.tasks: list[Task] = []

        self.new_task_box.focus_set()

    def update_task_list(
        self,
        tasks: list[Task],
    ) -> None:
        """
        Refresh task list in the Treeview.

        Args:
            tasks: List of tasks to display.
        """

        for item_id in self.task_tree.get_children():
            self.task_tree.delete(item_id)

        self.tasks = tasks

        for priority, color in c.PRIORITY_COLORS.items():

            self.task_tree.tag_configure(
                priority,
                background=color,
            )

        selected_item_id = None
        for index, task in enumerate(tasks):

            tags = (task.priority,)
            if task.completed:
                tags += ("completed",)

            self.task_tree.insert(
                "",
                tk.END,
                iid=task.id,
                values=(
                    task.completed,
                    task.priority,
                    task.name,
                    task.created,
                ),
                tags=tags,
            )

            if selected_item_id is None and task.last_selected:
                selected_item_id = task.id

        if selected_item_id is None:
            selected_item_id = tasks[0].id

        self.task_tree.selection_set(selected_item_id)
        self.task_tree.focus(selected_item_id)
        self.task_tree.see(selected_item_id)

        self.new_task_box.focus_set()

    def get_input_value(self) -> dict[str, str] | None:
        """
        Get current input values from entry and combobox.

        Returns:
            Dict with task name and priority, or None if invalid.
        """

        task = self.new_task_box.get()
        priority = self.new_task_priority_combo.get()

        if not task or not priority:
            return None

        return {"name": task, "priority": priority}

    def get_selected_task(self) -> Task | None:
        """
        Get currently selected task from Treeview.

        Returns:
            Selected Task or None.
        """

        selection = self.task_tree.selection()

        if not selection:
            return None

        task_id = selection[0]

        return next((t for t in self.tasks if t.id == task_id), None)

    def set_complete_callback(self, callback: Callable[[], None]):
        """
        Set callback for complete action.

        Args:
            callback: Function to call when complete is triggered.
        """

        self.on_complete_task = callback

    def set_delete_callback(self, callback: Callable[[], None]):
        """
        Set callback for delete action.

        Args:
            callback: Function to call when delete is triggered.
        """

        self.on_delete_task = callback

    def _on_edit_activate(self):
        self.edit_button.invoke()

    def _on_back_to_selection_activate(self):
        self.back_button.invoke()

    def _on_add_activate(self):
        self.add_button.invoke()

    def _on_enter(self, _event=None) -> None:
        widget = self.focus_get()

        if widget == self.task_tree:
            self._on_edit_activate()

        elif widget == self.back_button:
            self._on_back_to_selection_activate()

        elif widget == self.add_button:
            self._on_add_activate()

    def _on_double_click(self, _event=None) -> None:
        self._on_edit_activate()

    def _on_escape(self, _event=None) -> None:
        self._on_back_to_selection_activate()

    def _on_backspace(self, _event=None) -> None:
        if self.on_complete_task:
            self.on_complete_task()

    def _on_delete(self, _event=None) -> None:
        if self.on_delete_task:
            self.on_delete_task()

    def _on_select_task_tree(self, _event=None) -> None:
        selection = self.task_tree.selection()

        if not selection:
            return None

        task_id = selection[0]
        task = next((t for t in self.tasks if t.id == task_id), None)

        self.new_task_box.delete(0, tk.END)
        self.new_task_box.insert(0, task.name)

        self.new_task_priority_combo.set(task.priority)

    def _setup_window(self, title: str, geometry: str) -> None:
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()
        self.title(title)
        self.geometry(geometry)
