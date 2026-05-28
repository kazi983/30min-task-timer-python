import os

from pathlib import Path


APP_NAME = "30min-task-timer"


def get_app_data_dir() -> Path:
    """
    アプリデータ保存ディレクトリ取得
    """

    if os.name == "nt":

        appdata = os.getenv("APPDATA")

        if appdata:
            return Path(appdata) / APP_NAME

    xdg_config = os.getenv(
        "XDG_CONFIG_HOME"
    )

    if xdg_config:
        return Path(xdg_config) / APP_NAME

    return (
        Path.home()
        / f".{APP_NAME}"
    )


MODE = os.getenv(
    "TASK_MODE",
    "production",
)

filename = (
    "tasks_test.json"
    if MODE == "test"
    else "tasks.json"
)

APP_DATA_DIR = get_app_data_dir()

APP_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TASK_DATA_FILE = (
    APP_DATA_DIR / filename
)