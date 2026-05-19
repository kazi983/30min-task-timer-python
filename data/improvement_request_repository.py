"""改修要望リポジトリ（データ永続化層）"""
import json
from pathlib import Path
from typing import List, Dict
from tkinter import messagebox


class ImprovementRequestRepository:
    """改修要望のJSON保存・読込を管理"""

    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file

    def load_requests(self) -> List[Dict]:
        """改修要望をファイルから読込"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"改修要望読み込みエラー: {e}")
                return []
        return []

    def save_requests(self, requests: List[Dict]) -> bool:
        """改修要望をファイルに保存"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            messagebox.showerror("保存エラー", f"改修要望の保存に失敗:\n{e}")
            return False
