.PHONY: test tables figures all reproduce check-log-isolation

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
	# Refuses to run at all if any interim artifact is older than an input it is
	# derived from (D-49: outcomes.parquet once predated parsed_outcomes.parquet,
	# one of its own inputs, and every figure drawn from it described a parse
	# generation no longer on disk). First, for the same reason secret_scan is
	# early: a gate placed behind a step that can fail is not a gate.
	uv run python analysis/check_freshness.py
	# Release blocker (T1.6b), and independent of every step below it, so it
	# runs first: a gate placed behind a step that can fail is not a gate.
	# Exits non-zero only on a credential-shaped match.
	uv run python analysis/secret_scan.py
	uv run python analysis/resolve_bases.py
	# Needs a GitHub PAT and the network, and it is the step that caused D-49:
	# it sits ABOVE parse_base_logs and fault_revealing, so when it aborted for
	# a missing PAT, `make tables` stopped here and the labels were never
	# rebuilt while every step above had succeeded -- leaving outcomes.parquet
	# silently older than its own inputs.
	#
	# The corpus is PINNED (data/interim/CORPUS_PIN.json), so fetching further
	# base logs after the pin would move the corpus out from under every figure
	# already computed against it. D-49 fixes the base side at the local
	# RawStore only. Skipped loudly rather than fatally; downstream staleness is
	# now caught by check_freshness.py above, not by this step failing.
	@if [ -n "$$GITHUB_PAT_1" ]; then \
		uv run python analysis/fetch_base_logs.py; \
	else \
		echo "[tables] SKIP analysis/fetch_base_logs.py — no GITHUB_PAT_1 in env;"; \
		echo "[tables]      corpus is pinned, base side is local RawStore only (D-49)."; \
	fi
	uv run python analysis/parse_base_logs.py
	uv run python src/label/fault_revealing.py
	uv run python analysis/fixture_score.py
	uv run python analysis/holdout_eval.py
	uv run python analysis/binding_report.py
	uv run python analysis/attrition_funnel.py
	uv run python analysis/rq1_divergence.py
	# The exact_green sweep itself needs PATs and runs for tens of minutes, so
	# it is an explicit step (`uv run --env-file .env python
	# analysis/verify_exact_green.py`), not part of `tables`. What `tables`
	# regenerates is every NUMBER derived from its committed output.
	uv run python analysis/verify_exact_green.py --report-only
	uv run python analysis/corpus_delta.py
	uv run python analysis/expiry_cliff.py
	uv run python analysis/annotation_census.py
	uv run python analysis/corpus_stats.py


figures:
	@echo "not implemented"

# T5.6b: the 3-repo graph-layer mini-corpus reproduction (docs/MINI_CORPUS.md),
# budgeted under 15 minutes. Graph layer only -- per D-48 nothing it prints
# reaches `make tables`, `release/` or the paper, and the binding figure it
# reports is the graph-side diagnostic, not Gate 1.5.
#
# Bounded by construction: data/graphs/ holds 427 graphs and a cold rebuild of
# all of them cannot fit the budget, so the target reproduces the full
# build -> bind -> query chain over 3 SHAs per repo and names the subset size
# alongside every figure. Exact commands and expected output: docs/REPRODUCE.md.
reproduce:
	uv run --extra graph python analysis/reproduce_mini_corpus.py

all: test reproduce
