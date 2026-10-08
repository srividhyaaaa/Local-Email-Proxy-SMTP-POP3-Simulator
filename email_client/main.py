"""Application entry point and Tkinter/network task coordination."""

import queue
import threading
import tkinter as tk
from tkinter import messagebox

from .client import EmailClient
from .config import HOST, PORT
from .inbox import InboxFrame
from .login import LoginFrame


class EmailApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Application")
        self.root.geometry("820x520")
        self.root.minsize(620, 380)
        self.client = EmailClient(HOST, PORT)
        self.current_username = None
        self.current_frame = None
        self.task_queue = queue.Queue()
        self.show_login()
        self.root.after(100, self.process_tasks)

    def show_frame(self, frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.show_frame(LoginFrame(self.root, self.login, self.on_authenticated))

    def show_inbox(self):
        self.show_frame(InboxFrame(self.root, self, self.current_username))

    def login(self, username, password, on_complete):
        self.run_async(
            lambda: self.client.request(
                {"action": "login", "username": username, "password": password}
            ),
            lambda _data: on_complete(username, None),
            lambda error: on_complete(username, error),
        )

    def on_authenticated(self, username):
        self.current_username = username
        self.show_inbox()

    def logout(self, username):
        def complete(_data):
            self.current_username = None
            self.show_login()

        def failed(error):
            self.current_username = None
            self.show_login()
            messagebox.showwarning("Log out", f"Logged out locally. {error}", parent=self.root)

        self.run_async(
            lambda: self.client.request({"action": "logout", "username": username}),
            complete,
            failed,
        )

    def run_async(self, operation, on_success, on_error):
        """Run blocking socket work off the Tk thread and deliver its result on Tk."""
        def worker():
            try:
                result = operation()
            except Exception as error:
                self.task_queue.put((on_error, error))
            else:
                self.task_queue.put((on_success, result))

        threading.Thread(target=worker, daemon=True).start()

    def process_tasks(self):
        while True:
            try:
                callback, result = self.task_queue.get_nowait()
            except queue.Empty:
                break
            callback(result)
        self.root.after(100, self.process_tasks)


def main():
    root = tk.Tk()
    EmailApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()