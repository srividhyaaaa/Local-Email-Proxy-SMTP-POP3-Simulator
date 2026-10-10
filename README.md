# Local-Email-Proxy-SMTP-POP3-Simulator
A local email system that simulates SMTP and POP3 protocols using TCP sockets, with a Python frontend and Firebase-powered backend for storing and retrieving emails.

## Tkinter Email Client

The frontend lives in `email_client/`. It uses only the Python standard library.

### Run

From the repository root, start the backend listening on `127.0.0.1:5000`, then run:

```powershell
py -m email_client.main
```

Change `HOST` and `PORT` in `email_client/config.py` to connect to another backend. The GUI sends network requests on background threads so the window remains responsive.

### Backend TCP contract

The client opens a TCP connection for each operation. The client sends exactly one UTF-8 JSON object followed by a newline. The backend should read through that newline, process the request, send exactly one UTF-8 JSON response followed by a newline, and close the connection. The client times out after five seconds and accepts responses up to 2 MiB.

Every response must include a boolean `ok`. Successful responses may include `data`; failures should set `ok` to `false` and include a user-safe `message`:

```json
{"ok": true, "data": {}}
```

```json
{"ok": false, "message": "Invalid username or password."}
```

Supported requests:

| Action | Request fields | Successful `data` |
| --- | --- | --- |
| `login` | `username`, `password` | `{"username": "user1"}` |
| `list_emails` | `username` | `{"emails": [{"id": "e1", "sender": "user2", "subject": "Hello", "timestamp": "2026-10-07 12:30:00"}]}` |
| `get_email` | `username`, `email_id` | `{"email": {"id": "e1", "sender": "user2", "receiver": "user1", "subject": "Hello", "timestamp": "2026-10-07 12:30:00", "body": "Message text"}}` |
| `send_email` | `sender`, `receiver`, `subject`, `body` | `{}` |
| `delete_email` | `username`, `email_id` | `{}` |
| `logout` | `username` | `{}` |

The sender field is set by the client from the logged-in username; the backend should verify it rather than trust it. Each inbox email's `id` must be unique within the inbox and is passed back unchanged in `get_email` and `delete_email` requests.

## GitHub

From the repository root, stage, commit, and push your changes:

```powershell
git add .
git commit -m "Add Tkinter email client"
git push
```

If you are pushing to a different GitHub repository, create it on GitHub and update the remote first. Use `git remote set-url origin https://github.com/USERNAME/REPOSITORY.git` if `origin` already exists, or `git remote add origin https://github.com/USERNAME/REPOSITORY.git` if it does not; then run `git push -u origin main`.
