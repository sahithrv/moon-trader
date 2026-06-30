from datetime import datetime, timedelta, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Timeframe = Literal["1Day", "1Hour", "15Min", "1Min"]

class BackfillRequests(BaseModel):
    symbols: List[str] = Field(default_factory=list) #makes a list for every instance instead of one shared for all instances of class
    timeframe: Timeframe = "1Day"
    start: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) - timedelta(days=60)
    )
    end: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class BackfillResponse(BaseModel):
    symbols: List[str]
    timeframe: Timeframe
    inserted_or_updated: int
    source: str = "alpaca"

class BarResponse(BaseModel):
    symbol: str
    timeframe: str
    opened_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str

class IndicatorBarResponse(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    sma_20: Optional[float]
    ema_20: Optional[float]
    rsi_14: Optional[float]
    vwap: Optional[float]
    daily_return: Optional[float]
    volatility_20: Optional[float]

class IndicatorResponse(BaseModel):
    symbol: str
    timeframe: Timeframe
    count: int
    bars: List[IndicatorBarResponse]
