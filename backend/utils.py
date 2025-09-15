# utils.py

def calculate_charges(num_contracts: int) -> float:
    """
    Charges:
    - $0.50 per contract on entry
    - $0.50 per contract on exit
    - $0.57 regulatory fee on entry
    - $0.57 regulatory fee on exit
    """
    commission = 0.50 * 2 * num_contracts     # in + out
    regulatory = 0.57 * 2                     # per trade, in + out
    return commission + regulatory

def calculate_tax(gross_pl: float) -> float:
    """
    15% tax on profits only (not on losses).
    """
    return 0.15 * gross_pl if gross_pl > 0 else 0.0