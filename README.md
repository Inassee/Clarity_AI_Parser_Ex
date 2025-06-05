# Clarity – Data Operations Engineer Code Challenge

**Python utility for ESG-style connection logs**:  
1. Static range queries  
2. Live monitor  
3. Streamlit UI

**Production link**  
[https://clarity-parser-app.streamlit.app](https://clarity-parser-app.streamlit.app)

---

## Install

```bash
python -m venv venv && source venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

---

## Command-line examples

**Static query:**
```bash
python -m clarity_parser.static_parser Optional-connections.log "2024-01-01 00:00:00" "2024-12-31 23:59:59" host80
```

**Live monitor:**
```bash
python -m clarity_parser.streaming_parser Optional-connections.log host80
```

---

## Layout

```
clarity_parser/             → core library
  ├─ static_parser.py       → static log parser
  └─ streaming_parser.py    → live log monitor
streamlit_app.py            → one-page web UI
Optional-connections.log    → 10000 line sample log
requirements.txt            → dependencies
```

---

<sub>Created by <strong>Inasse Tyouss</strong> for <strong>Clarity AI</strong></sub>
