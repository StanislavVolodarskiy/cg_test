.PHONY: help
help:
	cat makefile

.PHONY: test
test:
	flake8
	pytest -v -s --cov=cg_test --cov-report=term-missing tests
