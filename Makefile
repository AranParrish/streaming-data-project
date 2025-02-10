#################################################################################
#
# Makefile to build the project
#
#################################################################################

PROJECT_NAME = streaming-data-project
PYTHON = python
WD=$(shell pwd)
PYTHONPATH=${WD}
SHELL := /bin/bash
PROFILE = default
PIP:=pip

## Create python interpreter environment.
create-environment:
	@echo ">>> About to create environment: $(PROJECT_NAME)..."
	@echo ">>> check python3 version"
	( \
		$(PYTHON) --version; \
	)
	@echo ">>> Setting up VirtualEnv."
	( \
	    $(PYTHON) -m venv venv; \
	)

# Define utility variable to help calling Python from the virtual environment
ACTIVATE_ENV := source venv/bin/activate

# Execute python related functionalities from within the project's environment
define execute_in_env
	$(ACTIVATE_ENV) && $1
endef

## Build the environment requirements
requirements: create-environment
	$(call execute_in_env, $(PIP) install pip-tools)
	$(call execute_in_env, pip-compile requirements.in)
	$(call execute_in_env, $(PIP) install -r ./requirements.txt)

################################################################################################################
# Set Up
## Install bandit
bandit:
	$(call execute_in_env, $(PIP) install bandit)

## Install safety
safety:
	$(call execute_in_env, $(PIP) install safety)

## Install black
black:
	$(call execute_in_env, $(PIP) install black)

## Install coverage
coverage:
	$(call execute_in_env, $(PIP) install coverage)

## Set up dev requirements (bandit, safety, black)
dev-setup: bandit safety black coverage

# Build / Run

## Run the security test (bandit + safety)
security-test:
	$(call execute_in_env, safety scan)
	$(call execute_in_env, bandit -lll */*.py *c/*.py)

## Run the black code check
run-black:
	$(call execute_in_env, black  ./src/*.py ./test/*.py)

## Run the unit tests
unit-test:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --testdox -v)

## Run the coverage check
check-coverage:
	$(call execute_in_env, PYTHONPATH=${PYTHONPATH} pytest --cov=src test/)

## Run all checks
run-checks: security-test run-black unit-test check-coverage

################################################################################################################

## Create lambda layer for cloud deployment

# Create lambda layer virtual environment

lambda-venv:
	$(PYTHON) -m venv lambda_venv;

# Define utility variable to help calling Python from the lamnda virtual environment
ACTIVATE_LAMBDA_ENV := source lambda_venv/bin/activate

# Execute python related functionalities from within the lambda's virtual environment
define execute_in_lambda_env
	$(ACTIVATE_LAMBDA_ENV) && $1
endef

lambda-layer: lambda-venv
	rm -rf lambda_layer
	mkdir -p lambda_layer/python
	$(call execute_in_lambda_env, $(PIP) install pip-tools)
	$(call execute_in_lambda_env, pip-compile requirements.in)
	$(call execute_in_lambda_env, $(PIP) install -r ./requirements.txt -t lambda_layer/python/lib/python3.11/site-packages)
	cp src/streaming_data.py lambda_layer/python/streaming_data.py
	cd lambda_layer && zip -r ../lambda_layer.zip . && cd ..
	rm -rf lambda_layer
	@echo "Lambda layer created in file lambda_layer.zip"