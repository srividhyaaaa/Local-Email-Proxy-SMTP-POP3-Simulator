import socket


HOST = "127.0.0.1"
PORT = 2525


def send_command(client, command):
    print(f"Client: {command}")
    client.sendall(f"{command}\r\n".encode("utf-8"))
    response = client.recv(4096).decode("utf-8", errors="replace")
    print(f"Server: {response}", end="")
    return response


def main():
    try:
        with socket.create_connection((HOST, PORT), timeout=10) as client:
            print("Server:", client.recv(4096).decode("utf-8", errors="replace"), end="")
            send_command(client, "HELO localhost")
            send_command(client, "MAIL FROM:<bob@localmail.com>")
            send_command(client, "RCPT TO:<alice@localmail.com>")
            send_command(client, "DATA")
            client.sendall(
                b"Subject: Hello Alice\r\n\r\n"
                b"Hi Alice! This is a test email.\r\n.\r\n"
            )
            print("Server:", client.recv(4096).decode("utf-8", errors="replace"), end="")
            send_command(client, "QUIT")
    except ConnectionRefusedError:
        print("Could not connect to SMTP. Start backend\\smtp_server.py first.")


if __name__ == "__main__":
    main()
