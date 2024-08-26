
from payment_handler_rs import PaymentHandlerParallel
import time
import cProfile
import os
import logging
import pandas as pd
from datetime import datetime
import joblib
from helpers import generate_random_seeds, generate_payments, setup_environment, initialize_profiler, log_time
import math

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)

# Create a logger object
logger = logging.getLogger(__name__)

def main():
    config = setup_environment()
    profiler = initialize_profiler()
    time_taken = []

    for run_index in range(config['runs']):

        logger.info("Loading payments")

        payments = pd.read_parquet(f'artefacts/payments/payments_{run_index}.parquet').to_dict(orient='records')

        logger.info(f"Starting run {run_index + 1}/{config['runs']}")

        start_time = time.time()
        profiler.enable()

        payment_handler = PaymentHandlerParallel()
        payment_handler.process_payments(
            [(payment["merchant_id"], payment["amount"]) for payment in payments],
            config['periodic_statistics_interval'],
            config['periodic_statistics_window_size'],
            config['confidence_interval'])

        profiler.disable()
        profiler.dump_stats(f"artefacts/rust_parallel/run_{run_index + 1}.prof")

        end_time = time.time()
        elapsed_time = log_time(start_time, end_time)
        time_taken.append(elapsed_time)

    joblib.dump(time_taken, 'artefacts/rust_parallel/time_taken.joblib')
    logger.info(f"Average time taken: {sum(time_taken)/len(time_taken):.2f} seconds")
    logger.info(f"Max time taken: {max(time_taken):.2f} seconds")
    logger.info(f"Min time taken: {min(time_taken):.2f} seconds")

if __name__ == "__main__":
    main()