# models.py

from pydantic import BaseModel
from typing import List

class StrategyResult(BaseModel):
    strategy: str
    total_contracts: int
    gross_pl: float
    charges: float
    tax: float
    net_pl: float

class PortfolioSummary(BaseModel):
    strategies: List[StrategyResult]
    total_gross: float
    total_charges: float
    total_tax: float
    total_net: float