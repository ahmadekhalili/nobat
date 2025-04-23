
# native_host.py
import sys
import os
import json
import struct
import requests
import logging
log_file = os.path.join(os.path.dirname(__file__), 'app.log')

# تنظیم لاگر
logging.basicConfig(
    level=logging.DEBUG,  # یا INFO یا WARNING بسته به نیاز
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # برای نمایش در کنسول همزمان
    ]
)

# استفاده
logging.info('برنامه شروع شد')

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    logging.info(f"sys.stdin.buffer.read: {raw_length}")
    if len(raw_length) == 0:
        print("Chrome closed. Exiting.")

    message_length = struct.unpack('=I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)

def write_log(message):
    requests.get("http://127.0.0.1:8000/main/browser_close", json=message)

if __name__ == "__main__":
    try:
        while True:
            logging.info('read_message running:')
            message = read_message()

            if message is None:
                break

            print("Received message:", message)
    except Exception as e:
        print('error:', e)
        write_log({"status": "browser_closed @@@@"})
