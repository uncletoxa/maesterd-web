import json
import logging
import os
import signal
import socket
import threading
from typing import Any

from langchain_core.messages import HumanMessage
from maesterd.llm.graph import graph
from maesterd.constants import GRAPH_RECURSION_LIMIT

logger = logging.getLogger(__name__)


class MaesterdServer:
    def __init__(self, socket_path: str,
                 timeout: float = 30.0, buffer_size: int = 8192, mock_response: bool = False):
        self.socket_path = socket_path
        self.timeout = timeout
        self.buffer_size = buffer_size
        self.mock_response = mock_response
        self.sock = None
        self.running = False
        self._setup_logging()

    def _setup_logging(self):
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def _setup_socket(self):
        try:
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
        except OSError:
            if os.path.exists(self.socket_path):
                raise

        # Create socket directory if it doesn't exist
        os.makedirs(os.path.dirname(self.socket_path), exist_ok=True)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.bind(self.socket_path)

        # Set sockets permissions
        os.chmod(self.socket_path, 0o666)

    @staticmethod
    def _handle_prompt(data: dict[str, Any]) -> dict[str, Any]:
        try:
            prompt = data.get('prompt')
            if prompt is None:
                return {"error": "No prompt provided"}

            execution_config = {
                "recursion_limit": GRAPH_RECURSION_LIMIT,
                "configurable": {
                    "thread_id": data.get('thread_id', 'default')}}

            messages = [HumanMessage(content=prompt)]
            graph.update_state(
                config=execution_config,
                values={
                    'actor_prompts': [prompt],
                    "num_pc": data.get('num_pc', 1),})

            graph.invoke(
                input={'messages': messages, 'num_pc': data.get('num_pc', 1)},
                config=execution_config)

            # Get the last message content from the graph state
            state = graph.get_state(config=execution_config)
            last_message = state.values['messages'][-1].content

            return {"content": last_message,
                    "state": {
                        "name": state.values.get('name'),
                        "setting": state.values.get('setting'),
                        "goal": state.values.get('goal')}}

        except Exception as e:
            logger.exception("Error processing prompt")
            return {"error": str(e)}

    @staticmethod
    def _handle_health_check() -> dict[str, Any]:
        return {"status": "ok"}

    def _handle_client(self, client_sock: socket.socket):
        try:
            with client_sock:
                data = client_sock.recv(self.buffer_size).decode()
                if not data:
                    return

                try:
                    request = json.loads(data)
                except json.JSONDecodeError as e:
                    response = {"error": f"Invalid JSON: {str(e)}"}
                else:
                    request_type = request.get('type', 'prompt')
                    if request_type == 'health_check':
                        response = self._handle_health_check()
                    else:
                        if self.mock_response:
                            response = {"content": "content",
                                         "state": {
                                             "name": 'name',
                                             "setting": 'setting',
                                             "goal": 'goal'}}
                        else:
                            response = self._handle_prompt(request)

                client_sock.sendall(json.dumps(response).encode())

        except Exception as e:
            logger.exception(f"Error handling client connection: {e}")
        finally:
            client_sock.close()

    def serve_forever(self):
        self._setup_socket()
        self.running = True
        self.sock.listen(1)

        logger.info(f"Starting maesterd socket api on {self.socket_path}")

        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        try:
            while self.running:
                try:
                    client_sock, _ = self.sock.accept()

                    # Handle client in a new thread
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock,))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket accept error: {e}")
        finally:
            self.shutdown()

    def _shutdown_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()

    def shutdown(self):
        """Shutdown the api"""
        self.running = False
        if self.sock:
            self.sock.close()
            try:
                os.unlink(self.socket_path)
            except OSError:
                pass


def run_server(socket_path: str, *args, **kwargs):
    server = MaesterdServer(socket_path=socket_path, *args, **kwargs)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception("Server error")
        raise
