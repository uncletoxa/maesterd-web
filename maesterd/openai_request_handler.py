import logging
import socket
import os
import json
from openai import OpenAI, OpenAIError
import requests.exceptions

SOCKET_PATH = "/tmp/sockets/openai_service.sock"


def handle_openai_request(prompt, api_key):
    try:
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a dungeons and dragons role play game master"},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )
        return {"content": completion.choices[0].message.content}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection error. Please check your internet connection"}
    except OpenAIError as openai_error:
        if "invalid_api_key" in str(openai_error).lower():
            return {"error": "Invalid OpenAI API key. Please check your API key and try again"}
        elif "rate_limit" in str(openai_error).lower():
            return {"error": "Rate limit exceeded. Please wait a moment before trying again"}
        else:
            return {"error": f"OpenAI API error: {str(openai_error)}"}
    except Exception as e:
        return {"error": f"Unexpected error in OpenAI request: {str(e)}"}


def start_server():
    os.makedirs(os.path.dirname(SOCKET_PATH), exist_ok=True)
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)

    logging.info(f"OpenAI service listening on {SOCKET_PATH}")

    while True:
        conn, _ = server.accept()
        try:
            with conn:
                data = conn.recv(1024).decode()
                request = json.loads(data)
                logging.info(f"Request received: {data}")

                response = json.dumps(handle_openai_request(request["prompt"], request["api_key"]))
                logging.info(f"Response received: {response}")
                conn.send(response.encode())

        except json.JSONDecodeError:
            conn.send(json.dumps({"error": "Invalid request format"}).encode())
        except Exception as e:
            conn.send(json.dumps({"error": f"Server error: {str(e)}"}).encode())


if __name__ == "__main__":
    start_server()
