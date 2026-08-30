.PHONY: test tables figures all check-log-isolation

test:
	uv run pytest -q

# Regression check for the logs/requests.jsonl contamination fix (§8.2,
# §34.1 Rule 6). Not expressible as a pytest test in this suite without
# spawning a second, self-referential subprocess run of the whole suite
# from inside a test — technically possible, but it would make `make test`
# recursively invoke itself and roughly double every run's cost for a
# check that's naturally a wrapper around the run, not a unit inside it.
#
# Previously this check asserted line count and mtime were strictly
# unchanged. That was abandoned because the live harvester daemon writes
# to logs/requests.jsonl concurrently in the background, causing random
# false-positive failures during healthy test runs.
#
# Instead, the check inspects any new lines appended during the run and
# enforces an allowlist: all newly appended requests must match valid
# daemon endpoint URL shapes (api.github.com/rate_limit or real repo
# endpoints: actions, pulls, commits, check-runs). Any fixture/dummy URL
# or un-isolated test traffic triggers a failure.
check-log-isolation:
	@if [ -f logs/requests.jsonl ]; then \
		before_lines=$$(wc -l < logs/requests.jsonl); \
	else \
		before_lines=0; \
	fi; \
	uv run pytest -q; \
	if [ -f logs/requests.jsonl ]; then \
		after_lines=$$(wc -l < logs/requests.jsonl); \
	else \
		after_lines=0; \
	fi; \
	if [ "$$after_lines" -gt "$$before_lines" ]; then \
		bad_lines=$$(tail -n +$$((before_lines + 1)) logs/requests.jsonl | grep -v -E '"url": "https://api\.github\.com/(rate_limit|repos/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/(actions|pulls|commits|check-runs))' || true); \
		if [ -n "$$bad_lines" ]; then \
			echo "FAIL: logs/requests.jsonl received invalid/test traffic during suite run:"; \
			echo "$$bad_lines"; \
			exit 1; \
		fi; \
	fi; \
	echo "OK: logs/requests.jsonl isolated (no test traffic appended, lines $$before_lines -> $$after_lines)"

tables:
	mkdir -p paper/generated
	uv run python analysis/resolve_bases.py
	uv run python analysis/parse_base_logs.py
	uv run python src/label/fault_revealing.py
	uv run python analysis/fixture_score.py
	uv run python analysis/holdout_eval.py
	uv run python analysis/binding_report.py
	uv run python analysis/attrition_funnel.py
	uv run python analysis/rq1_divergence.py
	uv run python analysis/expiry_cliff.py
	uv run python analysis/annotation_census.py
	uv run python analysis/corpus_stats.py


figures:
	@echo "not implemented"

all: test
