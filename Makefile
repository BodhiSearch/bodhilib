.PHONY: run exec install build ci.check ci.install ci.lint ci.test ci.build clean_docs docs run_docs

install:
	@# Invoke the Python script to 'install' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS)) install
	@:

build:
	@# Invoke the Python script to 'build' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS)) build
	@:

test:
	@# Invoke the Python script to 'test' and all passed arguments.
	python make.py run $(filter-out $@,$(MAKECMDGOALS)) pytest
	@:

run:
	@# Invoke the Python script with 'run' and all passed arguments.
	python make.py run $(filter-out $@,$(MAKECMDGOALS))
	@:

exec:
	@# Invoke the Python script with 'exec' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS))
	@:

all.check:
	@python make.py exec all check --lock

ci.test:
	@python make.py run $(filter-out $@,$(MAKECMDGOALS)) pytest --cov=src --cov-report=xml --cov-report=html

lint:
	pre-commit run --all-files

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	docs/docs.py

run_docs:
	poetry run python -m http.server -d docs/_build/html 8000

%:
	@echo "Unknown target '$@'":
