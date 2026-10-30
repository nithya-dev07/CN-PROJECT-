import socket
import time

SERVERS = [
    ("Server1", "10.0.0.1", 8000),
    ("Server2", "10.0.0.2", 8000),
]

def measure_server(name, host, port):
    start = time.perf_counter()

    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.settimeout(5)
            sock.sendall(b"GET content\n")
            data = sock.recv(1024)

        elapsed = (time.perf_counter() - start) * 1000
        return {
            "name": name,
            "host": host,
            "port": port,
            "latency_ms": elapsed,
            "response": data.decode(errors="replace").splitlines()[0],
        }
    except OSError as exc:
        print(f"{name} unavailable: {exc}")
        return None

results = []
print("Checking server availability and response time...\n")

for server in SERVERS:
    result = measure_server(*server)
    if result:
        results.append(result)
        print(f"{result['name']} ({result['host']}): "
              f"{result['latency_ms']:.2f} ms")

if not results:
    print("\nNo content servers are available.")
else:
    selected = min(results, key=lambda item: item["latency_ms"])
    print(f"\nSelected server: {selected['name']}")
    print(f"Server IP: {selected['host']}")
    print(f"Response time: {selected['latency_ms']:.2f} ms")
