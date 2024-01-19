build:
	maturin develop

release:
	maturin develop --release

testrs:
	cargo test

test:
	poetry run pytest

bench:
	maturin develop --release
	poetry run pytest --benchmark-only
