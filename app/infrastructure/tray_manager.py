"""
app/infrastructure/tray_manager.py

System tray integration module.

Provides TrayManager which manages the system tray icon and its menu actions
using pystray. Supports application restart and graceful shutdown from tray.
"""

import pystray

from PIL import Image


class TrayManager:
    """
    Manages system tray integration for the application.

    Responsibilities:
    - Create and display system tray icon
    - Handle tray menu actions (restart, exit)
    - Delegate application lifecycle actions via callbacks

    This class acts as an infrastructure layer for OS-level integration.
    """

    def __init__(
        self,
        on_restart,
        on_exit,
    ) -> None:

        self.on_restart = on_restart

        self.on_exit = on_exit

        image = Image.new(
            "RGB",
            (64, 64),
            color="blue",
        )

        menu = pystray.Menu(
            pystray.MenuItem(
                "再起動",
                self.handle_restart,
            ),
            pystray.MenuItem(
                "終了",
                self.handle_exit,
            ),
        )

        self.icon = pystray.Icon(
            "30min-task-timer",
            image,
            "30min Task Timer",
            menu,
        )

    def run(self) -> None:
        """
        Start the system tray icon in detached mode.

        This runs the tray event loop without blocking the main application.
        """

        self.icon.run_detached()

    def handle_restart(self) -> None:
        """
        Handle restart action from tray menu.

        Delegates restart logic to the injected callback.
        """

        self.on_restart()

    def handle_exit(self) -> None:
        """
        Handle exit action from tray menu.

        Stops the tray icon and triggers application shutdown callback.
        """
        self.icon.stop()

        self.on_exit()
