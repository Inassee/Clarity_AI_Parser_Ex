import sys, time, argparse
from collections import deque, Counter
from pathlib import Path

def parse_line(txt: str):
    p = txt.split()
    if len(p) != 3:
        return None
    try:
        return int(p[0]), p[1], p[2]
    except ValueError:
        return None

def main() -> None:
    cli = argparse.ArgumentParser(description="Unlimited Input Parser")
    cli.add_argument("file", help="log file path")
    cli.add_argument("host", help="host to track")
    cli.add_argument("-w", "--window", type=int, default=3600,
                     help="window seconds (default 3600)")
    cli.add_argument("-p", "--poll", type=int, default=1,
                     help="disk poll seconds")
    args = cli.parse_args()

    buf = deque()
    last_pos = 0
    latest_ts_seen = 0

    def next_full_hour(ts: int) -> int:
        return (ts // 3600 + 1) * 3600

    logical_now = int(time.time())
    next_report = next_full_hour(logical_now)

    path = Path(args.file)

    with path.open("r", encoding="utf-8") as fh:
        while True:
            fh.seek(last_pos)
            for line in fh:
                rec = parse_line(line)
                if rec:
                    buf.append(rec)
                    latest_ts_seen = max(latest_ts_seen, rec[0])
            last_pos = fh.tell()

            real_now = int(time.time())
            if real_now - latest_ts_seen > 60:
                logical_now = latest_ts_seen
            else:
                logical_now = real_now

            cutoff = logical_now - args.window
            while buf and buf[0][0] < cutoff:
                buf.popleft()

            # ───── hourly report
            if logical_now >= next_report:
                inc, out = set(), set()
                cnt = Counter()
                for ts, src, dst in buf:
                    cnt[src] += 1
                    if dst == args.host:
                        inc.add(src)
                    if src == args.host:
                        out.add(dst)
                top = cnt.most_common(1)[0][0] if cnt else "—"

                t0 = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.gmtime(next_report-args.window))
                t1 = time.strftime("%Y-%m-%d %H:%M:%S",
                                   time.gmtime(next_report))
                print(f"\n[{t0} – {t1}]")
                print(f"Incoming → {args.host}: {sorted(inc)}")
                print(f"Outgoing ← {args.host}: {sorted(out)}")
                print(f"Most active host: {top}")
                next_report = next_full_hour(logical_now)

            time.sleep(args.poll)

if __name__ == "__main__":
    main()
