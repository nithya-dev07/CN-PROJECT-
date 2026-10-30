import socket
import time

SERVERS = [
    ("Server1", "10.0.0.1", 8000),
    ("Server2", "10.0.0.2", 8000),
]

def download_from_server(name, host, port):
    start = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=3) as sock:
            sock.settimeout(5)
            sock.sendall(b"GET content\n")

            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)

        elapsed = time.perf_counter() - start
        content = b"".join(chunks)
        size = len(content)
        throughput = size / elapsed / (1024 * 1024) if elapsed > 0 else 0

        return {
            "name": name,
            "host": host,
            "size": size,
            "elapsed": elapsed,
            "throughput": throughput,
        }

    except OSError as error:
        print(f"{name} ({host}) unavailable: {error}")
        return None

results = []

print("Measuring full-content delivery...\n")

for server in SERVERS:
    result = download_from_server(*server)
    if result:
        results.append(result)
        print(f"{result['name']} ({result['host']})")
        print(f"  Bytes received: {result['size']}")
        print(f"  Download time:  {result['elapsed'] * 1000:.2f} ms")
        print(f"  Throughput:     {result['throughput']:.3f} MiB/s\n")

if not results:
    print("No content servers are available.")
else:
    best = min(results, key=lambda item: item["elapsed"])
    print("Selected server:", best["name"])
    print("Server IP:", best["host"])
