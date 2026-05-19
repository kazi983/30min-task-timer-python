"""共通ストレージモジュール."""

from pathlib import Path


class Storage:
    """ストレージ操作を提供するユーティリティクラス。"""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def get_path(self, filename: str) -> Path:
        return self.base_dir / filename
