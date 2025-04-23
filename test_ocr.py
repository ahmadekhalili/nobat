
# native_host.py
import sys
import json
import struct
import requests

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        return None
    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

def write_log(message):
    requests.get("http://127.0.0.1:8000/browser-close", json=message)

if __name__ == "__main__":
    try:
        while True:
            message = read_message()
            if message is None:
                break
            print("Received message:", message)
    except Exception as e:
        write_log({"status": "browser_closed @@@@"})
