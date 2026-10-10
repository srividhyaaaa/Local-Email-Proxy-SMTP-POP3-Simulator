"""Login screen for the email application."""

import tkinter as tk
from tkinter import messagebox, ttk


class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login, on_authenticated):
        super().__init__(master, padding=24)
        self.on_login = on_login
        self.on_authenticated = on_authenticated

        ttk.Label(self, text="Email Login", font=("TkDefaultFont", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 18)
        )
        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(self, width=32)
        self.username_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(self, width=32, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=5)
        self.password_entry.bind("<Return>", lambda _event: self.submit())

        self.login_button = ttk.Button(self, text="Log in", command=self.submit)
        self.login_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        self.columnconfigure(1, weight=1)

        self.username_entry.focus_set()

    def submit(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Login", "Enter both your username and password.", parent=self)
            return

        self.login_button.configure(state="disabled")
        self.on_login(username, password, self.login_finished)

    def login_finished(self, username, error):
        if error is not None:
            self.login_button.configure(state="normal")
            messagebox.showerror("Login failed", str(error), parent=self)
            return
        self.on_authenticated(username)