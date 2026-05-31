.PHONY: install models lint format typecheck test build clean

install:        ## install the package + dev tools (editable)
	pip install -e ".[dev]"

models:         ## regenerate the pydantic models from the OpenAPI snapshot
	python scripts/generate_models.py

lint:           ## lint with ruff
	ruff check src tests

format:         ## auto-format with ruff
	ruff format src tests

typecheck:      ## strict type-check (generated models excluded via pyproject)
	mypy -p trustat

test:           ## run the offline test suite
	pytest -q

build:          ## build wheel + sdist
	python -m build

clean:
	rm -rf dist build src/*.egg-info .pytest_cache .mypy_cache .ruff_cache
