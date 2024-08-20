from helpers import generate_random_seeds, generate_payments, setup_environment
import logging
import joblib
import pandas as pd

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
)

logger = logging.getLogger(__name__)

def main():
    config = setup_environment()
    random_seeds = generate_random_seeds(config['initial_seed'], config['runs'])

    logger.info("Generating payments for %s runs", config['runs'])

    for run_index in range(config['runs']):

        payments = generate_payments(config['num_merchants'], config['num_payments_per_merchant'], random_seeds[run_index])
        payments_df = pd.DataFrame(payments)
        payments_df.to_parquet(f'artefacts/payments/payments_{run_index}.parquet')
        logger.info("Generated payments for run %s", run_index + 1)

if __name__ == "__main__":
    main()