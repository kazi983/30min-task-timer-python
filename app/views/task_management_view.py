"""
app/views/task_management_view.py
"""

import tkinter as tk
from tkinter import ttk

from app.models.task import Task
import app.config.constants as c


class _UIColors:
    # =====================
    # SUB VIEW (management)
    # =====================

    BG_SUB = "#f3f4f6"  # 明るいニュートラルグレー（重要）
    # CARD = "#ffffff"
    BORDER = "#d1d5db"

    BASE = "#111827"
    TEXT_SUB = "#6b7280"

    ACCENT = "#4d8eff"
    ACCENT_SOFT = "#e0f2fe"

    SELECT_BG = "#dbeafe"

    PRIMARY = "#1e6c3b"
    NEUTRAL = "#404C63"
    DESTRUCTIVE = "#8e0909"

    PRIORITY = {
        "NOW": "#fee2e2",
        "SOONER": "#fef3c7",
        "ANYTIME": "#dcfce7",
        "SOMEDAY": "#f3f4f6",
    }


class TaskManagementView(tk.Toplevel):
    """
    Task management UI view built with Tkinter.

    Responsibilities:
    - Present a list of tasks using a Treeview
    - Provide inputs for creating and updating tasks
    - Delegate task operations (add/edit/delete/complete) via callbacks

    This class is a view component and does not contain business logic.
    """

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)

        self._setup_view()

        self.tasks: list[Task] = []

        # =========================
        # CONTAINER
        # =========================

        container = tk.Frame(self, bg=_UIColors.BG_SUB)
        container.pack(fill="both", expand=True, padx=28, pady=24)

        # =========================
        # HEADER
        # =========================

        header = tk.Frame(container, bg=_UIColors.BG_SUB)
        header.pack(fill="x", pady=(0, 12))

        tk.Label(
            header,
            text="タスク管理",
            font=(c.FONT_FAMILY, 18, "bold"),
            bg=_UIColors.BG_SUB,
            fg=_UIColors.BASE,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="タスクの追加・編集・整理",
            font=(c.FONT_FAMILY, 10),
            bg=_UIColors.BG_SUB,
            fg=_UIColors.TEXT_SUB,
        ).pack(anchor="w")

        # =========================
        # TABLE
        # =========================

        table_card = tk.Frame(
            container,
            bg="white",
            highlightthickness=1,
            highlightbackground=_UIColors.BORDER,
        )
        table_card.pack(fill="both", expand=True, pady=12)

        self.task_tree = ttk.Treeview(
            table_card,
            columns=("completed", "priority", "name", "memo", "created_at"),
            show="headings",
            height=11,
        )

        self.task_tree.heading("completed", text="✓")
        self.task_tree.heading("priority", text="優先度")
        self.task_tree.heading("name", text="タスク")
        self.task_tree.heading("memo", text="メモ")
        self.task_tree.heading("created_at", text="作成日")

        self.task_tree.column("completed", width=40, anchor="center")
        self.task_tree.column("priority", width=80, anchor="center")
        self.task_tree.column("name", width=300)
        self.task_tree.column("memo", width=600)
        self.task_tree.column("created_at", width=110, anchor="center")

        self.task_tree.pack(fill="both", expand=True, padx=8, pady=8)

        for priority, color in _UIColors.PRIORITY.items():
            self.task_tree.tag_configure(priority, background=color)

        # =========================
        # INPUT CARD
        # =========================

        input_card = tk.Frame(
            container,
            bg="white",
            highlightthickness=1,
            highlightbackground=_UIColors.BORDER,
        )
        input_card.pack(fill="x", pady=10)

        input_row = tk.Frame(input_card, bg="white")
        input_row.pack(padx=12, pady=10, fill="x")

        # ---- task name ----
        self.new_task_box = tk.Entry(
            input_row,
            font=(c.FONT_FAMILY, 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground=_UIColors.BORDER,
            highlightcolor=_UIColors.ACCENT,
            width=28,
        )
        self.new_task_box.pack(side=tk.LEFT, padx=6, ipady=5)

        # ---- priority ----
        self.new_task_priority_combo = ttk.Combobox(
            input_row,
            width=10,
            state="readonly",
            values=["NOW", "SOONER", "ANYTIME", "SOMEDAY"],
        )
        self.new_task_priority_combo.set("NOW")
        self.new_task_priority_combo.pack(side=tk.LEFT, padx=8)

        # ---- memo (NEW) ----
        self.new_task_memo_box = tk.Entry(
            input_row,
            font=(c.FONT_FAMILY, 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground=_UIColors.BORDER,
            highlightcolor=_UIColors.ACCENT,
            width=35,
        )
        self.new_task_memo_box.pack(side=tk.LEFT, padx=8, ipady=5)

        # =========================
        # ACTION BAR
        # =========================

        action_bar = tk.Frame(container, bg=_UIColors.BG_SUB)
        action_bar.pack(fill="x", pady=10)

        # left actions
        self.add_button = tk.Button(
            action_bar,
            text="＋ 新規登録",
            bg=_UIColors.ACCENT,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
        )
        self.add_button.pack(side=tk.LEFT)

        # right actions
        right = tk.Frame(action_bar, bg=_UIColors.BG_SUB)
        right.pack(side=tk.RIGHT)

        self.complete_button = tk.Button(
            right,
            text="完了",
            bg=_UIColors.PRIMARY,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
        )
        self.complete_button.pack(side=tk.LEFT, padx=6)

        self.delete_button = tk.Button(
            right,
            text="削除",
            bg=_UIColors.DESTRUCTIVE,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
        )
        self.delete_button.pack(side=tk.LEFT, padx=6)

        self.edit_button = tk.Button(
            right,
            text="更新",
            bg=_UIColors.NEUTRAL,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
        )
        self.edit_button.pack(side=tk.LEFT, padx=6)

        self.back_button = tk.Button(
            right,
            text="戻る",
            bg=_UIColors.NEUTRAL,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
        )
        self.back_button.pack(side=tk.LEFT, padx=6)

        # =========================
        # BINDINGS
        # =========================
        self.bind("<Escape>", lambda e: self.back_button.invoke())

        self.task_tree.bind("<<TreeviewSelect>>", self._on_select_task_tree)

        self.task_tree.bind(
            "<Return>", self._on_enter_task_tree
        )  # テキストボックス選択
        self.task_tree.bind("<BackSpace>", lambda e: self.complete_button.invoke())
        self.task_tree.bind("<Delete>", lambda e: self.delete_button.invoke())

        self.new_task_box.bind("<Return>", lambda e: self.add_button.invoke())
        self.new_task_priority_combo.bind(
            "<Return>", lambda e: self.add_button.invoke()
        )

        self.new_task_box.focus_set()

    # =========================
    # DATA
    # =========================

    def update_task_list(self, tasks: list[Task]) -> None:
        """
        Refresh task list in the Treeview.

        Args:
            tasks: List of tasks to display.
        """

        self.tasks = tasks

        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        selected_id = None

        for task in tasks:

            tags = (task.priority,)
            if task.completed:
                tags += ("completed",)

            self.task_tree.insert(
                "",
                "end",
                iid=task.id,
                values=(
                    "✓" if task.completed else "",
                    task.priority,
                    task.name,
                    task.memo,
                    task.created_local(),
                ),
                tags=tags,
            )

            if task.last_selected:
                selected_id = task.id

        if tasks:
            selected_id = selected_id or tasks[0].id
            self.task_tree.selection_set(selected_id)
            self.task_tree.focus(selected_id)
            self.task_tree.see(selected_id)

        self.new_task_box.focus_set()

    # =========================
    # INPUT API
    # =========================

    def get_input_value(self) -> dict[str, str] | None:
        """
        Get current input values from entry and combobox.

        Returns:
            Dict with task name and priority, or None if invalid.
        """

        name = self.new_task_box.get().strip()
        priority = self.new_task_priority_combo.get()
        memo = self.new_task_memo_box.get().strip()

        if not name:
            return None

        return {
            "name": name,
            "priority": priority,
            "memo": memo,
        }

    # =========================
    # TASK SELECT
    # =========================

    def get_selected_task(self) -> Task | None:
        """
        Get currently selected task from Treeview.

        Returns:
            Selected Task or None.
        """
        sel = self.task_tree.selection()
        if not sel:
            return None

        return next((t for t in self.tasks if t.id == sel[0]), None)

    # =========================
    # ACTION HANDLERS
    # =========================

    def _on_edit_request(self, _event=None) -> None:
        self.edit_button.invoke()

    def _on_escape(self, _event=None) -> None:
        self.back_button.invoke()

    def _on_backspace(self, _event=None) -> None:
        self.complete_button.invoke()

    def _on_delete(self, _event=None) -> None:
        self.delete_button.invoke()

    # =========================
    # TREE SELECTION
    # =========================

    def _on_select_task_tree(self, _event=None):
        sel = self.task_tree.selection()
        if not sel:
            return

        task = next((t for t in self.tasks if t.id == sel[0]), None)
        if not task:
            return

        self.new_task_box.delete(0, tk.END)
        self.new_task_box.insert(0, task.name)
        self.new_task_priority_combo.set(task.priority)

    def _on_enter_task_tree(self, _event=None):
        self.new_task_box.focus()

    # =========================
    # NAV
    # =========================

    def _setup_view(self) -> None:
        self.configure(bg=_UIColors.BG_SUB)

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.lift()
        self.focus_force()

        self.update_idletasks()

        w = c.WINDOW_WIDTH
        h = c.WINDOW_HEIGHT

        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")
