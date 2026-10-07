import socket


HOST = "127.0.0.1"
PORT = 1100


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
            send_command(client, "USER alice")
            login_response = send_command(client, "PASS 1234")
            if login_response.startswith("-ERR"):
                print("POP3 login failed. Register alice with password 1234 first.")
                return

            stat_response = send_command(client, "STAT")
            send_command(client, "LIST")
            if stat_response.split()[1].isdigit() and int(stat_response.split()[1]) > 0:
                send_command(client, "RETR 1")
                send_command(client, "DELE 1")
            send_command(client, "QUIT")
    except ConnectionRefusedError:
        print("Could not connect to POP3. Start backend\\pop3_server.py first.")


if __name__ == "__main__":
    main()
