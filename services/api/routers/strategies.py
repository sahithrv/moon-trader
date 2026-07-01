from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.dependency import get_db
from models.strategies import RunStrategyRequest, RunStrategyResponse
from routers.data import get_bars_for_symbol
from services.strategies.registry import get_strategy
from service.signal_service import SignalService

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("/run", response_model=RunStrategyResponse)
def run_strat(
    request: RunStrategyRequest,
    db: Session = Depends(get_db),
):
    bars = get_bars_for_symbol(
        db=db,
        symbol=request.symbol,
        timeframe=request.timeframe,
        limit=request.limit,
    )

    if not bars:
        raise HTTPException(
            status_code=404,
            detail=f"No bars found for {request.symbol} {request.timeframe}",
        )

    chronological_bars = list(reversed(bars))

    strategy = get_strategy(request.strategy_name)

    portfolio_state = {
        "cash": 100000,
        "positions": {},
    }

    signal = strategy.generate_signal(
        symbol=request.symbol,
        bars=chronological_bars,
        portfolio_state=portfolio_state,
    )

    bar_timestamp = chronological_bars[-1].opened_at

    try:
        stored_signal = SignalService(db).create_signal(
            symbol=signal.symbol,
            timeframe=request.timeframe,
            strategy_name=signal.strategy_name,
            action=signal.action,
            confidence=signal.confidence,
            reason=signal.reason,
            bar_timestamp=bar_timestamp,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return RunStrategyResponse(
        signal_id=stored_signal.id,
        symbol=signal.symbol.upper(),
        timeframe=stored_signal.timeframe,
        strategy_name=stored_signal.strategy_name,
        action=stored_signal.side.upper(),
        confidence=float(stored_signal.confidence),
        reason=stored_signal.reason,
        bar_timestamp=stored_signal.bar_timestamp,
        created_at=stored_signal.created_at,
    )