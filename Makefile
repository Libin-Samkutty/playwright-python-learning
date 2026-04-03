# Makefile for Playwright test automation

.PHONY: help install test smoke regression parallel clean report

# Default target
help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run all tests"
	@echo "  make smoke       - Run smoke tests"
	@echo "  make regression  - Run regression tests"
	@echo "  make parallel    - Run tests in parallel"
	@echo "  make clean       - Clean artifacts and reports"
	@echo "  make report      - Generate and open report"

# Install dependencies
install:
	pip install -r requirements.txt
	playwright install chromium

# Install all browsers
install-all-browsers:
	playwright install

# Run all tests
test:
	pytest tests/ -v

# Run smoke tests
smoke:
	pytest tests/ -m smoke -v

# Run regression tests
regression:
	pytest tests/ -m regression -v

# Run tests in parallel
parallel:
	pytest tests/ -n auto -v

# Run with specific environment
test-staging:
	PLAYWRIGHT_ENV=staging pytest tests/ -v

test-ci:
	PLAYWRIGHT_ENV=ci pytest tests/ -n 4 --html=reports/html/report.html --alluredir=reports/allure-results -v

# Clean artifacts and reports
clean:
	rm -rf artifacts/
	rm -rf reports/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Generate Allure report
allure-report:
	allure generate reports/allure-results -o reports/allure-report --clean

# Serve Allure report
allure-serve:
	allure serve reports/allure-results

# Open HTML report
open-report:
	open reports/html/report.html || xdg-open reports/html/report.html

# Generate and open report
report: allure-report
	allure open reports/allure-report

# Run tests with coverage
coverage:
	pytest tests/ --cov=pages --cov=utils --cov-report=html

# Lint code
lint:
	flake8 pages/ tests/ utils/ config/
	mypy pages/ tests/ utils/ config/

# Format code
format:
	black pages/ tests/ utils/ config/
	isort pages/ tests/ utils/ config/

# Full CI pipeline
ci: clean
	@echo "Running CI pipeline..."
	PLAYWRIGHT_ENV=ci pytest tests/ \
		-n 4 \
		--html=reports/html/report.html \
		--self-contained-html \
		--alluredir=reports/allure-results \
		-v \
		--tb=short
	@echo "Generating Allure report..."
	allure generate reports/allure-results -o reports/allure-report --clean || true
	@echo "CI pipeline completed."