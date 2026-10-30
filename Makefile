.PHONY: help dev test lint fix audit build install uninstall clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  dev        Create .venv with all deps (uv sync)"
	@echo "  test       Run the test suite"
	@echo "  lint       Run ruff checks"
	@echo "  fix        Apply ruff autofixes"
	@echo "  audit      Scan locked dependencies for known vulnerabilities"
	@echo "  build      Build sdist and wheel (output: dist/)"
	@echo "  install    Install the CLI globally as a uv tool"
	@echo "  uninstall  Remove the globally installed CLI"
	@echo "  clean      Remove build artifacts and caches"

dev:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix .

audit:
	uv export --no-dev --no-emit-project --format requirements.txt | uv run pip-audit --strict -r /dev/stdin --disable-pip

build:
	uv build

install:
	uv tool install --force .

uninstall:
	uv tool uninstall imgsort

clean:
	rm -rf dist/ build/ .pytest_cache/ .ruff_cache/
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
