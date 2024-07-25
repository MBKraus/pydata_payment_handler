1) poetry install 
2) maturin new -b pyo3 payment_handler_rs then edit Cargo.toml to add abi3-py38 feature
3) development -> maturin develop (for dev profile)
4) release

export VIRTUAL_ENV=/Users/mkraus/opt/miniconda3/envs/pydata

maturin build --release --target x86_64-apple-darwin

pip install target/wheels/payment_handler_rs-0.1.0-cp310-cp310-macosx_10_12_x86_64.whl --force-reinstall

To do

- payment by payment check count in loop in python
- payment by payment check count loop in rust
- hand all payments to rust



