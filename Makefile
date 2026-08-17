.PHONY: test tables figures all check-log-isolation

test:
	uv run pytest -q

# Regression check for the logs/requests.jsonl contamination fix (§8.2,
# §34.1 Rule 6). Not expressible as a pytest test in this suite without
# spawning a second, self-referential subprocess run of the whole suite
# from inside a test — technically possible, but it would make `make test`
# recursively invoke itself and roughly double every run's cost for a
# check that's naturally a wrapper around the run, not a unit inside it.
# A Makefile target says the same thing more plainly: run the suite, prove
# the one file it must never touch didn't move.
check-log-isolation:
	@if [ -f logs/requests.jsonl ]; then \
		before_lines=$$(wc -l < logs/requests.jsonl); \
		before_mtime=$$(stat -c %Y logs/requests.jsonl); \
	else \
		before_lines=0; before_mtime=0; \
	fi; \
	uv run pytest -q; \
	if [ -f logs/requests.jsonl ]; then \
		after_lines=$$(wc -l < logs/requests.jsonl); \
		after_mtime=$$(stat -c %Y logs/requests.jsonl); \
	else \
		after_lines=0; after_mtime=0; \
	fi; \
	if [ "$$before_lines" != "$$after_lines" ] || [ "$$before_mtime" != "$$after_mtime" ]; then \
		echo "FAIL: logs/requests.jsonl changed (lines $$before_lines -> $$after_lines, mtime $$before_mtime -> $$after_mtime) — a test wrote to the real request log"; \
		exit 1; \
	fi; \
	echo "OK: logs/requests.jsonl unchanged (lines=$$before_lines, mtime=$$before_mtime) after running the suite"

tables:
	mkdir -p paper/generated
	uv run python analysis/attrition_funnel.py
	uv run python analysis/expiry_cliff.py


figures:
	@echo "not implemented"

all: test
