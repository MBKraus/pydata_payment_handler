import random
import logging
import os
import cProfile
from datetime import datetime


logger = logging.getLogger(__name__)


def generate_random_seeds(initial_seed, num_seeds):
    random.seed(initial_seed)
    return [random.randint(0, 2**32 - 1) for _ in range(num_seeds)]


def generate_payments(num_merchants, num_transactions, seed):
    random.seed(seed)
    transactions = []

    for _ in range(num_merchants):
        merchant_id = f"merchant_{random.randint(1000, num_merchants+10000)}"
        
        # Generate 80% positive transactions
        positive_transactions = [{'merchant_id': merchant_id, 'amount': random.uniform(0, 10000)} for _ in range(int(num_transactions * 0.8))]
        
        # Generate 20% negative transactions
        negative_transactions = [{'merchant_id': merchant_id, 'amount': random.uniform(-5000, 0)} for _ in range(num_transactions - len(positive_transactions))]
        
        # Combine both positive and negative transactions
        all_transactions = positive_transactions + negative_transactions
        
        # Add transactions to the main list
        transactions.extend(all_transactions)
    
    # Shuffle the list to mix transactions
    random.shuffle(transactions)
    
    return transactions


def setup_environment():
    """Load configuration from environment variables."""
    return {
        'initial_seed': int(os.environ['INITIAL_SEED']),
        'runs': int(os.environ['RUNS']),
        'num_merchants': int(os.environ['NUM_MERCHANTS']),
        'num_payments_per_merchant': int(os.environ['NUM_PAYMENTS_PER_MERCHANT']),
        'periodic_statistics_interval': int(os.environ['PERIODIC_STATISTICS_INTERVAL']),
        'periodic_statistics_window_size': int(os.environ['PERIODIC_STATISTICS_WINDOW_SIZE']),
        'confidence_interval': float(os.environ['CONFIDENCE_INTERVAL']),
    }


def initialize_profiler():
    """Initialize and return a cProfile.Profile instance."""
    return cProfile.Profile()

def log_time(start_time, end_time):
    """Log the start and end times, and the elapsed time."""
    start_formatted = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_formatted = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    elapsed_time = end_time - start_time
    logger.info("Start time: %s", start_formatted)
    logger.info("End time: %s", end_formatted)
    logger.info(f"Time taken: {elapsed_time:.2f} seconds")
    return elapsed_time

