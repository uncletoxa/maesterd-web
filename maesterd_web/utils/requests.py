import socket
import json

from maesterd_web.settings import OPENAI_SOCKET_ADDR


class SocketRequestError(Exception):
    pass


def make_request(socket_path: str, request_data: dict, buffer_size: int = 8192) -> dict:
    """
    Make a request to a Unix socket with the given data.

    Args:
        socket_path: Path to the Unix socket
        request_data: Dictionary containing request data
        buffer_size: Socket buffer size in bytes

    Returns:
        Dictionary containing the response data

    Raises:
        SocketRequestError: If any error occurs during communication
    """
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(socket_path)

            sock.sendall(json.dumps(request_data).encode())

            chunks = []
            while True:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    break
                chunks.append(chunk)

            response = b''.join(chunks).decode()

            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                raise SocketRequestError(f"Invalid JSON response: {str(e)}")

    except socket.error as e:
        raise SocketRequestError(f"Socket error: {str(e)}")
    except Exception as e:
        raise SocketRequestError(f"Unexpected error: {str(e)}")