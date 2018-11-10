.PHONY: help
help:
	cat makefile

.PHONY: clean
clean:
	find * -name '*.pyc' -delete
	find * -name __pycache__ -delete

.PHONY: test
test:
	flake8
	pytest -v -s --cov=cg_test --cov-report=term-missing .
