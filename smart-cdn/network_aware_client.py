import json
import socket
import time
import os

SERVERS = [
    ("Server1", "10.0.0.1", 8000, [1]),
    ("Server2", "10.0.0.2", 8000, [2]),
]

STATS_FILE = "/home/sohan/smart-cdn/port_stats.json"


def get_network_load():
    try:
        with open(STATS_FILE) as f:
            stats = json.load(f)

        ports = stats.get("ports", {})
        total_rate = sum(
            p.get("rx_bytes_per_sec", 0) +
            p.get("tx_bytes_per_sec", 0)
            for p in ports.values()
        )
        return total_rate
    except (OSError, ValueError, TypeError):
        return None


def test_server(name, host, port):
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=2) as sock:
            sock.settimeout(5)
            sock.sendall(b"GET content\n")
            response = sock.recv(1024)

        latency = (time.perf_counter() - start) * 1000
        return latency, response.decode(errors="replace").splitlines()[0]
    except OSError as e:
        print(f"{name} unavailable: {e}")
        return None


print("Reading Ryu network statistics...")
load = get_network_load()

if load is None:
    print("Warning: statistics file unavailable; using response time only.")
else:
    print(f"Observed aggregate switch-port traffic rate: {load:.2f} bytes/s")

print("\nTesting available content servers...")
results = []

for name, host, port, ports in SERVERS:
    result = test_server(name, host, port)
    if result:
        latency, identity = result
        results.append({
            "name": name,
            "host": host,
            "latency": latency,
            "identity": identity,
        })
        print(f"{name} ({host}): {latency:.2f} ms")

if not results:
    print("\nNo content servers are available.")
else:
    selected = min(results, key=lambda x: x["latency"])
    print(f"\nSelected server: {selected['name']}")
    print(f"Server IP: {selected['host']}")
    print(f"Response time: {selected['latency']:.2f} ms")
    print("\nSelection uses measured response time and availability.")
    print("Controller statistics are currently reported as network context.")
