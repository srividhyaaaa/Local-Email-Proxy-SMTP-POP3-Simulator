"""Inbox screen and email actions."""

import tkinter as tk
from tkinter import messagebox, ttk

from .compose import ComposeWindow
from .email_view import EmailView


class InboxFrame(ttk.Frame):
    def __init__(self, master, app, username):
        super().__init__(master, padding=14)
        self.app = app
        self.username = username

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text=f"Inbox: {username}", font=("TkDefaultFont", 16, "bold")).pack(
            side="left", padx=(0, 16)
        )
        ttk.Button(toolbar, text="Compose", command=self.open_compose).pack(side="left", padx=3)
        self.refresh_button = ttk.Button(toolbar, text="Refresh", command=self.refresh)
        self.refresh_button.pack(side="left", padx=3)
        self.delete_button = ttk.Button(toolbar, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=3)
        ttk.Button(toolbar, text="Log out", command=self.logout).pack(side="right", padx=3)

        columns = ("sender", "subject", "timestamp")
        self.email_table = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.email_table.heading("sender", text="Sender")
        self.email_table.heading("subject", text="Subject")
        self.email_table.heading("timestamp", text="Date/Time")
        self.email_table.column("sender", width=170, minwidth=100)
        self.email_table.column("subject", width=320, minwidth=140)
        self.email_table.column("timestamp", width=190, minwidth=130)
        self.email_table.pack(fill="both", expand=True)
        self.email_table.bind("<Double-1>", self.open_selected)
        self.email_table.bind("<Return>", self.open_selected)

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(anchor="w", pady=(8, 0))
        self.refresh()

    def refresh(self):
        self.refresh_button.configure(state="disabled")
        self.status_label.configure(text="Loading inbox...")
        self.app.run_async(
            lambda: self.app.client.request(
                {"action": "list_emails", "username": self.username}
            ),
            self.inbox_loaded,
            self.inbox_failed,
        )

    def inbox_loaded(self, data):
        self.refresh_button.configure(state="normal")
        emails = data.get("emails", []) if isinstance(data, dict) else data
        if not isinstance(emails, list):
            self.inbox_failed(ValueError("The server returned an invalid email list."))
            return

        for item_id in self.email_table.get_children():
            self.email_table.delete(item_id)
        for email in emails:
            if not isinstance(email, dict) or email.get("id") is None:
                continue
            self.email_table.insert(
                "",
                "end",
                iid=str(email["id"]),
                values=(
                    email.get("sender", ""),
                    email.get("subject", ""),
                    email.get("timestamp", ""),
                ),
            )
        count = len(self.email_table.get_children())
        self.status_label.configure(text=f"{count} email{'s' if count != 1 else ''}")

    def inbox_failed(self, error):
        self.refresh_button.configure(state="normal")
        self.status_label.configure(text="Inbox could not be loaded.")
        messagebox.showerror("Inbox", str(error), parent=self)

    def open_compose(self):
        ComposeWindow(self, self.username, self.send_email, self.refresh)

    def send_email(self, receiver, subject, body, on_complete):
        request_data = {
            "action": "send_email",
            "sender": self.username,
            "receiver": receiver,
            "subject": subject,
            "body": body,
        }
        self.app.run_async(
            lambda: self.app.client.request(request_data),
            lambda result: on_complete(result, None),
            lambda error: on_complete(None, error),
        )

    def selected_email_id(self):
        selection = self.email_table.selection()
        return selection[0] if selection else None

    def open_selected(self, _event=None):
        email_id = self.selected_email_id()
        if email_id is None:
            return
        self.status_label.configure(text="Opening email...")
        self.app.run_async(
            lambda: self.app.client.request(
                {"action": "get_email", "username": self.username, "email_id": email_id}
            ),
            self.email_loaded,
            self.inbox_failed,
        )

    def email_loaded(self, data):
        email = data.get("email", data) if isinstance(data, dict) else None
        if not isinstance(email, dict):
            self.inbox_failed(ValueError("The server returned an invalid email."))
            return
        self.status_label.configure(text="")
        EmailView(self, email)

    def delete_selected(self):
        email_id = self.selected_email_id()
        if email_id is None:
            messagebox.showinfo("Delete email", "Select an email to delete.", parent=self)
            return
        if not messagebox.askyesno(
            "Delete email", "Delete the selected email?", parent=self
        ):
            return

        self.delete_button.configure(state="disabled")
        self.app.run_async(
            lambda: self.app.client.request(
                {"action": "delete_email", "username": self.username, "email_id": email_id}
            ),
            self.email_deleted,
            self.delete_failed,
        )

    def email_deleted(self, _data):
        self.delete_button.configure(state="normal")
        messagebox.showinfo("Delete email", "Email deleted.", parent=self)
        self.refresh()

    def delete_failed(self, error):
        self.delete_button.configure(state="normal")
        messagebox.showerror("Delete email", str(error), parent=self)

    def logout(self):
        self.app.logout(self.username)