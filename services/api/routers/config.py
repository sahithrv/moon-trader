from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter
from models.config import Symbol, SymbolCreate

#create router for config
# API Router allows you to group related API endpoints together across multiple files

router = APIRouter(prefix="/config", tags=["config"])

symbols_store: List[Symbol] = [
    Symbol(
        symbol="AAPL",
        enabled=True,
        name="Apple Inc.",
        asset_type="stock",
        exchange="NASDAQ",
        created_at=datetime.now(timezone.utc),
    ),
    Symbol(
        symbol="MSFT",
        enabled=True,
        name="Microsoft Corporation",
        asset_type="stock",
        exchange="NASDAQ",
        created_at=datetime.now(timezone.utc),
    ),
]

@router.get("/symbols", response_model=List[Symbol])
def get_symbols():
    return symbols_store

# we use **payload.model_dump() because FastAPI already converts the JSON to a Python object
# ** is python's way of unpacking a dict into keyword args
@router.post("/symbols", response_model=Symbol)
def add_symbol(payload: SymbolCreate):
    new_symbol = Symbol(
        **payload.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    symbols_store.append(new_symbol)
    return new_symbol

@router.delete("/symbols/{symbol}")
def remove_symbol(symbol: str):
    for index, ticker in enumerate(symbols_store):
        if ticker.symbol == symbol:
            del symbols_store[index]
            return {"message": f"{symbol.upper()} removed"}
    return {"message": f"{symbol.upper()} is not in your ticker list"}