import os
import socket
import sys
import tempfile
import threading
import time
import tkinter as tk

from tkinter import messagebox

from app.controllers.app_controller import AppController

APP_NAME = "30min-task-timer"
LOCK_FILE = os.path.join(tempfile.gettempdir(), f"{APP_NAME}.lock")
HOST = "127.0.0.1"

stop_event = threading.Event()
server_socket = None


# =========================
# IPC Client
# =========================
def send_command(command: bytes) -> bool:
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as file:
            port = int(file.read().strip())

        with socket.create_connection((HOST, port), timeout=1) as sock:
            sock.sendall(command)

        return True

    except Exception:
        return False


def send_focus() -> bool:
    return send_command(b"FOCUS")


def send_shutdown() -> bool:
    return send_command(b"SHUTDOWN")


def is_existing_instance_alive() -> bool:
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as file:
            port = int(file.read().strip())

        with socket.create_connection((HOST, port), timeout=1):
            pass

        return True

    except Exception:
        return False


# =========================
# Startup Dialog
# =========================
def ask_existing_instance_action():

    dialog_root = tk.Tk()
    dialog_root.withdraw()

    result = messagebox.askokcancel(
        title="30min Task Timer",
        message=(
            "30min Task Timer is already running.\n\n"
            "Ok      : Replace existing instance\n"
            "Cancel  : Exit"
        ),
        parent=dialog_root,
    )

    dialog_root.destroy()

    return result


# =========================
# IPC Server
# =========================
def start_ipc_server(on_focus, on_shutdown):

    global server_socket

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, 0))

    port = server_socket.getsockname()[1]

    server_socket.listen()

    with open(LOCK_FILE, "w", encoding="utf-8") as file:
        file.write(str(port))

    def loop():

        while not stop_event.is_set():

            try:
                server_socket.settimeout(1.0)
                conn, _ = server_socket.accept()

            except socket.timeout:
                continue

            except OSError:
                break

            with conn:

                data = conn.recv(1024)

                if data == b"FOCUS":
                    on_focus()

                elif data == b"SHUTDOWN":
                    on_shutdown()

    threading.Thread(
        target=loop,
        daemon=True,
    ).start()


# =========================
# Cleanup
# =========================
def cleanup():

    stop_event.set()

    global server_socket

    if server_socket:

        try:
            server_socket.close()

        except OSError:
            pass

    try:
        os.remove(LOCK_FILE)

    except FileNotFoundError:
        pass


# =========================
# Main
# =========================
def main() -> None:

    root = tk.Tk()
    root.withdraw()

    app = AppController(root)

    def bring_to_front():

        def focus():

            root.deiconify()

            root.lift()

            root.focus_force()

            root.attributes("-topmost", True)

            root.after(
                200,
                lambda: root.attributes("-topmost", False),
            )

        root.after(0, focus)

    start_ipc_server(
        on_focus=bring_to_front,
        on_shutdown=app.exit_app,
    )

    def on_close():

        cleanup()

        root.destroy()

    root.protocol(
        "WM_DELETE_WINDOW",
        on_close,
    )

    app.start()

    root.mainloop()

    cleanup()


# =========================
# Entry Point
# =========================
if __name__ == "__main__":

    if is_existing_instance_alive():

        action = ask_existing_instance_action()

        if action is True:
            send_shutdown()

            for _ in range(50):

                if not is_existing_instance_alive():
                    break

                time.sleep(0.1)

            else:
                sys.exit(1)

        else:
            sys.exit(0)

    main()
