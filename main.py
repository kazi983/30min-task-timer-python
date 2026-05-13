import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import os
import signal
from constants import *
from drag_drop_listbox import DragDropListbox
from improvement_request_manager import ImprovementRequestManager


class TaskManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        """タスク管理アプリ初期化"""
        self.root = root
        self.root.withdraw()
        default_font = tkfont.Font(family=FONT_FAMILY, size=10)
        self.root.option_add("*Font", default_font)
        self.root.option_add("*Menu.font", default_font)
        
        # モードに応じた保存先設定
        MODE = os.getenv("TASK_MODE", "production")
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