import socket
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True)
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--request", default="GET content")
args = parser.parse_args()

start = time.perf_counter()

try:
    with socket.create_connection((args.host, args.port), timeout=5) as sock:
        sock.sendall((args.request + "\n").encode())

        chunks = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)

    response = b"".join(chunks)
    elapsed = time.perf_counter() - start

    print(response[:150].decode(errors="replace"))
    print(f"Bytes received: {len(response)}")
    print(f"Response time: {elapsed * 1000:.2f} ms")

except OSError as e:
    print(f"Request failed: {e}")
