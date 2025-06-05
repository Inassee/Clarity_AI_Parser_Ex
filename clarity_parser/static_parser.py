import sys
from typing import Set
from datetime import datetime, timezone

def to_epoch(ts: str) -> int:
    dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def parse_file(path: str, t1: str, t2: str, host: str) -> list[str]:
    start, end = to_epoch(t1), to_epoch(t2)
    peers: Set[str] = set()

    with open(path, "r", encoding="utf-8") as fh:
        for ln in fh:
            try:
                ts, h1, h2 = ln.strip().split()
            except ValueError:
                continue
            ts_i = int(ts)
            if ts_i < start:
                continue
            if ts_i > end:
                break
            if h1 == host:
                peers.add(h2)
            elif h2 == host:
                peers.add(h1)
    return sorted(peers)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("usage: python -m clarity_parser.static_parser <log> <start> <end> <host>")
        sys.exit(1)
    file_, t_start, t_end, target = sys.argv[1:]
    out = parse_file(file_, t_start, t_end, target)
    print(out)
