SHELL := /bin/bash
.PHONY: test deps lint format

install:
	python setup.py build
	python setup.py install

release:
	python setup.py register
	python setup.py sdist upload

deps:
	pip install -r requirements-dev.txt

# Check for errors in Python files
pylint: deps
	find . | grep .py$$ | xargs pylint -E

lint: deps
	pep8 --config ./pep8 . || true

format: deps
	autopep8 -i -r -j0 -a --experimental --max-line-length 100 --indent-size 2 .

# nose test-runner
nose:
	nosetests test

test: deps pylint nose
