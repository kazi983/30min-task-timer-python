import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import os
import signal
import uuid

APP_NAME = "30min-task-timer"

def get_app_data_dir() -> Path:
    """Return the application-specific directory for storing data."""
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / APP_NAME
    return Path.home() / Path(f".{APP_NAME}")

APP_DATA_DIR = get_app_data_dir()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 定数
INTERVAL_MS = 5000 if os.getenv("TASK_MODE", "production") == "test" else 30 * 60 * 1000  # テスト用5秒、本番用30分
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