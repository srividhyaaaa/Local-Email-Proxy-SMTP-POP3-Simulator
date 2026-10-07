import socket

from authentication import login_user
from firebase import delete_email, get_emails


HOST = "127.0.0.1"
PORT = 1100
SOCKET_TIMEOUT = 60


def _read_line(client, buffer):
    while b"\r\n" not in buffer:
        chunk = client.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    line, _, remainder = buffer.partition(b"\r\n")
    buffer[:] = remainder
    return line.decode("utf-8", errors="replace")


def _send(client, text):
    client.sendall(text.encode("utf-8"))


def _field(email, name):
    return email.get("fields", {}).get(name, {}).get("stringValue", "")


def _email_size(email):
    return len((_field(email, "subject") + _field(email, "message")).encode("utf-8"))


def _get_authenticated_emails(username):
    return get_emails(f"{username}@localmail.com")


def start_pop3_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"POP3 server running on {HOST}:{PORT}")

        while True:
            client, address = server.accept()
            print("Client connected:", address)
            with client:
                client.settimeout(SOCKET_TIMEOUT)
                client.sendall(b"+OK Local POP3 Server Ready\r\n")
                handle_client(client)


def handle_client(client):
    username = None
    authenticated = False
    buffer = bytearray()

    try:
        while True:
            data = _read_line(client, buffer)
            if data is None:
                return

            parts = data.strip().split(None, 1)
            command = parts[0].upper() if parts else ""
            argument = parts[1].strip() if len(parts) == 2 else ""
            print("Client:", data)

            if command == "USER":
                if argument:
                    username = argument
                    authenticated = False
                    _send(client, "+OK User accepted\r\n")
                else:
                    _send(client, "-ERR Username required\r\n")
            elif command == "PASS":
                if not username:
                    _send(client, "-ERR USER command required\r\n")
                elif not argument:
                    _send(client, "-ERR Password required\r\n")
                elif login_user(username, argument):
                    authenticated = True
                    _send(client, "+OK Login successful\r\n")
                else:
                    _send(client, "-ERR Invalid username or password\r\n")
            elif command in {"STAT", "LIST", "RETR", "DELE"}:
                if not authenticated:
                    _send(client, "-ERR Please login first\r\n")
                    continue

                emails = _get_authenticated_emails(username)
                if command == "STAT":
                    _send(client, f"+OK {len(emails)} {sum(map(_email_size, emails))}\r\n")
                elif command == "LIST":
                    response = f"+OK {len(emails)} messages\r\n"
                    response += "".join(
                        f"{index} {_email_size(email)}\r\n"
                        for index, email in enumerate(emails, 1)
                    )
                    _send(client, response + ".\r\n")
                else:
                    if not argument.isdigit() or int(argument) < 1:
                        _send(client, "-ERR Invalid message number\r\n")
                        continue

                    message_number = int(argument)
                    if message_number > len(emails):
                        _send(client, "-ERR No such message\r\n")
                        continue

                    email = emails[message_number - 1]
                    if command == "RETR":
                        receiver = f"{username}@localmail.com"
                        response = (
                            f"+OK Message {message_number}\r\n"
                            f"From: {_field(email, 'sender')}\r\n"
                            f"To: {receiver}\r\n"
                            f"Subject: {_field(email, 'subject')}\r\n\r\n"
                            f"{_field(email, 'message')}\r\n.\r\n"
                        )
                        _send(client, response)
                    elif delete_email(email):
                        _send(client, "+OK Message deleted\r\n")
                    else:
                        _send(client, "-ERR Could not delete message\r\n")
            elif command == "QUIT":
                _send(client, "+OK Bye\r\n")
                return
            else:
                _send(client, "-ERR Command not recognized\r\n")
    except (ConnectionResetError, BrokenPipeError, socket.timeout, UnicodeError):
        return


if __name__ == "__main__":
    start_pop3_server()
