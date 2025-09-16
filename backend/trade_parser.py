# trade_parser.py

import csv
from collections import defaultdict
from backend.utils import calculate_charges, calculate_tax
from backend.models import StrategyResult, PortfolioSummary

def parse_trades_from_csv(file_path: str) -> PortfolioSummary:
    strat_data = defaultdict(lambda: {"contracts": 0, "gross": 0.0})

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            strategy = row["strategy"]
            contracts = int(row["contracts"])
            gross_pl = float(row["gross_pl"])

            strat_data[strategy]["contracts"] += contracts
            strat_data[strategy]["gross"] += gross_pl

    strat_results = []
    total_gross = total_charges = total_tax = total_net = 0.0

    for strat, data in strat_data.items():
        charges = calculate_charges(data["contracts"])
        tax = calculate_tax(data["gross"])
        net = data["gross"] - charges - tax

        strat_results.append(StrategyResult(
            strategy=strat,
            total_contracts=data["contracts"],
            gross_pl=data["gross"],
            charges=charges,
            tax=tax,
            net_pl=net
        ))

        total_gross += data["gross"]
        total_charges += charges
        total_tax += tax
        total_net += net

    return PortfolioSummary(
        strategies=strat_results,
        total_gross=total_gross,
        total_charges=total_charges,
        total_tax=total_tax,
        total_net=total_net
    )