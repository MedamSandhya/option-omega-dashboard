# backend/models.py

from pydantic import BaseModel
from typing import List, Optional

class StrategyResult(BaseModel):
    strategy_name: str
    gross_pl: float
    charges: float
    tax: float
    net_pl: float

class PortfolioSummary(BaseModel):
    total_gross_pl: float
    total_charges: float
    total_tax: float
    total_net_pl: float
    strategy_breakdown: List[StrategyResult]