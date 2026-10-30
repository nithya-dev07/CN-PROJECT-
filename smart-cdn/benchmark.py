import csv
import socket
import time
from datetime import datetime

SERVERS = [
    ("Server1", "10.0.0.1", 8000),
    ("Server2", "10.0.0.2", 8000),
]
ROUNDS = 10
OUTPUT = "/home/sohan/smart-cdn/benchmark_results.csv"

with open(OUTPUT, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "timestamp", "round", "server", "ip",
        "bytes_received", "download_time_ms",
        "throughput_MiB_s", "status"
    ])

    for round_no in range(1, ROUNDS + 1):
        for name, host, port in SERVERS:
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
                size = sum(len(chunk) for chunk in chunks)
                throughput = size / elapsed / (1024 * 1024) if elapsed else 0

                writer.writerow([
                    datetime.now().isoformat(timespec="seconds"),
                    round_no, name, host, size,
                    round(elapsed * 1000, 2),
                    round(throughput, 3), "OK"
                ])
                print(
                    f"Round {round_no:02} | {name} | "
                    f"{elapsed * 1000:.2f} ms | {throughput:.3f} MiB/s"
                )

            except OSError as error:
                writer.writerow([
                    datetime.now().isoformat(timespec="seconds"),
                    round_no, name, host, 0, "", "", "FAILED"
                ])
                print(f"Round {round_no:02} | {name} | FAILED: {error}")

print(f"\nResults saved to {OUTPUT}")
