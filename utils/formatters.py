"""書式整形ユーティリティモジュール."""

from datetime import datetime


def format_datetime(dt: datetime) -> str:
    """日時オブジェクトを表示用文字列に変換する。"""
    return dt.strftime("%Y-%m-%d %H:%M")
