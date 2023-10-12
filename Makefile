.PHONY: run exec ci.check ci.install ci.lint ci.test ci.build clean_docs docs run_docs

run:
	@# Invoke the Python script with 'run' and all passed arguments.
	python make.py run $(filter-out $@,$(MAKECMDGOALS))
	@:

exec:
	@# Invoke the Python script with 'exec' and all passed arguments.
	python make.py exec $(filter-out $@,$(MAKECMDGOALS))
	@:

ci.check:
	@python make.py exec all check --lock

ci.install:
	@python make.py exec all install --compile

ci.lint:
	pre-commit run --all-files

ci.test:
	@python make.py run all pytest --cov=src --cov-report=xml --cov-report=html

ci.build:
	@python make.py exec all build

clean_docs:
	rm -rf docs/_build

docs: clean_docs
	docs/docs.py

run_docs:
	poetry run python -m http.server -d docs/_build/html 8000

%:
	@echo "Unknown target '$@'":
