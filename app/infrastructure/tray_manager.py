import pystray

from PIL import Image


class TrayManager:
    """
    Manage the system tray icon and tray menu actions.

    This class integrates the application with the operation
    system tray using pystray. It handles tray menu events,
    application restarting, and graceful shutdown behavior.
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
        Start the tray icon event loop in detached mode.
        """

        self.icon.run_detached()

    def handle_restart(self) -> None:
        """
        Trigger the callback for restarting the application from the tray menu.
        """

        self.on_restart()

    def handle_exit(self) -> None:
        """
        Trigger the callback for shutting down the app.
        """

        self.icon.stop()

        self.on_exit()
