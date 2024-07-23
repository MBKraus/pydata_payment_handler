import time
import random
from payment_handler_rs import PaymentHandler
from helpers import generate_random_seeds, generate_transactions
import logging
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)

# Create a logger object
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    time_taken = []
    RANDOM_SEED = int(os.environ['RANDOM_SEED'])
    RUNS = int(os.environ['RUNS'])
    NUM_MERCHANTS = int(os.environ['NUM_MERCHANTS'])
    NUM_TRANSACTIONS_PER_MERCHANT = int(os.environ['NUM_TRANSACTIONS_PER_MERCHANT'])
    WINDOW_SIZE = int(os.environ['WINDOW_SIZE'])

    random_seeds = generate_random_seeds(RANDOM_SEED, RUNS)

    for i in range(RUNS):
        logger.info(f"Starting run {i+1}/{RUNS}")
        payment_handler = PaymentHandler()
        
        transactions = generate_transactions(NUM_MERCHANTS, NUM_TRANSACTIONS_PER_MERCHANT, random_seeds[i])
        logger.info("Generated transactions")

        start_time = time.time()
        start_time_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        logger.info("Start time: %s", start_time_formatted)

        # Add transactions to the Bookkeeping instance
        for merchant_id, amounts in transactions.items():
            for amount in amounts:
                payment_handler.add_transaction(merchant_id, amount)
                if payment_handler.get_transaction_count(merchant_id) % WINDOW_SIZE == 0:
                    payment_handler.update_periodic_statistics(merchant_id, WINDOW_SIZE)  

        for merchant_id in transactions.keys():
            summary = payment_handler.summarize(merchant_id)
            # print(f"Summary for {merchant_id}: {summary}")

        end_time = time.time()
        end_time_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
        elapsed_time = end_time - start_time
        logger.info("End time: %s", end_time_formatted)
        logger.info(f"Time taken to run __main__: {elapsed_time:.2f} seconds")

        time_taken.append(elapsed_time)

    logger.info(f"Average time taken to run __main__: {sum(time_taken) / len(time_taken):.2f} seconds")
    logger.info(f"Max time taken to run __main__: {max(time_taken):.2f} seconds")
    logger.info(f"Min time taken to run __main__: {min(time_taken):.2f} seconds")
