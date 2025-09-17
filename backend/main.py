from fastapi import FastAPI
from models import TradeWithTax, TradesRequest

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Option Omega Dashboard Backend Running"}

@app.post("/calculate_pl/", response_model=list[TradeWithTax])
def calculate_pl(request: TradesRequest):
    """
    Calculate net P/L after tax for each strategy.
    Tax applies only on positive profits.
    """
    results = []
    for t in request.trades:
        tax_paid = max(0, t.gross_pl * (request.tax_rate / 100)) if t.gross_pl > 0 else 0
        net_pl = t.gross_pl - tax_paid
        results.append(
            TradeWithTax(
                strategy=t.strategy,
                gross_pl=t.gross_pl,
                tax_rate=request.tax_rate,
                tax_paid=tax_paid,
                net_pl=net_pl
            )
        )
    return results