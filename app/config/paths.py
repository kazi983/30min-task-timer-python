"""
app/config/path.py

Application path configuration.

This module defines platform-specific application data directories
and resolves file paths used for persistent task storage.

It also supports environment-based configuration (e.g. test mode).
"""

import os

from pathlib import Path

APP_NAME = "30min-task-timer"


def get_app_data_dir() -> Path:
    """
    Get the application data directory depending on the operating system.

    Returns:
        Path object pointing to the app data directory.
    """

    if os.name == "nt":

        appdata = os.getenv("APPDATA")

        if appdata:
            return Path(appdata) / APP_NAME

    xdg_config = os.getenv("XDG_CONFIG_HOME")

    if xdg_config:
        return Path(xdg_config) / APP_NAME

    return Path.home() / f".{APP_NAME}"


MODE = os.getenv(
    "TASK_MODE",
    "production",
)

FILENAME = "tasks_test.json" if MODE == "test" else "tasks.json"

APP_DATA_DIR = get_app_data_dir()

APP_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TASK_DATA_FILE = APP_DATA_DIR / FILENAME
