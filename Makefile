.PHONY: install test lint format clean build zip

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src/mrif --cov-report=term-missing

test-fast:
	pytest tests/ -v -x

lint:
	ruff check src/ tests/
	mypy src/mrif

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete
	rm -rf .coverage htmlcov/ dist/ build/ *.egg-info

build:
	pip install build
	python -m build

zip:
	zip -r mrif_project.zip . \
		--exclude "*.pyc" \
		--exclude "__pycache__/*" \
		--exclude ".git/*" \
		--exclude "*.db" \
		--exclude "dist/*" \
		--exclude "*.egg-info/*"
	@echo "Created mrif_project.zip"
