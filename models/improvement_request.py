"""改修要望データモデル"""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ImprovementRequest:
    """改修要望"""
    id: str
    title: str
    description: str
    priority: str  # "高", "中", "低"
    status: str  # "未対応", "対応中", "完了"
    created: str  # "YYYY-MM-DD HH:MM"
    updated: str  # "YYYY-MM-DD HH:MM"

    @classmethod
    def from_dict(cls, data: dict) -> "ImprovementRequest":
        """辞書からインスタンス生成"""
        return cls(**data)

    def to_dict(self) -> dict:
        """辞書に変換"""
        return asdict(self)
