import random
import time
import cProfile
import os
import logging
from datetime import datetime
from helpers import generate_random_seeds, generate_transactions

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)

# Create a logger object
logger = logging.getLogger(__name__)

class Bookkeeping:
    def __init__(self):
        self.transactions = {}
        self.moving_averages = {}

    def add_transaction(self, merchant_id, amount):
        if merchant_id not in self.transactions:
            self.transactions[merchant_id] = []
        self.transactions[merchant_id].append(amount)

    def compute_totals(self, merchant_id):
        if merchant_id in self.transactions:
            return sum(self.transactions[merchant_id])
        else:
            raise ValueError("Merchant ID not found")

    def compute_average(self, merchant_id):
        if merchant_id in self.transactions:
            total = sum(self.transactions[merchant_id])
            return total / len(self.transactions[merchant_id])
        else:
            raise ValueError("Merchant ID not found")

    def find_extremes(self, merchant_id):
        if merchant_id in self.transactions:
            highest = max(self.transactions[merchant_id])
            lowest = min(self.transactions[merchant_id])
            return highest, lowest
        else:
            raise ValueError("Merchant ID not found")

    def summarize(self, merchant_id):
        if merchant_id in self.transactions:
            total = self.compute_totals(merchant_id)
            average = self.compute_average(merchant_id)
            highest, lowest = self.find_extremes(merchant_id)
            return {
                'total': total,
                'average': average,
                'highest': highest,
                'lowest': lowest
            }
        else:
            raise ValueError("Merchant ID not found")
    
    def calculate_moving_average(self, merchant_id, window_size):
        if merchant_id in self.transactions:
            transactions = self.transactions[merchant_id]
            if len(transactions) >= window_size:
                moving_average = sum(transactions[-window_size:]) / window_size
                if merchant_id not in self.moving_averages:
                    self.moving_averages[merchant_id] = []
                self.moving_averages[merchant_id].append(moving_average)
        else:
            raise ValueError("Merchant ID not found")


if __name__ == "__main__":

    profiler = cProfile.Profile()

    time_taken = []
    RANDOM_SEED = int(os.environ['RANDOM_SEED'])
    RUNS = int(os.environ['RUNS'])
    NUM_MERCHANTS = int(os.environ['NUM_MERCHANTS'])
    NUM_TRANSACTIONS_PER_MERCHANT = int(os.environ['NUM_TRANSACTIONS_PER_MERCHANT'])
    WINDOW_SIZE = int(os.environ['WINDOW_SIZE'])

    random_seeds = generate_random_seeds(RANDOM_SEED, RUNS)

    for i in range(RUNS):

        # profiler.enable()
        logger.info(f"Starting run {i+1}/{RUNS}")

        # Create a Bookkeeping instance
        bookkeeping = Bookkeeping()

        # Generate random transactions
        transactions = generate_transactions(NUM_MERCHANTS, NUM_TRANSACTIONS_PER_MERCHANT, random_seeds[i])

        logger.info("Generated transactions")

        start_time = time.time()
        start_time_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
        logger.info("Start time: %s", start_time_formatted)

        # Add transactions to the Bookkeeping instance
        for merchant_id, amounts in transactions.items():
            for amount in amounts:
                bookkeeping.add_transaction(merchant_id, amount)
                bookkeeping.calculate_moving_average(merchant_id, WINDOW_SIZE)  # Calculate moving average

        # Summarize and print the results for each merchant
        for merchant_id in transactions.keys():
            summary = bookkeeping.summarize(merchant_id)
            # print(f"Summary for {merchant_id}: {summary}")
   
        end_time = time.time()
        end_time_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
        elapsed_time = end_time - start_time
        logger.info("End time: %s", end_time_formatted)
        logger.info(f"Time taken to run __main__: {elapsed_time:.2f} seconds")

        time_taken.append(elapsed_time)

        # profiler.disable()
        # profiler.print_stats()

    logger.info(f"Average time taken to run __main__: {sum(time_taken)/len(time_taken):.2f} seconds")
    logger.info(f"Max time taken to run __main__: {max(time_taken):.2f} seconds")
    logger.info(f"Min time taken to run __main__: {min(time_taken):.2f} seconds")
