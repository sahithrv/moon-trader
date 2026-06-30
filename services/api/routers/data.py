from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.dependency import get_db
from db.models import BarORM, SymbolORM
from models.data import (
    BackfillRequests,
    BackfillResponse,
    BarResponse,
    IndicatorBarResponse,
    IndicatorResponse,
    Timeframe,
)
from service.market_data_service import MarketDataService, WATCHLIST
from services.indicators.engine import calculate_indicators_from_bars

router = APIRouter(prefix="/data", tags=["data"])

def get_bars_for_symbol(
    db: Session,
    symbol: str,
    timeframe: Timeframe = "1Day",
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

def build_indicator_response(
    symbol: str,
    timeframe: Timeframe,
    bars: List[BarResponse],
) -> IndicatorResponse:
    indicators = calculate_indicators_from_bars(bars)

    return IndicatorResponse(
        symbol=symbol.upper(),
        timeframe=timeframe,
        count=len(bars),
        bars=[
            IndicatorBarResponse(
                timestamp=bar.opened_at,
                open=bar.open,
                high=bar.high,
                low=bar.low,
                close=bar.close,
                volume=bar.volume,
                sma_20=indicators["sma_20"][i],
                ema_20=indicators["ema_20"][i],
                rsi_14=indicators["rsi_14"][i],
                vwap=indicators["vwap"][i],
                daily_return=indicators["daily_return"][i],
                volatility_20=indicators["volatility_20"][i],
            )
            for i, bar in enumerate(bars)
        ],
    )

#backfills and updates the DB
@router.post("/backfill", response_model=BackfillResponse)
def backfill_data(
    payload: BackfillRequests,
    db: Session = Depends(get_db),
):
    symbols = payload.symbols or WATCHLIST
    service = MarketDataService(db)

    count = service.backfill_bars(
        symbols=symbols,
        start=payload.start,
        end=payload.end,
        timeframe=payload.timeframe,
    )

    return BackfillResponse(
        symbols=[symbol.upper() for symbol in symbols],
        timeframe=payload.timeframe,
        inserted_or_updated=count,
        source="alpaca"
    )

@router.get('/bars/{symbol}', response_model=List[BarResponse])
def get_bars(
    symbol: str,
    timeframe: Timeframe = Query(default="1Day", description="Bar timeframe: 1Day, 1Hour, 15Min, or 1Min"),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return get_bars_for_symbol(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )

@router.get("/indicators/{symbol}", response_model=IndicatorResponse)
def get_indicators(
    symbol: str,
    timeframe: Timeframe = Query(default="1Day", description="Bar timeframe: 1Day, 1Hour, 15Min, or 1Min"),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    bars = get_bars_for_symbol(
        db=db,
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )
    chronological_bars = list(reversed(bars))
    return build_indicator_response(
        symbol=symbol,
        timeframe=timeframe,
        bars=chronological_bars,
    )
