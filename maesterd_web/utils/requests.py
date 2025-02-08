import socket
import json


class SocketRequestError(Exception):
    pass


def make_request(prompt, api_key):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect("/tmp/sockets/openai_service.sock")

            request_data = {"prompt": ':::,' + prompt, "api_key": api_key}
            sock.send(json.dumps(request_data).encode())

            response = sock.recv(4096).decode()  #  4 KiB buffer size
            response_data = json.loads(response)

            if response_data.get("error"):
                raise SocketRequestError(response_data["error"])
            return response_data["content"]

    except ConnectionRefusedError:
        raise SocketRequestError("OpenAI service is not running")
    except Exception as e:
        raise SocketRequestError(f"Socket communication error: {str(e)}") from e
