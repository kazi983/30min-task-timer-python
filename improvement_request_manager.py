import tkinter as tk
from tkinter import messagebox, font as tkfont, scrolledtext
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import uuid
from constants import FONT_FAMILY, PRIMARY_COLOR, COLOR_HIGH, COLOR_MEDIUM, COLOR_LOW


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