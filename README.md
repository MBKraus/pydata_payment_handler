## Polishing Python: Preventing Performance Corrosion with Rust


Steps to run the payment handler scripts:

1) install [Rust](https://www.rust-lang.org/tools/install)
2) create a Python 3.10 virtual environment 
2) install [Poetry](https://python-poetry.org/) in this virtual environment and
   install the project's dependencies (`poetry install`) 
   Note: The lock file in the repo was generated with Poetry 1.8.3
3) ensure you put the path to your virtual environment in VIRTUAL_ENV (`export VIRTUAL_ENV=<path_to_virtual_env>`)
4) build and install the wheel in your Python environment (`maturin develop`)
5) generate payment batches with `make generate_payments`
6) run the Python and Rust payment handler with `make python_handler`, `make rust_parallel_handler` and `rust_single_threaded_handler`, respectively
