"""Read-only email viewer."""

import tkinter as tk
from tkinter import ttk


class EmailView(tk.Toplevel):
    def __init__(self, master, email):
        super().__init__(master)
        self.title(email.get("subject") or "Email")
        self.geometry("640x480")
        self.minsize(420, 320)

        content = ttk.Frame(self, padding=16)
        content.pack(fill="both", expand=True)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(4, weight=1)

        fields = (
            ("From", email.get("sender", "")),
            ("To", email.get("receiver", "")),
            ("Subject", email.get("subject", "")),
            ("Date/Time", email.get("timestamp", "")),
        )
        for row, (label, value) in enumerate(fields):
            ttk.Label(content, text=f"{label}:").grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=4)
            ttk.Label(content, text=str(value), wraplength=500).grid(
                row=row, column=1, sticky="w", pady=4
            )

        body = tk.Text(content, wrap="word", height=12)
        body.insert("1.0", email.get("body", ""))
        body.configure(state="disabled")
        body.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(12, 0))