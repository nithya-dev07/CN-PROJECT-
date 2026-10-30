import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--name", default="Server")
args = parser.parse_args()

HOST = "0.0.0.0"
content = (f"Content delivered by {args.name}\n" * 1000).encode()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, args.port))
server.listen(10)

print(f"{args.name} listening on port {args.port}", flush=True)

while True:
    conn, addr = server.accept()
    with conn:
        request = conn.recv(1024).decode(errors="replace").strip()
        print(f"{args.name}: request from {addr}: {request}", flush=True)
        conn.sendall(f"SERVER={args.name}\n".encode() + content)
