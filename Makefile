.PHONY: all lint test coverage e2e clean precommit test-fast test-full test-deep security mutation

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

# === Три категории тестов (как в проде; подробно — docs/testing_infrastructure.md) ===
# (1) Быстрый — каждый push: unit + integration + property + покрытие 90%.
test-fast:
	$(TEST_ENV) coverage run -m pytest -m fast
	coverage report -m

# (2) Полный — перед релизом/тегом: визуальная регрессия + live-a11y (нужен браузер).
#     Дополняется security и нагрузкой (locust) на уровне CI/локально.
test-full:
	python3 -m playwright install chromium
	$(TEST_ENV) pytest -m full

# (3) Глубокий — редко/вручную: стресс-property (тысячи примеров) + мутации.
test-deep:
	$(TEST_ENV) pytest -m deep

# Безопасность (полный тир): статанализ кода + аудит уязвимостей зависимостей.
security:
	pip install -q bandit pip-audit
	bandit -q -r app -ll
	pip-audit -r requirements.txt

# Мутационное тестирование (глубокий тир): проверяет силу самих тестов.
mutation:
	pip install -q mutmut
	mutmut run --paths-to-mutate app/core
	mutmut results
