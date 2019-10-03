.PHONY: help
help:
	cat makefile

.PHONY: clean
clean:
	find * -name '*.pyc' -delete
	find * -name __pycache__ -delete

.PHONY: setup
setup:
	pip install -r requirements.txt

.PHONY: test2
test2:
	bash -ci "ac; flake8"
	bash -ci "ac; pytest -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test3
test3:
	bash -ci "ac 3; flake8"
	bash -ci "ac 3; pytest -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test
test: test2 test3
