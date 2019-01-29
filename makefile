.PHONY: help
help:
	cat makefile

.PHONY: clean
clean:
	find * -name '*.pyc' -delete
	find * -name __pycache__ -delete

.PHONY: test
test:
	bash -ci "ac; flake8"
	bash -ci "ac; pytest -v -s --cov=cg_test --cov-report=term-missing ."
	bash -ci "ac 3; flake8"
	bash -ci "ac 3; pytest -v -s --cov=cg_test --cov-report=term-missing ."
