.PHONY: develop, release, python_handler, rust_handler

# export VIRTUAL_ENV={path to your virtual environment}
export INITIAL_SEED=42
export RUNS=5
export NUM_MERCHANTS=1000
export NUM_PAYMENTS_PER_MERCHANT=10000
export PERIODIC_STATISTICS_INTERVAL=100
export PERIODIC_STATISTICS_WINDOW_SIZE=100
export CONFIDENCE_INTERVAL=0.9

develop:
	maturin develop 
	
release:
	maturin build --release --target x86_64-apple-darwin
	pip install target/wheels/payment_handler_rs-0.1.0-cp310-cp310-macosx_10_12_x86_64.whl --force-reinstall

python_handler:
	python handler_py.py

rust_handler:
	python handler_rs.py