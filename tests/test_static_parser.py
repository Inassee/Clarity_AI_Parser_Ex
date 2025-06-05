from pathlib import Path
from clarity_parser.static_parser import parse_file

LOG = """\
1704069933 host2 host80
1704070333 host14 host80
1704071000 host80 host35
"""

def test_window(tmp_path: Path):
    p = tmp_path / "log"
    p.write_text(LOG)

    res = parse_file(
        path=str(p),
        t1="2024-01-01 00:00:00",
        t2="2024-01-01 01:10:00",
        host="host80",
    )
    assert set(res) == {"host2", "host14", "host35"}
