.PHONY: help install test clean lint format examples run-examples

help:
	@echo "AUTOSAR ARXML Merger - Verfügbare Befehle:"
	@echo ""
	@echo "  install         - Installiere Abhängigkeiten"
	@echo "  install-dev     - Installiere Entwicklungsabhängigkeiten"
	@echo "  test            - Führe Tests aus"
	@echo "  clean           - Bereinige Build-Artefakte"
	@echo "  lint            - Führe Code-Analyse aus"
	@echo "  format          - Formatiere Code"
	@echo "  examples        - Erstelle Beispieldateien"
	@echo "  run-examples    - Führe Beispiele aus"
	@echo "  build           - Baue Paket"
	@echo "  upload          - Lade Paket zu PyPI hoch"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

test:
	python -m pytest tests/ -v --cov=arxml_merger --cov-report=html --cov-report=term-missing

test-quick:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=arxml_merger --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

lint:
	flake8 arxml_merger/ tests/
	mypy arxml_merger/

format:
	black arxml_merger/ tests/ examples/

examples:
	mkdir -p examples
	@echo "Erstelle Beispieldateien..."

run-examples:
	python examples/example_usage.py

build:
	python -m build

build-wheel:
	python -m build --wheel

build-sdist:
	python -m build --sdist

upload:
	twine upload dist/*

# Hilfsbefehle für Entwicklung
dev-setup: install-dev
	@echo "Entwicklungsumgebung eingerichtet!"

quick-test:
	python -m pytest tests/test_merger.py::TestArxmlMerger::test_basic_merge -v

# Bereinigung verschiedener Dateitypen
clean-pyc:
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -type d -name __pycache__ -exec rm -rf {} +

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-test:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

clean-all: clean clean-pyc clean-build clean-test

# Dokumentation
docs:
	@echo "Generiere Dokumentation..."
	@echo "Siehe docs/README.md für vollständige Dokumentation"

# Validierung
validate:
	python -c "import arxml_merger; print('✓ Modul erfolgreich importiert')"
	python -c "from arxml_merger import ArxmlMerger; print('✓ ArxmlMerger importiert')"
	python -c "from arxml_merger import MergeConfig; print('✓ MergeConfig importiert')"
	python -c "from arxml_merger import ConflictResolutionStrategy; print('✓ ConflictResolutionStrategy importiert')"

# Vollständige Validierung
full-validate: validate lint test
	@echo "✓ Vollständige Validierung erfolgreich!"
