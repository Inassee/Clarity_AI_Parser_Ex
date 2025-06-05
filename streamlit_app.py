import streamlit as st, time, queue, threading, tempfile, pathlib, os, itertools
from datetime import datetime, timezone
from collections import Counter, deque
from clarity_parser.static_parser import parse_file
from clarity_parser.streaming_parser import parse_line

ACCENT, BG, CARD = "#3B82F6", "#0E1117", "#11151f"
st.set_page_config("Clarity AI • Log Parser", "🔍", "wide")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
* {{font-family:'Inter',sans-serif;color:#E5E7EB;}}
body {{background:{BG};}}
a,.stButton>button {{background:{ACCENT}!important;color:#fff!important;
  border:none;border-radius:12px;padding:10px 26px;font-weight:600;transition:.25s}}
a:hover,.stButton>button:hover{{filter:brightness(1.1);transform:translateY(-3px)}}
.card{{background:{CARD};border-radius:12px;padding:28px;box-shadow:0 4px 16px #0006}}
.card:hover{{transform:translateY(-4px);transition:.25s}}
.pill{{background:#1E2739;border-radius:9999px;padding:4px 14px;display:inline-block}}
.fade{{transition:all .3s ease-in-out}}
</style>""", unsafe_allow_html=True)

def _first_ts(p: str):
    with open(p) as f:
        for ln in itertools.islice(f, 200):
            if ln and ln.split()[0].isdigit():
                return int(ln.split()[0])
    return 0
def _last_ts(p: str, chunk=4096):
    with open(p, "rb") as f:
        f.seek(0, os.SEEK_END); pos=f.tell()
        buff=b""
        while pos>0:
            step=min(chunk,pos); pos-=step; f.seek(pos)
            buff=f.read(step)+buff
            if buff.count(b"\n")>3: break
        for ln in reversed(buff.splitlines()):
            if ln and ln.split()[0].isdigit():
                return int(ln.split()[0])
    return 0
def scan_range(p:str):
    return (_first_ts(p), _last_ts(p))

st.markdown(f"""
<div style="text-align:center;padding:90px 16px;
 background:linear-gradient(135deg,{BG} 0%,#1E2739 100%);">
 <h1 style="font-size:3rem;font-weight:600;margin-bottom:12px">🔍 Log Analyzer</h1>
 <p style="opacity:.8;max-width:620px;margin:auto">
  Upload a connection log, choose a window, get instant insights.</p><br>
 <span style="font-size:.9rem;opacity:.72;display:inline-flex;align-items:center;gap:6px">
   Created by <b>Inasse Tyouss</b> for
   <img src="logo.png" style="height:24px;border-radius:4px"> <b>Clarity AI</b>
 </span><br><br>
 <a href="#demo">Get started</a>
</div>
""", unsafe_allow_html=True)

st.markdown("### 1️⃣ Upload log file")
uploaded = st.file_uploader("Drop .log / .txt", type=["log","txt"])
if uploaded:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(uploaded.read()); tmp.close()
    log_path = tmp.name
else:
    log_path = "Optional-connections.log"
st.markdown(f"<span class='pill'>Using: {pathlib.Path(log_path).name}</span>",
            unsafe_allow_html=True)

lo, hi = scan_range(log_path)
def_start = datetime.fromtimestamp(lo, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if lo else ""
def_end   = datetime.fromtimestamp(hi, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if hi else ""
default_window = min(max(300, int(time.time())-hi+60), 86400) if hi else 3600  # 5 min–24 h

tab_static, tab_live = st.tabs(["🔎 Static", "📈 Live"])
with tab_static:
    st.markdown("### 2️⃣ Static query")
    c1,c2,c3 = st.columns(3)
    start = c1.text_input("Start UTC", def_start)
    end   = c2.text_input("End UTC"  , def_end)
    host  = c3.text_input("Host",      "host80")
    if st.button("Run query"):
        with st.spinner("Scanning…"):
            peers = parse_file(log_path, start, end, host)
        st.success(f"{len(peers)} peers")
        st.markdown(f"<div class='card'>{peers}</div>", unsafe_allow_html=True)
with tab_live:
    st.markdown("### 3️⃣ Live monitor")
    col1,col2 = st.columns(2)
    window  = col1.slider("Window s", 60, 86400, default_window, 60)
    refresh = col2.slider("Refresh s", 1, 30, 5)
    live_host = st.text_input("Track host", "host80")
    run = st.toggle("Start / stop"); live_out = st.empty()
    def tail(fp:pathlib.Path, q:queue.Queue):
        pos, ring = 0, deque()
        while run:
            fp.seek(pos)
            for ln in fp:
                rec = parse_line(ln)
                if rec: ring.append(rec)
            pos = fp.tell()
            logical_now = max(time.time(), ring[-1][0] if ring else 0)
            cutoff = logical_now - window
            while ring and ring[0][0] < cutoff: ring.popleft()
            cnt = Counter()
            inc = out = []
            for ts, src, dst in ring:
                cnt[src]+=1
            inc = sorted({src for ts, src, dst in ring if dst==live_host})
            out= sorted({dst for ts, src, dst in ring if src==live_host})
            top = cnt.most_common(1)[0][0] if cnt else "—"
            q.put((len(ring), inc, out, top))
            time.sleep(refresh)

    if run:
        q=queue.Queue(); fh=open(log_path, "r", encoding="utf-8")
        threading.Thread(target=tail,args=(fh,q),daemon=True).start()
        while run:
            if not q.empty():
                size,inc,out,top = q.get()
                live_out.markdown(f"""
                  <div class='card fade'>
                   <span class='pill'>Lines {size}</span><br><br>
                   <b>Incoming → {live_host}</b><br>{inc}<br><br>
                   <b>Outgoing ← {live_host}</b><br>{out}<br><br>
                   <b>Top speaker:</b> {top}
                  </div>""", unsafe_allow_html=True)
            time.sleep(.1)
    else:
        live_out.info("Toggle **Start** to begin monitoring.")

st.markdown("---"); st.markdown("### 🛠️ Developer corner")
st.code(
"from clarity_parser.static_parser import parse_file\n"
"peers = parse_file('log.txt','2024-01-01 00:00:00','2024-01-02 00:00:00','host80')\n"
"print(peers)", language="python")
st.markdown(
f"<a class='btn' href='https://github.com/your_org/clarity-parser' target='_blank'>GitHub repo</a>",
unsafe_allow_html=True)
