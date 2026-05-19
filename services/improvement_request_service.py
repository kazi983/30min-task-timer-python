"""改修要望サービス（ビジネスロジック層）"""
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from pathlib import Path
from data.improvement_request_repository import ImprovementRequestRepository


class ImprovementRequestService:
    """改修要望のビジネスロジック管理"""

    def __init__(self, data_file: Path) -> None:
        self.repository = ImprovementRequestRepository(data_file)
        self.requests: List[Dict] = self.repository.load_requests()

    def add_request(self, title: str, description: str, priority: str = "中") -> Dict:
        """新しい改修要望を追加"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_request = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "priority": priority,
            "status": "未対応",
            "created": now,
            "updated": now
        }
        self.requests.append(new_request)
        self.save()
        return new_request

    def edit_request(self, request_id: str, data: Dict) -> bool:
        """改修要望を編集"""
        for request in self.requests:
            if request["id"] == request_id:
                request.update(data)
                request["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save()
                return True
        return False

    def delete_request(self, request_id: str) -> bool:
        """改修要望を削除"""
        for i, request in enumerate(self.requests):
            if request["id"] == request_id:
                self.requests.pop(i)
                self.save()
                return True
        return False

    def get_requests(self) -> List[Dict]:
        """すべての改修要望を取得（作成日時の新しい順）"""
        return sorted(self.requests, key=lambda r: r["created"], reverse=True)

    def get_request_by_id(self, request_id: str) -> Optional[Dict]:
        """IDで改修要望を取得"""
        for request in self.requests:
            if request["id"] == request_id:
                return request
        return None

    def save(self) -> bool:
        """改修要望をファイルに保存"""
        return self.repository.save_requests(self.requests)
