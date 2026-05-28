import os

COLOR_HIGH = "#ffcdd2"
COLOR_MEDIUM = "#fff9c4"
COLOR_LOW = "#e8f5e9"
COLOR_NONE = "#ffffff"
PRIORITY_COLORS = {
    "高": COLOR_HIGH,
    "中": COLOR_MEDIUM,
    "低": COLOR_LOW,
    "なし": COLOR_NONE,
}
PRIMARY_COLOR = "#4CAF50"

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
MAIN_WINDOW_WIDTH = 400
MAIN_WINDOW_HEIGHT = 500

FONT_FAMILY = "Meiryo"

TIME_MS_SNOOZE = (
    10000 if os.getenv("TASK_MODE", "production") == "test" else 5 * 60 * 1000
)
TIME_MS_INTERVAL = (
    5000 if os.getenv("TASK_MODE", "production") == "test" else 30 * 60 * 1000
)
