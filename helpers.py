import random

def generate_random_seeds(initial_seed, num_seeds):
    random.seed(initial_seed)
    return [random.randint(0, 2**32 - 1) for _ in range(num_seeds)]

def generate_transactions(num_merchants, num_transactions, seed=42):
    random.seed(seed)
    transactions = {}
    for _ in range(num_merchants):
        merchant_id = f"merchant_{random.randint(1000, 1000000)}"
        transactions[merchant_id] = [random.uniform(1.0, 10000.0) for _ in range(num_transactions)]
    return transactions