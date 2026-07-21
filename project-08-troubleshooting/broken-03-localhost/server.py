import socket

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 5432))
server.listen()
while True:
    conn, _ = server.accept()
    conn.sendall(b"db-ready")
    conn.close()
