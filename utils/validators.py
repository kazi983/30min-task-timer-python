"""検証ユーティリティモジュール."""


def validate_task_title(title: str) -> bool:
    """タスクタイトルの基本検証を行う。"""
    return bool(title and title.strip())
