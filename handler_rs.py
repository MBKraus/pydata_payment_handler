import time
import random
from payment_handler_rs import PaymentHandler
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)

# Create a logger object
logger = logging.getLogger(__name__)

def generate_transactions(num_merchants, num_transactions, seed=42):
    random.seed(seed)
    transactions = {}
    for _ in range(num_merchants):
        merchant_id = f"merchant_{random.randint(1000, 9999)}"
        transactions[merchant_id] = [random.uniform(1.0, 1000.0) for _ in range(num_transactions)]
    return transactions

if __name__ == "__main__":
    time_taken = []
    RUNS = 5
    NUM_MERCHANTS = 2000
    NUM_TRANSACTIONS_PER_MERCHANT = 10000

    for i in range(RUNS):
        logger.info(f"Starting run {i+1}/{RUNS}")
        payment_handler = PaymentHandler()
        
        transactions = generate_transactions(NUM_MERCHANTS, NUM_TRANSACTIONS_PER_MERCHANT)
        logger.info("Generated transactions")

        start_time = time.time()
        start_time_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        logger.info("Start time: %s", start_time_formatted)

        for merchant_id, amounts in transactions.items():
            for amount in amounts:
                payment_handler.add_transaction(merchant_id, amount)
                payment_handler.calculate_moving_average(merchant_id, 1000)

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
