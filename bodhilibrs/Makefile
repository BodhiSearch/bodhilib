build:
	maturin develop

testrs:
	cargo test

test:
	poetry run pytest

bench:
	maturin develop --release
	poetry run pytest --benchmark-only
