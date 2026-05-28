import tkinter as tk

from app.controllers.app_controller import AppController


def main() -> None:
    root = tk.Tk()

    root.withdraw()

    app = AppController(root)
    app.start()

    root.mainloop()


if __name__ == "__main__":
    main()
