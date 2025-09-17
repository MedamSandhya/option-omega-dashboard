from pydantic import BaseModel
from typing import List

class Trade(BaseModel):
    strategy: str
    gross_pl: float

class TradeWithTax(BaseModel):
    strategy: str
    gross_pl: float
    tax_rate: float
    tax_paid: float
    net_pl: float

class TradesRequest(BaseModel):
    trades: List[Trade]
    tax_rate: float