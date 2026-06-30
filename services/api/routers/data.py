from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.dependency import get_db
from db.models import BarORM, SymbolORM
from models.data import BackfillRequests, BackfillResponse, BarResponse
from service.market_data_service import MarketDataService, WATCHLIST
from services.indicators.engine import calculate_indicators_from_bars

router = APIRouter(prefix="/data", tags=["data"])

def get_bars_for_symbol(
    db: Session,
    symbol: str,
    timeframe: str = "1Day",
    limit: int = 100,
) -> List[BarResponse]:
    normalized_symbol = symbol.upper()

    rows = (
        db.query(BarORM, SymbolORM)
        .join(SymbolORM, BarORM.symbol_id == SymbolORM.id)
        .filter(SymbolORM.symbol == normalized_symbol)
        .filter(BarORM.timeframe == timeframe)
        .order_by(BarORM.opened_at.desc())
        .limit(limit)
        .all()
    )

    return [
        BarResponse(
            symbol=symbol_row.symbol,
            timeframe=bar.timeframe,
            opened_at=bar.opened_at,
            open=float(bar.open),
            high=float(bar.high),
            low=float(bar.low),
            close=float(bar.close),
            volume=bar.volume,
            source=bar.source,
        )
        for bar, symbol_row in rows
    ]

#backfills and updates the DB
@router.post("/backfill", response_model=BackfillResponse)
def backfill_data(
    payload: BackfillRequests,
    db: Session = Depends(get_db),
):
    symbols = payload.symbols or WATCHLIST
    service = MarketDataService(db)

    count = service.backfill_daily_bars(
        symbols=symbols,
        start=payload.start,
        end=payload.end,
    )

    return BackfillResponse(
        symbols=[symbol.upper() for symbol in symbols],
        timeframe="1Day",
        inserted_or_updated=count,
        source="alpaca"
    )

@router.get('/bars/{symbol}', response_model=List[BarResponse])
def get_bars(
    symbol: str,
    timeframe: str = Query(default="1Day"),
    limit: int = Query(default=100),
    db: Session = Depends(get_db)
):
    return get_bars_for_symbol(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )

@router.get("/indicators/{symbol}")
def get_indicators(
    symbol: str,
    timeframe: str = Query(default="1Day"),
    limit: int = Query(default=100),
    db: Session = Depends(get_db),
):
    bars = get_bars_for_symbol(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )
    return calculate_indicators_from_bars(list(reversed(bars)))
