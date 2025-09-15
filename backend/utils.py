# Reusable helpers (e.g., fee calculators)

# utils.py
def calculate_charges(contracts: int) -> float:
    # Per contract $0.50 entry + $0.50 exit
    per_contract_fee = 0.50 * 2
    # Regulatory SPX fee: $0.57 per side → $1.14 total
    regulatory_fee = 0.57 * 2
    return (contracts * per_contract_fee) + regulatory_fee

def calculate_tax(profit: float) -> float:
    return 0.15 * profit if profit > 0 else 0.0