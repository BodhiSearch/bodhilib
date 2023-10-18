.PHONY: install build test run exec all.check ci.test ci.build lint clean_docs docs run_docs

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

ci.check:
	@poetry run python make.py exec all check --lock

ci.test:
	@poetry run python make.py run $(filter-out $@,$(MAKECMDGOALS)) pytest --cov=src --cov-report=xml --cov-report=html
	@:

ci.build:
	@# Invoke the Python script to 'build' and all passed arguments.
	@poetry run python make.py exec $(filter-out $@,$(MAKECMDGOALS)) build
	@:

ci.supports:
	@# Invoke the Python script to 'supports' and all passed arguments.
	@poetry run python make.py supports $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.tox:
	@# Invoke the make.py script with 'tox' passing all passthrough args.
	@poetry run python make.py tox $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.lint:
	@poetry run pre-commit run --show-diff-on-failure --color=always --all-files

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	docs/docs.py

run_docs:
	python -m http.server -d docs/_build/html 8000

%:
	@:
