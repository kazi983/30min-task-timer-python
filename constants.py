import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import os
import signal
import uuid


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