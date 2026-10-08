"""Small JSON-over-TCP client used by the GUI."""

import json
import socket

from .config import HOST, MAX_RESPONSE_BYTES, PORT, SOCKET_TIMEOUT_SECONDS


class EmailClientError(Exception):
    """An expected connection, protocol, or server error."""


class EmailClient:
    def __init__(
        self,
        host=HOST,
        port=PORT,
        timeout=SOCKET_TIMEOUT_SECONDS,
        max_response_bytes=MAX_RESPONSE_BYTES,
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_response_bytes = max_response_bytes

    def request(self, request_data):
        """Send one JSON line and return the response's data field."""
        try:
            request_bytes = (json.dumps(request_data) + "\n").encode("utf-8")
            with socket.create_connection(
                (self.host, self.port), timeout=self.timeout
            ) as connection:
                connection.settimeout(self.timeout)
                connection.sendall(request_bytes)

                response_bytes = bytearray()
                while b"\n" not in response_bytes:
                    chunk = connection.recv(4096)
                    if not chunk:
                        break
                    response_bytes.extend(chunk)
                    if len(response_bytes) > self.max_response_bytes:
                        raise EmailClientError("The server response was too large.")

            response_line = bytes(response_bytes).split(b"\n", 1)[0].strip()
            if not response_line:
                raise EmailClientError("The server closed the connection without a response.")

            try:
                response = json.loads(response_line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise EmailClientError("The server returned an invalid JSON response.") from error

            if not isinstance(response, dict) or not isinstance(response.get("ok"), bool):
                raise EmailClientError("The server response must contain a boolean 'ok' field.")
            if not response["ok"]:
                message = response.get("message", "The server rejected the request.")
                raise EmailClientError(str(message))

            return response.get("data", {})
        except EmailClientError:
            raise
        except (OSError, socket.timeout) as error:
            raise EmailClientError(
                f"Could not communicate with the email server at {self.host}:{self.port}. "
                "Check that the server is running and try again."
            ) from error