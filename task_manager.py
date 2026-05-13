import tkinter as tk
from tkinter import messagebox, font as tkfont, scrolledtext
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import os
import signal
import uuid

# モード設定（環境変数 TASK_MODE=test でテストモード）
MODE = os.getenv("TASK_MODE", "production")

# 定数
INTERVAL_MS = 5000 if MODE == "test" else 30 * 60 * 1000  # テスト用5秒、本番用30分
SNOOZE_MS = 5 * 60 * 1000  # 5分

# 色定数
COLOR_HIGH = "#ffcdd2"
COLOR_MEDIUM = "#fff9c4"
COLOR_LOW = "#e8f5e9"
COLOR_NONE = "#ffffff"
PRIMARY_COLOR = "#4CAF50"

# ウィンドウサイズ
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
DIALOG_WIDTH = 480
DIALOG_HEIGHT = 520

# フォント（Segoe UI統一）
FONT_FAMILY = "Meiryo"


class ImprovementRequestManager:
    """改修要望管理クラス"""
    
    def __init__(self, parent_window: tk.Tk, mode: str = "production") -> None:
        self.parent = parent_window
        self.mode = mode
        filename = "improvement_requests_test.json" if mode == "test" else "improvement_requests.json"
        self.data_file = Path.home() / filename
        self.requests: List[Dict] = []
        self.load_requests()
    
    def load_requests(self) -> None:
        """改修要望読み込み"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.requests = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"改修要望読み込みエラー: {e}")
                self.requests = []
    
    def save_requests(self) -> None:
        """改修要望保存"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.requests, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("保存エラー", f"改修要望の保存に失敗:\n{e}")
    
    def show_management_window(self) -> None:
        """改修要望管理ウィンドウ表示"""
        window = tk.Toplevel(self.parent)
        window.title("改修要望管理")
        window.geometry("600x500")
        
        # フォント設定
        default_font = tkfont.Font(family=FONT_FAMILY, size=10)
        window.option_add("*Font", default_font)
        
        # タイトル
        tk.Label(window, text="改修要望管理", 
                font=tkfont.Font(family=FONT_FAMILY, size=16, weight="bold")).pack(pady=10)
        
        # 新規ボタン
        btn_frame = tk.Frame(window)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="新規要望", command=lambda: self.show_add_edit_dialog(window),
                 font=tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
                 bg=PRIMARY_COLOR, fg="white").pack()
        
        # 一覧
        list_frame = tk.Frame(window)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.request_listbox = tk.Listbox(
            list_frame,
            font=tkfont.Font(family=FONT_FAMILY, size=10),
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.request_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.request_listbox.yview)
        
        # ダブルクリックで編集
        self.request_listbox.bind('<Double-Button-1>', lambda e: self.edit_selected_request(window))
        
        # 操作ボタン
        op_frame = tk.Frame(window)
        op_frame.pack(pady=10)
        
        tk.Button(op_frame, text="編集", command=lambda: self.edit_selected_request(window),
                 font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT, padx=5)
        tk.Button(op_frame, text="削除", command=lambda: self.delete_selected_request(window),
                 font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT, padx=5)
        tk.Button(op_frame, text="閉じる", command=window.destroy,
                 font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT, padx=5)
        
        # キーボードショートカット
        window.bind('<Control-n>', lambda e: self.show_add_edit_dialog(window))
        window.bind('<Return>', lambda e: self.edit_selected_request(window))
        window.bind('<Delete>', lambda e: self.delete_selected_request(window))
        window.bind('<Escape>', lambda e: window.destroy())
        
        self.update_request_list(window)
    
    def show_add_edit_dialog(self, parent_window: tk.Toplevel, request: Optional[Dict] = None) -> None:
        """要望追加/編集ダイアログ"""
        is_edit = request is not None
        title = "改修要望の編集" if is_edit else "改修要望の追加"
        
        dialog = tk.Toplevel(parent_window)
        dialog.title(title)
        dialog.geometry("500x400")
        
        tk.Label(dialog, text=title, 
                font=tkfont.Font(family=FONT_FAMILY, size=14, weight="bold")).pack(pady=10)
        
        # フォーム
        form_frame = tk.Frame(dialog)
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # タイトル
        tk.Label(form_frame, text="タイトル:", anchor=tk.W).pack(fill=tk.X)
        title_var = tk.StringVar(value=request.get("title", "") if request else "")
        title_entry = tk.Entry(form_frame, textvariable=title_var,
                              font=tkfont.Font(family=FONT_FAMILY, size=10))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 説明
        tk.Label(form_frame, text="説明:", anchor=tk.W).pack(fill=tk.X)
        desc_text = scrolledtext.ScrolledText(form_frame, height=8, 
                                             font=tkfont.Font(family=FONT_FAMILY, size=10))
        desc_text.pack(fill=tk.X, pady=(0, 10))
        if request:
            desc_text.insert(tk.END, request.get("description", ""))
        
        # 優先度
        tk.Label(form_frame, text="優先度:", anchor=tk.W).pack(fill=tk.X)
        priority_var = tk.StringVar(value=request.get("priority", "中") if request else "中")
        priority_spinbox = tk.Spinbox(form_frame, values=("高", "中", "低"),
                                     textvariable=priority_var, state="readonly",
                                     justify=tk.CENTER)
        priority_spinbox.pack(pady=(0, 10))
        
        # ステータス
        tk.Label(form_frame, text="ステータス:", anchor=tk.W).pack(fill=tk.X)
        status_var = tk.StringVar(value=request.get("status", "未対応") if request else "未対応")
        status_spinbox = tk.Spinbox(form_frame, values=("未対応", "対応中", "完了"),
                                   textvariable=status_var, state="readonly",
                                   justify=tk.CENTER)
        status_spinbox.pack(pady=(0, 10))
        
        # ボタン
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def save_request():
            if not title_var.get().strip():
                messagebox.showwarning("警告", "タイトルを入力してください", parent=dialog)
                return
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            if is_edit and request:
                request["title"] = title_var.get().strip()
                request["description"] = desc_text.get("1.0", tk.END).strip()
                request["priority"] = priority_var.get()
                request["status"] = status_var.get()
                request["updated"] = now
            else:
                new_request = {
                    "id": str(uuid.uuid4()),
                    "title": title_var.get().strip(),
                    "description": desc_text.get("1.0", tk.END).strip(),
                    "priority": priority_var.get(),
                    "status": status_var.get(),
                    "created": now,
                    "updated": now
                }
                self.requests.append(new_request)
            
            self.save_requests()
            dialog.destroy()
            self.update_request_list(parent_window)
        
        tk.Button(btn_frame, text="保存", command=save_request,
                 font=tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
                 bg=PRIMARY_COLOR, fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="キャンセル", command=dialog.destroy,
                 font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT, padx=5)
        
        title_entry.focus()
    
    def edit_selected_request(self, parent_window: tk.Toplevel) -> None:
        """選択中の要望を編集"""
        selection = self.request_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.requests):
                request = self.requests[index]
                self.show_add_edit_dialog(parent_window, request)
    
    def delete_selected_request(self, parent_window: tk.Toplevel) -> None:
        """選択中の要望を削除"""
        selection = self.request_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.requests):
                request = self.requests[index]
                if messagebox.askyesno("確認", f"「{request['title']}」を削除しますか？", parent=parent_window):
                    self.requests.pop(index)
                    self.save_requests()
                    self.update_request_list(parent_window)
    
    def update_request_list(self, parent_window: tk.Toplevel) -> None:
        """要望一覧更新"""
        if not hasattr(self, 'request_listbox'):
            return
        
        self.request_listbox.delete(0, tk.END)
        
        # 作成日時でソート（新しい順）
        sorted_requests = sorted(self.requests, key=lambda r: r["created"], reverse=True)
        
        for request in sorted_requests:
            priority_mark = {"高": "[高]", "中": "[中]", "低": "[低]"}.get(request.get("priority", "中"), "[中]")
            status_mark = {"未対応": "未", "対応中": "中", "完了": "完"}.get(request.get("status", "未対応"), "未")
            display_text = f"{priority_mark} {request['title']} ({status_mark})"
            self.request_listbox.insert(tk.END, display_text)
            
            # 優先度に応じた背景色
            bg_color = {
                "高": COLOR_HIGH,
                "中": COLOR_MEDIUM,
                "低": COLOR_LOW
            }.get(request.get("priority", "中"), COLOR_MEDIUM)
            self.request_listbox.itemconfig(self.request_listbox.size() - 1, bg=bg_color)


class DragDropListbox(tk.Listbox):
    """ドラッグ＆ドロップ対応Listbox"""
    def __init__(self, master, drag_callback=None, **kw):
        kw['selectmode'] = tk.SINGLE
        super().__init__(master, **kw)
        self.drag_callback = drag_callback
        self.bind('<Button-1>', self.set_current)
        self.bind('<B1-Motion>', self.shift_selection)
        self.cur_index = None
    
    def set_current(self, event):
        """ドラッグ開始位置を記録"""
        self.cur_index = self.nearest(event.y)
    
    def shift_selection(self, event):
        """ドラッグ中の並び替え"""
        i = self.nearest(event.y)
        if self.cur_index is None or i == self.cur_index:
            return
        
        if i < self.cur_index:
            x = self.get(i)
            self.delete(i)
            self.insert(i + 1, x)
            self.cur_index = i
            if self.drag_callback:
                self.drag_callback(i + 1, i)
        elif i > self.cur_index:
            x = self.get(i)
            self.delete(i)
            self.insert(i - 1, x)
            self.cur_index = i
            if self.drag_callback:
                self.drag_callback(i - 1, i)


class TaskManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        """タスク管理アプリ初期化"""
        self.root = root
        self.root.withdraw()
        default_font = tkfont.Font(family=FONT_FAMILY, size=10)
        self.root.option_add("*Font", default_font)
        self.root.option_add("*Menu.font", default_font)
        
        # モードに応じた保存先設定
        filename = "tasks_test.json" if MODE == "test" else "tasks.json"
        self.data_file = Path.home() / filename
        self.tasks: List[Dict] = []
        self.last_selected_task_text: Optional[str] = None  # 前回選択したタスク
        self.load_tasks()
        
        self.scheduled_timer: Optional[str] = None
        
        # 改修要望マネージャー
        self.improvement_manager = ImprovementRequestManager(self.root, MODE)
        
        # UI要素
        self.task_entry: Optional[tk.Entry] = None
        self.task_listbox: Optional[DragDropListbox] = None
        self.status_label: Optional[tk.Label] = None
        self.priority_var: Optional[tk.StringVar] = None
        self.priority_menu: Optional[tk.OptionMenu] = None
        self.show_completed_var: Optional[tk.BooleanVar] = None
        self.sort_var: Optional[tk.StringVar] = None
        
        # フィルタ/ソート後の表示用タスクリスト
        self.display_tasks: List[Dict] = []
        
        self.show_task_selection_dialog()
    
    def bring_to_front(self, window: tk.Toplevel | tk.Tk) -> None:
        """ウィンドウを最前面に表示"""
        window.lift()
        window.focus_force()
        window.attributes('-topmost', True)
        window.after(100, lambda: window.attributes('-topmost', False))
    
    def cancel_scheduled_timer(self) -> None:
        """タイマーキャンセル"""
        if self.scheduled_timer:
            self.root.after_cancel(self.scheduled_timer)
            self.scheduled_timer = None
    
    def schedule_next_notification(self) -> None:
        """次回通知スケジュール"""
        self.cancel_scheduled_timer()
        self.scheduled_timer = self.root.after(INTERVAL_MS, self.show_task_selection_dialog)
    
    def setup_keyboard_shortcuts(self) -> None:
        """キーボードショートカット設定"""
        self.root.bind('<Control-n>', lambda e: self.add_task())
        # Delete: 削除（リストボックス選択時のみ）
        if self.task_listbox:
            self.task_listbox.bind('<Delete>', lambda e: self.delete_task())
            # Backspace: 完了（リストボックス選択時のみ）
            self.task_listbox.bind('<BackSpace>', lambda e: self.complete_task())
    
    def focus_task_entry(self) -> None:
        """タスク入力欄にフォーカス"""
        if self.task_entry:
            self.task_entry.focus()
    
    def ensure_listbox_selection(self) -> None:
        """Listboxにフォーカスがあるとき、アクティブ項目を選択する"""
        if not self.task_listbox:
            return
        if self.task_listbox.curselection():
            return
        try:
            index = self.task_listbox.index(tk.ACTIVE)
        except tk.TclError:
            index = 0
        if 0 <= index < self.task_listbox.size():
            self.task_listbox.selection_set(index)
    
    def on_drag_drop(self, from_index: int, to_index: int) -> None:
        """ドラッグ＆ドロップ時のコールバック"""
        if self.sort_var and self.sort_var.get() == "手動":
            # 表示タスクの順序変更を元のタスクリストに反映
            task = self.display_tasks.pop(from_index)
            self.display_tasks.insert(to_index, task)
            
            # 元のタスクリストも更新
            self.tasks = self.display_tasks.copy()
            self.save_tasks()
    
    def show_main_window(self) -> None:
        """タスク一覧ウィンドウ表示"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.deiconify()
        self.root.title("タスク一覧")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        self.bring_to_front(self.root)
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        self.update_task_list()
    
    def create_widgets(self) -> None:
        """UI作成"""
        # タイトル
        tk.Label(self.root, text="タスク一覧", 
                font=tkfont.Font(family=FONT_FAMILY, size=18, weight="bold")).pack(pady=10)
        
        # タスク入力フレーム
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(input_frame, text="新しいタスク:", 
                font=tkfont.Font(family=FONT_FAMILY, size=10)).pack(side=tk.LEFT)
        self.task_entry = tk.Entry(input_frame, width=28, 
                                   font=tkfont.Font(family=FONT_FAMILY, size=10))
        self.task_entry.pack(side=tk.LEFT, padx=5)
        self.task_entry.bind("<Return>", lambda e: self.add_task())
        self.task_entry.focus()
        
        # 優先度選択
        tk.Label(input_frame, text="優先度:", 
                font=tkfont.Font(family=FONT_FAMILY, size=10)).pack(side=tk.LEFT, padx=(10, 0))
        self.priority_var = tk.StringVar(value="なし")
        self.priority_spinbox = tk.Spinbox(
            input_frame,
            values=("高", "中", "低", "なし"),
            textvariable=self.priority_var,
            width=6,
            state="readonly",
            wrap=True,
            justify=tk.CENTER,
            takefocus=True
        )
        self.priority_spinbox.pack(side=tk.LEFT, padx=5)
        
        add_button = tk.Button(input_frame, text="追加", command=self.add_task, 
                              font=tkfont.Font(family=FONT_FAMILY, size=9))
        add_button.pack(side=tk.LEFT, padx=5)
        
        self.task_entry.bind("<Tab>", lambda e: self.priority_spinbox.focus_set() or "break")
        self.priority_spinbox.bind("<Tab>", lambda e: add_button.focus_set() or "break")
        
        # フィルタ・ソートフレーム
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=8, padx=20, fill=tk.X)
        
        self.show_completed_var = tk.BooleanVar(value=True)
        tk.Checkbutton(filter_frame, text="完了済みを表示", 
                      variable=self.show_completed_var, 
                      command=self.update_task_list,
                      font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT)
        
        tk.Label(filter_frame, text="並び順:", 
                font=tkfont.Font(family=FONT_FAMILY, size=9)).pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="手動")
        sort_menu = tk.OptionMenu(filter_frame, self.sort_var, "手動", "名前順", 
                                 "作成日時順", "優先度順",
                                 command=lambda _: self.update_task_list())
        sort_menu.config(font=tkfont.Font(family=FONT_FAMILY, size=9), width=10)
        sort_menu.pack(side=tk.LEFT)
        
        # ドラッグ＆ドロップヒント
        if self.sort_var.get() == "手動":
            tk.Label(filter_frame, text="(ドラッグ＆ドロップで並び替え)", 
                    font=tkfont.Font(family=FONT_FAMILY, size=8), fg="gray").pack(side=tk.LEFT, padx=10)
        
        # タスクリスト
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = DragDropListbox(
            list_frame, 
            drag_callback=self.on_drag_drop,
            yscrollcommand=scrollbar.set,
            font=tkfont.Font(family=FONT_FAMILY, size=10),
            height=15
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        self.task_listbox.bind('<FocusIn>', lambda e: self.ensure_listbox_selection())
        self.task_listbox.bind('<ButtonRelease-1>', lambda e: self.ensure_listbox_selection())
        
        # ボタンフレーム
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="削除\nDel", width=8, command=self.delete_task,
                 font=tkfont.Font(family=FONT_FAMILY, size=9), height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="完了\nBack", width=8, command=self.complete_task,
                 font=tkfont.Font(family=FONT_FAMILY, size=9), height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="全削除", width=8, command=self.clear_all,
                 font=tkfont.Font(family=FONT_FAMILY, size=9), height=2).pack(side=tk.LEFT, padx=5)
        
        # タスク選択ボタン
        proceed_frame = tk.Frame(self.root)
        proceed_frame.pack(pady=15)
        
        tk.Button(proceed_frame, text="タスクを選択する", 
                 command=self.proceed_to_selection,
                 font=tkfont.Font(family=FONT_FAMILY, size=11, weight="bold"), 
                 bg=PRIMARY_COLOR, fg="white",
                 padx=25, pady=12).pack()
        
        # ステータスバー
        self.status_label = tk.Label(
            self.root, 
            text="タスクを追加したら「タスクを選択する」をクリック",
            relief=tk.SUNKEN, anchor=tk.W, 
            font=tkfont.Font(family=FONT_FAMILY, size=9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 改修要望ボタン（右下）
        improvement_button = tk.Button(
            self.root,
            text="要望",
            command=self.improvement_manager.show_management_window,
            font=tkfont.Font(family=FONT_FAMILY, size=8),
            width=6, height=1,
            relief=tk.FLAT
        )
        improvement_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=5, pady=2)
    
    def get_priority_color(self, priority: str) -> str:
        """優先度に応じた背景色を返す"""
        return {
            "高": COLOR_HIGH,
            "中": COLOR_MEDIUM,
            "低": COLOR_LOW,
            "なし": COLOR_NONE
        }.get(priority, COLOR_NONE)
    
    def add_task(self) -> None:
        """タスク追加"""
        if not self.task_entry or not self.priority_var:
            return
        
        task_text = self.task_entry.get().strip()
        if task_text:
            task = {
                "text": task_text,
                "completed": False,
                "priority": self.priority_var.get(),
                "created": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            self.tasks.append(task)
            self.task_entry.delete(0, tk.END)
            self.priority_var.set("なし")
            self.update_task_list()
            self.save_tasks()
            
            if self.status_label:
                self.status_label.config(text=f"追加: {task_text}")
            self.task_entry.focus()
    
    def delete_task(self) -> None:
        """タスク削除"""
        if not self.task_listbox:
            return
        
        selection = self.task_listbox.curselection()
        display_index = None
        if selection:
            display_index = selection[0]
        elif self.task_listbox and self.task_listbox.size() > 0:
            try:
                display_index = self.task_listbox.index(tk.ACTIVE)
            except tk.TclError:
                display_index = None
        
        if display_index is not None and display_index < len(self.display_tasks):
            task_to_delete = self.display_tasks[display_index]
            self.tasks.remove(task_to_delete)
            self.update_task_list()
            self.save_tasks()
            
            if self.status_label:
                self.status_label.config(text=f"削除: {task_to_delete['text']}")
    
    def complete_task(self) -> None:
        """タスク完了"""
        if not self.task_listbox:
            return
        
        selection = self.task_listbox.curselection()
        display_index = None
        if selection:
            display_index = selection[0]
        elif self.task_listbox and self.task_listbox.size() > 0:
            try:
                display_index = self.task_listbox.index(tk.ACTIVE)
            except tk.TclError:
                display_index = None
        
        if display_index is not None and display_index < len(self.display_tasks):
            task = self.display_tasks[display_index]
            task["completed"] = True
            self.update_task_list()
            self.save_tasks()
            
            if self.status_label:
                self.status_label.config(text=f"完了: {task['text']}")
                self.save_tasks()
                
                if self.status_label:
                    self.status_label.config(text=f"完了: {task['text']}")
    
    def clear_all(self) -> None:
        """全タスク削除"""
        if messagebox.askyesno("確認", "すべて削除しますか？"):
            self.tasks = []
            self.update_task_list()
            self.save_tasks()
            
            if self.status_label:
                self.status_label.config(text="すべてのタスクを削除しました")
    
    def get_filtered_sorted_tasks(self) -> List[Dict]:
        """フィルタ・ソート適用後のタスクリスト"""
        # フィルタ
        if self.show_completed_var and not self.show_completed_var.get():
            filtered = [t for t in self.tasks if not t["completed"]]
        else:
            filtered = self.tasks.copy()
        
        # ソート
        if self.sort_var:
            sort_type = self.sort_var.get()
            if sort_type == "名前順":
                filtered.sort(key=lambda t: t["text"].lower())
            elif sort_type == "作成日時順":
                filtered.sort(key=lambda t: t["created"], reverse=True)
            elif sort_type == "優先度順":
                priority_order = {"高": 0, "中": 1, "低": 2, "なし": 3}
                filtered.sort(key=lambda t: priority_order.get(t.get("priority", "なし"), 3))
        
        return filtered
    
    def update_task_list(self) -> None:
        """タスクリスト表示更新"""
        if not self.task_listbox:
            return
        
        self.task_listbox.delete(0, tk.END)
        self.display_tasks = self.get_filtered_sorted_tasks()
        
        for i, task in enumerate(self.display_tasks):
            status = "✓" if task["completed"] else "□"
            priority = task.get("priority", "なし")
            priority_mark = {"高": "[高]", "中": "[中]", "低": "[低]"}.get(priority, "   ")
            created = task.get("created", "")
            
            task_text = task['text']
            display_text = f"{status} {priority_mark} {task_text}".ljust(60) + f"  {created}"
            
            self.task_listbox.insert(tk.END, display_text)
            
            # 背景色
            bg_color = self.get_priority_color(priority)
            self.task_listbox.itemconfig(i, bg=bg_color)
            
            # 完了済みは灰色
            if task["completed"]:
                self.task_listbox.itemconfig(i, fg="gray")
    
    def proceed_to_selection(self) -> None:
        """タスク選択ダイアログへ"""
        self.root.withdraw()
        self.show_task_selection_dialog()
    
    def show_task_selection_dialog(self) -> None:
        """タスク選択ダイアログ表示"""
        incomplete = [t for t in self.tasks if not t["completed"]]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("次の30分で取り組むタスク")
        dialog.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}")
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.bring_to_front(dialog)
        
        tk.Label(dialog, text="次の30分で取り組むタスクを選択:", 
                font=tkfont.Font(family=FONT_FAMILY, size=13, weight="bold")).pack(pady=15)
        tk.Label(dialog, text="ショートカット: Ctrl+N タスク追加 | Esc 5分後再通知",
                font=tkfont.Font(family=FONT_FAMILY, size=9), fg="gray").pack(pady=(0, 10))
        
        if not incomplete:
            tk.Label(dialog, text="未完了のタスクがありません", 
                    font=tkfont.Font(family=FONT_FAMILY, size=10), fg="gray").pack(pady=20)
            
            # タスクがない場合でもEscで閉じられるように
            def close_empty_dialog(e=None):
                dialog.destroy()
                self.cancel_scheduled_timer()
                self.show_main_window()
            
            dialog.bind('<Escape>', close_empty_dialog)
            dialog.bind('<Control-n>', lambda e: close_empty_dialog())
            
            # 下部ボタンのみ表示
            bottom_frame = tk.Frame(dialog)
            bottom_frame.pack(pady=10, side=tk.BOTTOM)
            
            tk.Button(bottom_frame, text="タスク追加", command=close_empty_dialog,
                     font=tkfont.Font(family=FONT_FAMILY, size=9), width=15).pack()
        else:
            listbox = tk.Listbox(dialog, font=tkfont.Font(family=FONT_FAMILY, size=10), height=13)
            listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            # リストにタスクを追加
            for task in incomplete:
                priority = task.get("priority", "なし")
                priority_mark = {"高": "[高]", "中": "[中]", "低": "[低]"}.get(priority, "")
                display = f"{priority_mark} {task['text']}".strip()
                listbox.insert(tk.END, display)
            
            # 前回選択したタスクを探す
            initial_index = 0
            if self.last_selected_task_text:
                for i, task in enumerate(incomplete):
                    if task['text'] == self.last_selected_task_text:
                        initial_index = i
                        break
            
            # 前回選択したタスクに選択とフォーカスを当てる
            listbox.selection_set(initial_index)
            listbox.activate(initial_index)  # アクティブ化（フォーカス）
            listbox.see(initial_index)  # スクロールして表示
            listbox.focus()  # リストボックス自体にフォーカス
            
            def select_task(e=None) -> None:
                sel = listbox.curselection()
                if sel:
                    selected = incomplete[sel[0]]
                    self.last_selected_task_text = selected['text']  # 選択を記憶
                    
                    # 選択完了ダイアログを表示
                    self.show_completion_dialog(dialog, selected)
                else:
                    messagebox.showwarning("警告", "タスクを選択してください", parent=dialog)
            
            def delete_selected_task(e=None) -> None:
                """Deleteキーでタスク削除"""
                sel = listbox.curselection()
                if sel:
                    selected = incomplete[sel[0]]
                    self.tasks.remove(selected)
                    self.save_tasks()
                    dialog.destroy()
                    # 再度タスク選択ダイアログを表示
                    self.show_task_selection_dialog()
            
            def complete_selected_task(e=None) -> None:
                """Backspaceキーでタスク完了"""
                sel = listbox.curselection()
                if sel:
                    selected = incomplete[sel[0]]
                    selected["completed"] = True
                    self.save_tasks()
                    dialog.destroy()
                    # 再度タスク選択ダイアログを表示
                    self.show_task_selection_dialog()
            
            # Enterキーで決定
            listbox.bind('<Return>', select_task)
            # Deleteキーで削除
            listbox.bind('<Delete>', delete_selected_task)
            # Backspaceキーで完了
            listbox.bind('<BackSpace>', complete_selected_task)
            
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=15)
            
            tk.Button(btn_frame, text="決定", command=select_task,
                     font=tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"), 
                     bg=PRIMARY_COLOR, fg="white",
                     width=12, padx=10, pady=5).pack()
            
            # 下部ボタン
            bottom_frame = tk.Frame(dialog)
            bottom_frame.pack(pady=10, side=tk.BOTTOM)
            
            def snooze(e=None) -> None:
                dialog.destroy()
                self.cancel_scheduled_timer()
                self.scheduled_timer = self.root.after(SNOOZE_MS, self.show_task_selection_dialog)
            
            tk.Button(bottom_frame, text="5分後再通知", command=snooze,
                     font=tkfont.Font(family=FONT_FAMILY, size=9), width=15).pack(side=tk.LEFT, padx=5)
            dialog.bind('<Escape>', snooze)
            
            def go_to_task_list() -> None:
                dialog.destroy()
                self.cancel_scheduled_timer()
                self.show_main_window()
            
            tk.Button(bottom_frame, text="タスク追加", command=go_to_task_list,
                     font=tkfont.Font(family=FONT_FAMILY, size=9), width=15).pack(side=tk.LEFT, padx=5)
            dialog.bind('<Control-n>', lambda e: go_to_task_list())
    
    def show_completion_dialog(self, parent_dialog: tk.Toplevel, selected_task: Dict) -> None:
        """選択完了ダイアログ表示"""
        parent_dialog.destroy()
        
        completion = tk.Toplevel(self.root)
        completion.title("選択完了")
        completion.geometry("400x250")
        
        self.bring_to_front(completion)
        
        tk.Label(completion, text="次の30分のタスク:", 
                font=tkfont.Font(family=FONT_FAMILY, size=12, weight="bold")).pack(pady=20)
        
        tk.Label(completion, text=f"「{selected_task['text']}」", 
                font=tkfont.Font(family=FONT_FAMILY, size=11), 
                wraplength=350).pack(pady=10)
        
        tk.Label(completion, text="頑張ってください！", 
                font=tkfont.Font(family=FONT_FAMILY, size=10)).pack(pady=10)
        
        def close_and_schedule(e=None):
            completion.destroy()
            self.schedule_next_notification()
        
        def cancel_selection(e=None):
            completion.destroy()
            self.show_task_selection_dialog()
        
        # EnterキーでOK
        completion.bind('<Return>', close_and_schedule)
        # Escキーでキャンセル（選択画面に戻る）
        completion.bind('<Escape>', cancel_selection)
        
        btn_frame = tk.Frame(completion)
        btn_frame.pack(pady=20)
        
        ok_button = tk.Button(btn_frame, text="OK (Enter)", command=close_and_schedule,
                 font=tkfont.Font(family=FONT_FAMILY, size=10, weight="bold"),
                 bg=PRIMARY_COLOR, fg="white",
                 width=12, padx=10, pady=5)
        ok_button.pack(side=tk.LEFT, padx=5)
        ok_button.focus()  # OKボタンにフォーカス
        
        cancel_button = tk.Button(btn_frame, text="キャンセル (Esc)", command=cancel_selection,
                 font=tkfont.Font(family=FONT_FAMILY, size=9),
                 width=15)
        cancel_button.pack(side=tk.LEFT, padx=5)

        def move_dialog_focus(event=None):
            current = completion.focus_get()
            if current == ok_button:
                cancel_button.focus_set()
            else:
                ok_button.focus_set()
            return "break"

        completion.bind('<Left>', move_dialog_focus)
        completion.bind('<Right>', move_dialog_focus)
    
    def save_tasks(self) -> None:
        """タスク保存"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("保存エラー", f"タスクの保存に失敗:\n{e}")
    
    def load_tasks(self) -> None:
        """タスク読み込み"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
                    # 古いデータに優先度追加
                    for task in self.tasks:
                        if "priority" not in task:
                            task["priority"] = "なし"
            except (json.JSONDecodeError, IOError) as e:
                print(f"読み込みエラー: {e}")
                messagebox.showwarning("読み込みエラー", 
                    "タスクファイルが破損しています。新規作成します。")
                self.tasks = []


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    
    # Ctrl+C で停止できるように設定
    def signal_handler(sig, frame):
        root.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    root.mainloop()