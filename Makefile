help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "build - package"

all: default

default: clean dev_deps deps build test


clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf Dockerfile*
	rm -rf run_anovos*
	rm -rf dist/
	rm -rf ml_anovos_report.html
	rm -rf ./*.whl
	rm -rf ./docker-stacks

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf ./data/tmp/output 

test:
	-coverage run --source=. -m pytest src/test
	coverage report
	coverage html

build: clean
	cp ./bin/*.whl ./
	cp ./demo/Dockerfile* ./
	cp ./demo/run_anovos* ./
	rm -rf ./dist && mkdir ./dist && mkdir ./dist/data && mkdir ./dist/output
	cp ./src/main/main.py ./dist
	cp ./config/configs.yaml ./dist
	cp -rf ./src/main/anovos ./dist/anovos
	cd ./dist && zip -r anovos.zip ./anovos
	cd ./dist && tar -cvzf anovos.tar.gz ./anovos
	cp -rf ./examples/data/income_dataset ./dist/data/income_dataset
	cp -rf ./data/metric_dictionary.csv ./dist/data/metric_dictionary.csv
	cp ./bin/spark-submit.sh ./dist
