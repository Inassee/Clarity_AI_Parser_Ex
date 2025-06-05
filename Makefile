install:
	pip install -e .

test:
	pytest -q

run-part1:
	python -m clarity_parser.static_parser Optional-connections.log "2024-01-01 00:00:00" "2024-02-01 00:00:00" host80

run-part2:
	python -m clarity_parser.streaming_parser Optional-connections.log host80
