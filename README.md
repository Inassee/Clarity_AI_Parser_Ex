### Instalación
python -m venv venv
source venv/Scripts/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

### Test unitario
pytest -q

### Uso – parte 1
python -m clarity_parser.log_parser_all_in_one Optional-connections.log "2024-01-01 00:00:00" "2024-02-01 00:00:00" host80

### Uso – parte 2 (streaming)
python -m clarity_parser.streaming_parser Optional-connections.log host80
