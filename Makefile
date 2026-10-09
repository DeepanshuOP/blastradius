.PHONY: test tables resolve-bases fetch-base-logs figures all reproduce check-log-isolation demo demo-data demo-web agents-demo analyze

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

# BR_OFFLINE=1 makes get_with_backoff() raise before any socket is opened, so a
# step that gains a network call fails loudly instead of silently fetching.
tables: export BR_OFFLINE=1
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
	# The base-log fetch is deliberately NOT a step here (D-49): it needs the
	# network and a PAT. `make tables` makes no network call, whatever the env.
	uv run python analysis/capture_stdout.py base_log_parse.md "Base-log parse" analysis/parse_base_logs.py
	uv run python analysis/capture_stdout.py labelling_run.md "Labelling run" src/label/fault_revealing.py
	uv run python analysis/fixture_score.py
	uv run python analysis/holdout_eval.py
	uv run python analysis/parser_precision_table.py
	uv run python analysis/capture_stdout.py binding_run.md "Binding run" analysis/binding_report.py
	uv run python analysis/paper_numbers.py
	uv run python analysis/attrition_funnel.py
	uv run python analysis/rq1_divergence.py
	uv run python analysis/leakage_audit.py
	uv run python analysis/infra_failure_audit.py
	# The exact_green sweep itself needs PATs and runs for tens of minutes, so
	# it is an explicit step (`uv run --env-file .env python
	# analysis/verify_exact_green.py`), not part of `tables`. What `tables`
	# regenerates is every NUMBER derived from its committed output.
	uv run python analysis/capture_stdout.py exact_green_report.md "exact_green verification report" analysis/verify_exact_green.py --report-only
	uv run python analysis/capture_stdout.py --note "The evidence-only and invariant-6 scenarios below are counterfactuals, not the committed corpus." corpus_delta.md "Corpus delta" analysis/corpus_delta.py
	uv run python analysis/expiry_cliff.py
	uv run python analysis/annotation_census.py
	uv run python analysis/corpus_stats.py


# Explicit, network-bound, NOT part of `tables` (it was, until D-50's round; it
# needs a PAT and the network, and rewrites base_resolution_new.parquet, which
# every downstream figure derives from). Needs GITHUB_PAT_1/_2/_3.
resolve-bases:
	@if [ -z "$$GITHUB_PAT_1" ] && [ -z "$$GITHUB_PAT_2" ] && [ -z "$$GITHUB_PAT_3" ]; then \
		echo "resolve-bases: needs GITHUB_PAT_1/_2/_3 in the environment" >&2; \
		exit 1; \
	fi
	uv run python analysis/resolve_bases.py

# Explicit, network-bound, NOT part of `tables`. The corpus is pinned
# (data/interim/CORPUS_PIN.json); fetching further base logs moves it, so this
# is an operator decision. The gate names every key TokenPool accepts
# (src/harvest/ratelimit.py DEFAULT_ENV_KEYS).
fetch-base-logs:
	@if [ -z "$$GITHUB_PAT_1" ] && [ -z "$$GITHUB_PAT_2" ] && [ -z "$$GITHUB_PAT_3" ]; then \
		echo "fetch-base-logs: needs GITHUB_PAT_1/_2/_3 in the environment" >&2; \
		exit 1; \
	fi
	uv run python analysis/fetch_base_logs.py

# Read-only, offline, deterministic walkthrough of one strict instance. A graph
# missing from data/graphs/ is built into a temp dir from local git objects.
demo:
	GIT_NO_LAZY_FETCH=1 uv run --extra graph python analysis/demo_walkthrough.py

# Recorded demo runs for the static site: the walkthrough's gates, offline graph
# build and RQ1's k=10 predictors, written as JSON to demo-web/public/data/ (the
# only output). Headline numbers are parsed from paper/generated/*.md.
# The five-agent workflow (D-55) on the bundled shopcart sample repo, three
# recorded scenarios, fully offline (no LLM, local forge). Writes the replay the
# demo site's Agents tab shows. Not part of `tables`: nothing here is a paper number.
agents-demo:
	BR_OFFLINE=1 uv run --extra graph python -m src.agents demo --export demo-web/public/data/agents.json

demo-data:
	GIT_NO_LAZY_FETCH=1 uv run --extra graph python analysis/export_demo_data.py

# Static Next.js replay of demo-data on http://localhost:3000 (needs Node >= 18
# and `npm ci` in demo-web/ once). No Python server, no runtime network calls.
demo-web:
	cd demo-web && npm run build && npm start

# CLI twin of the demo site's "Analyze a repo" tab: shallow-clone a public GitHub
# repo (Python or Java) into $$TMPDIR/br-analyze/<owner>__<repo> (reused if present)
# and run the offline Impact Analysis Agent on it. No LLM, no token.
#   make analyze REPO=https://github.com/pallets/itsdangerous STORY="..." [BRANCH=main]
analyze:
	@echo "$(REPO)" | grep -Eq '^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$$' \
		|| { echo 'usage: make analyze REPO=https://github.com/<owner>/<repo> STORY="..." [BRANCH=<branch>]' >&2; exit 2; }
	@test -n "$(STORY)" || { echo 'analyze: STORY="..." is required' >&2; exit 2; }
	@dir="$${TMPDIR:-/tmp}/br-analyze/$$(echo '$(REPO)' | sed -E 's#^https://github.com/##; s#\.git$$##; s#/#__#')$(if $(BRANCH),__$(BRANCH))"; \
	[ -d "$$dir/.git" ] || GIT_TERMINAL_PROMPT=0 timeout 120 git clone --quiet --depth 50 $(if $(BRANCH),--branch $(BRANCH)) '$(REPO)' "$$dir" || exit 1; \
	timeout 180 uv run --extra graph python -m src.agents impact --repo "$$dir" --story '$(STORY)' --provider offline \
		&& echo "impact.md and impact.json: $$dir/.blastradius/impact/"

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
