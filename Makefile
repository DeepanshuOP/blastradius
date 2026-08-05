.PHONY: test tables figures all

test:
	uv run pytest -q

tables:
	@echo "not implemented"

figures:
	@echo "not implemented"

all: test
