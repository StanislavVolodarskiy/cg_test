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
	bash -ci "pyenv-on; flake8"
	bash -ci "pyenv-on; PYTHONPATH=. pytest --pdb -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test37
test37:
	bash -ci "pyenv-on 37; flake8"
	bash -ci "pyenv-on 37; PYTHONPATH=. pytest --pdb -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test39
test39:
	bash -ci "pyenv-on 39; flake8"
	bash -ci "pyenv-on 39; PYTHONPATH=. pytest --pdb -v -s --cov=cg_test --cov-report=term-missing ."

.PHONY: test
test: test2 test37 test39
