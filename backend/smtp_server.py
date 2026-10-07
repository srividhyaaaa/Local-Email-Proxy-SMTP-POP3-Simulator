import socket

from firebase import add_email


HOST = "127.0.0.1"
PORT = 2525
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


def _read_message(client, buffer):
    terminator = b"\r\n.\r\n"
    while terminator not in buffer:
        chunk = client.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    message, _, remainder = buffer.partition(terminator)
    buffer[:] = remainder
    return message.decode("utf-8", errors="replace")


def _send(client, text):
    client.sendall(text.encode("utf-8"))


def start_smtp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"SMTP server running on {HOST}:{PORT}")

        while True:
            client, address = server.accept()
            print("Client connected:", address)
            with client:
                client.settimeout(SOCKET_TIMEOUT)
                client.sendall(b"220 Local SMTP Server Ready\r\n")
                handle_client(client)


def handle_client(client):
    sender = None
    receiver = None
    buffer = bytearray()

    try:
        while True:
            data = _read_line(client, buffer)
            if data is None:
                return

            command = data.strip()
            upper_command = command.upper()
            print("Client:", command)

            if upper_command.startswith("HELO ") or upper_command.startswith("EHLO "):
                _send(client, "250 Hello\r\n")
            elif upper_command.startswith("MAIL FROM:"):
                sender = command[10:].strip().strip("<>")
                _send(client, "250 Sender OK\r\n")
            elif upper_command.startswith("RCPT TO:"):
                receiver = command[8:].strip().strip("<>")
                _send(client, "250 Recipient OK\r\n")
            elif upper_command == "DATA":
                if not sender or not receiver:
                    _send(client, "503 Sender or recipient missing\r\n")
                    continue

                _send(client, "354 End data with <CR><LF>.<CR><LF>\r\n")
                email_text = _read_message(client, buffer)
                if email_text is None:
                    return

                headers, separator, message = email_text.partition("\r\n\r\n")
                subject = "No Subject"
                for line in headers.split("\r\n"):
                    if line.lower().startswith("subject:"):
                        subject = line[8:].strip()
                        break

                if not separator:
                    message = email_text

                if add_email(sender, receiver, subject, message):
                    _send(client, "250 Email accepted\r\n")
                else:
                    _send(client, "451 Could not store email\r\n")
            elif upper_command == "QUIT":
                _send(client, "221 Bye\r\n")
                return
            else:
                _send(client, "502 Command not recognized\r\n")
    except (ConnectionResetError, BrokenPipeError, socket.timeout, UnicodeError):
        return


if __name__ == "__main__":
    start_smtp_server()
