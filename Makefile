.PHONY: all lint test coverage e2e clean precommit

PYTHON=python3
TEST_ENV=SECRET_KEY=test-secret-key-for-ci

# === Линтеры (точь-в-точь набор курса: mypy + flake8 + pylint) ===
lint:
	rm -rf .mypy_cache
	$(PYTHON) -m mypy app --config-file=.mypy.ini
	flake8 .
	pylint app --rcfile=.pylintrc

# === Тесты + покрытие (coverage, порог из .coveragerc = 90%) ===
test:
	$(TEST_ENV) coverage run -m pytest
	coverage report -m
	coverage html

# Алиас для CI-совместимого прогона без html
coverage:
	$(TEST_ENV) coverage run -m pytest
	coverage report -m

all: lint test

precommit:
	pre-commit run --all-files

clean:
	find . -name "*.pyc" -delete
	rm -rf .mypy_cache __pycache__ htmlcov .pytest_cache .coverage

# === Браузерные E2E (Playwright) — отдельно, требуют браузер ===
e2e:
	python3 -m playwright install chromium
	pytest -m e2e
