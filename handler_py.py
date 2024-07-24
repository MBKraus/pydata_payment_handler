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

class PaymentHandler:
    def __init__(self):
        self.payments = {}
        self.payment_counts = {}
        self.current_balances = {}
        self.cumulative_balances = {}
        self.periodic_average_payments = {}
        self.periodic_std_payments = {}
        self.var_cumulative_balances = {}

    def initialize_merchant(self, merchant_id):
        """Initialize merchant data structures if not already initialized."""
        if merchant_id not in self.payments:
            self.payments[merchant_id] = []
            self.payment_counts[merchant_id] = 0
            self.current_balances[merchant_id] = 0.0  
            self.cumulative_balances[merchant_id] = [0.0]
            self.var_cumulative_balances[merchant_id] = []

    def process_payment(self, merchant_id, amount):
        """Process a payment for a merchant."""
        self.initialize_merchant(merchant_id)
        self.payments[merchant_id].append(amount)
        self.payment_counts[merchant_id] += 1
        self.current_balances[merchant_id] += amount  
        self.cumulative_balances[merchant_id].append(self.current_balances[merchant_id])  # Update cumulative balance

    def get_payment_count(self, merchant_id):
        """Get the payment count for a merchant."""
        if merchant_id in self.payment_counts:
            return self.payment_counts[merchant_id]
        else:
            raise ValueError("Merchant ID not found")

    def calculate_periodic_average(self, values, window_size):
        """Calculate the average of the last 'window_size' values."""
        if len(values) < window_size:
            raise ValueError("Not enough values to calculate average")
        return sum(values[-window_size:]) / window_size

    def calculate_periodic_std(self, values, window_size):
        """Calculate the standard deviation of the last 'window_size' values."""
        avg = self.calculate_periodic_average(values, window_size)
        variance = sum((x - avg) ** 2 for x in values[-window_size:]) / window_size
        return math.sqrt(variance)

    def update_periodic_statistics(self, merchant_id, window_size):
        """Update the periodic statistics for a merchant."""
        if merchant_id in self.payments:
            payments = self.payments[merchant_id]
            if len(payments) >= window_size:
                avg = self.calculate_periodic_average(payments, window_size)
                std = self.calculate_periodic_std(payments, window_size)
                self._append_to_dict_list(self.periodic_average_payments, merchant_id, avg)
                self._append_to_dict_list(self.periodic_std_payments, merchant_id, std)
        else:
            raise ValueError("Merchant ID not found")

    def calculate_var(self, values, confidence_level):
        """Calculate the Value at Risk (VaR) for a list of values."""
        if not values:
            raise ValueError("The values list is empty")

        sorted_values = sorted(values)
        index = int((1 - confidence_level) * len(sorted_values))
        return sorted_values[index]

    def calculate_balance_var(self, merchant_id, confidence_level):
        """Calculate the VaR for the cumulative balances of a merchant."""
        if merchant_id not in self.cumulative_balances:
            raise ValueError("Merchant ID not found")

        cumulative_balances = self.cumulative_balances[merchant_id]
        if len(cumulative_balances) <= 1:
            raise ValueError("Not enough balance data to calculate VaR")

        var = self.calculate_var(cumulative_balances, confidence_level)
        self._append_to_dict_list(self.var_cumulative_balances, merchant_id, var)
        return var

    def _append_to_dict_list(self, dictionary, key, value):
        """Helper method to append a value to a list in a dictionary."""
        if key not in dictionary:
            dictionary[key] = []
        dictionary[key].append(value)


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