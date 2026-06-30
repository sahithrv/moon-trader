from datetime import datetime, timedelta, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

class BackfillRequests(BaseModel):
    symbols: List[str] = Field(default_factory=list) #makes a list for every instance instead of one shared for all instances of class
    timeframe: str = "1Day"
    start: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) - timedelta(days=60)
    )
    end: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

class BackfillResponse(BaseModel):
    symbols: List[str]
    timeframe: str
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
