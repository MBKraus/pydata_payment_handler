.PHONY: develop, release

export VIRTUAL_ENV={path to your virtual environment}

develop:
	maturin develop 

release:
	maturin build --release --target x86_64-apple-darwin
	pip install target/wheels/payment_handler_rs-0.1.0-cp310-cp310-macosx_10_12_x86_64.whl --force-reinstall

python_handler
	python handler_py.py

rust_handler
	python handler_rs.py