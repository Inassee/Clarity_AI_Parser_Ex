# Install dependencies
install:
	pip install -r requirements.txt

# Run part1 (static) parser
run-part1:
	python log_parser_all_in_one.py Optional-connections.log "2024-01-01 00:00:00" "2024-02-01 00:00:00" host80

# Run part2 (streaming) parser with default 1-hour window
run-part2:
	python streaming_parser.py Optional-connections.log host80

# Unit tests
test:
	pytest -q
