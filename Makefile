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

run: docker_run

local_run:
	python ./main.py

docker_build:
	docker build -t ebs-snapshots-local .

docker_run: docker_build
	@echo "HERE"
	@echo "THERE"
	@docker run \
	-v /tmp:/tmp \
	-e AWS_ACCESS_KEY_ID=$$AWS_ACCESS_KEY_ID \
	-e AWS_SECRET_ACCESS_KEY=$$AWS_SECRET_ACCESS_KEY \
	-e AWS_REGION=$$AWS_REGION \
	-e BACKUP_CONFIG=$$BACKUP_CONFIG \
	ebs-snapshots-local
