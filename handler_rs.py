
from payment_handler_rs import PaymentHandler
import time
import cProfile
import os
import logging
from datetime import datetime
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
    random_seeds = generate_random_seeds(config['initial_seed'], config['runs'])
    time_taken = []

    for run_index in range(config['runs']):
        logger.info(f"Starting run {run_index + 1}/{config['runs']}")

        payments = generate_payments(config['num_merchants'], config['num_payments_per_merchant'], random_seeds[run_index])
        logger.info("Generated payments")

        start_time = time.time()
        profiler.enable()

        payment_handler = PaymentHandler()
        for payment in payments:
            payment_handler.process_payment(payment["merchant_id"], payment["amount"])
            if payment_handler.get_payment_count(payment["merchant_id"]) % config['periodic_statistics_interval'] == 0:
                payment_handler.update_periodic_statistics(payment["merchant_id"], config['periodic_statistics_window_size'])
                payment_handler.calculate_balance_var(payment["merchant_id"], config['confidence_interval'])

        profiler.disable()
        profiler.dump_stats(f"reports/python/run_{run_index + 1}.prof")

        end_time = time.time()
        elapsed_time = log_time(start_time, end_time)
        time_taken.append(elapsed_time)

    logger.info(f"Average time taken: {sum(time_taken)/len(time_taken):.2f} seconds")
    logger.info(f"Max time taken: {max(time_taken):.2f} seconds")
    logger.info(f"Min time taken: {min(time_taken):.2f} seconds")

if __name__ == "__main__":
    main()