.PHONY: install build test run exec all.check ci.test ci.build lint clean_docs docs run_docs rs testrs

build:
	@# Invoke the Python script to 'build' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS)) build
	@:

test:
	@# Invoke the Python script to 'test' and all passed arguments.
	python make.py tox $(filter-out $@,$(MAKECMDGOALS)) --only-dev --python-version py38
	@:

run:
	@# Invoke the Python script with 'run' and all passed arguments.
	python make.py run $(filter-out $@,$(MAKECMDGOALS))
	@:

exec:
	@# Invoke the Python script with 'exec' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS))
	@:

stub:
	@# Invoke the Python script with 'stub' and all passed arguments.
	python make.py stub $(filter-out $@,$(MAKECMDGOALS))
	@:

rs:
	$(MAKE) -C bodhilibrs build

testrs: rs
	poetry run pytest -vv -m rs
	$(MAKE) -C bodhilibrs test
	$(MAKE) -C bodhilibrs testrs

benchrs:
	$(MAKE) -C bodhilibrs bench

ci.check-pyproj:
	@python make.py check-pyproj all

ci.check:
	@python make.py exec all check --lock

ci.test:
	@python make.py tox $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.build:
	@# Invoke the Python script to 'build' and all passed arguments.
	@python make.py exec $(filter-out $@,$(MAKECMDGOALS)) build
	@:

ci.supports:
	@# Invoke the Python script to 'supports' and all passed arguments.
	@python make.py supports $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.tox:
	@# Invoke the make.py script with 'tox' passing all passthrough args.
	@python make.py tox $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.lint:
	@poetry run pre-commit run --show-diff-on-failure --color=always --all-files

ci.update-lock-files:
	@python make.py exec all lock --no-update

ci.update-configs:
	@python make.py update-configs

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	docs/docs.py

run_docs:
	python -m http.server -d docs/_build/html 8000

%:
	@:
