import os
import socket
import time

host = os.getenv("DB_HOST", "localhost")
while True:
    try:
        with socket.create_connection((host, 5432), timeout=2) as conn:
            print(conn.recv(32).decode(), flush=True)
    except Exception as exc:
        print(f"cannot connect to {host}:5432: {exc}", flush=True)
    time.sleep(3)
