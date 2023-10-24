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

.PHONY: test3
test3:
	bash -ci "pyenv-on 3; flake8 && PYTHONPATH=. pytest --pdb -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test
test: test3
