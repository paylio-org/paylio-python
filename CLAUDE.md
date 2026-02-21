# paylio-python

## Changed-Scope Checks (mandatory before every commit)
- `pip install -e ".[dev]"` (if deps changed)
- `pytest -q`
- `ruff check src/ tests/`
- `black --check src/ tests/`
- `mypy src/`
