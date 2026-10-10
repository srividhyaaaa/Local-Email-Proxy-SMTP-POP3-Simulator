"""Compose-email window."""

import tkinter as tk
from tkinter import messagebox, ttk


class ComposeWindow(tk.Toplevel):
    def __init__(self, master, username, on_send, on_sent):
        super().__init__(master)
        self.on_send = on_send
        self.on_sent = on_sent
        self.title("Compose email")
        self.geometry("620x470")
        self.minsize(480, 360)
        self.transient(master)

        content = ttk.Frame(self, padding=16)
        content.pack(fill="both", expand=True)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(3, weight=1)

        ttk.Label(content, text="From").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        sender_entry = ttk.Entry(content)
        sender_entry.insert(0, username)
        sender_entry.configure(state="readonly")
        sender_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(content, text="To").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        self.receiver_entry = ttk.Entry(content)
        self.receiver_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(content, text="Subject").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        self.subject_entry = ttk.Entry(content)
        self.subject_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(content, text="Message").grid(row=3, column=0, sticky="nw", padx=(0, 10), pady=5)
        self.body_text = tk.Text(content, wrap="word", height=12, undo=True)
        self.body_text.grid(row=3, column=1, sticky="nsew", pady=5)

        self.send_button = ttk.Button(content, text="Send", command=self.submit)
        self.send_button.grid(row=4, column=1, sticky="e", pady=(12, 0))
        self.receiver_entry.focus_set()

    def submit(self):
        receiver = self.receiver_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", "end-1c").strip()
        if not receiver or not subject or not body:
            messagebox.showerror(
                "Compose email", "Enter a receiver, subject, and message.", parent=self
            )
            return

        self.send_button.configure(state="disabled")
        self.on_send(receiver, subject, body, self.send_finished)

    def send_finished(self, _result, error):
        if error is not None:
            self.send_button.configure(state="normal")
            messagebox.showerror("Send failed", str(error), parent=self)
            return

        messagebox.showinfo("Email sent", "Your email was sent.", parent=self)
        self.on_sent()
        self.destroy()