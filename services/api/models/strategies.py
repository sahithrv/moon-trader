from pydantic import BaseModel
from datetime import datetime

class RunStrategyRequest(BaseModel):
    symbol: str
    timeframe: str = "1Day"
    strategy_name: str = "ema_rsi_volume_v1"
    limit: int = 100

class RunStrategyResponse(BaseModel):
    signal_id: int
    symbol: str
    timeframe: str
    strategy_name: str
    action: str
    confidence: float
    reason: str
    bar_timestamp: datetime
    created_at: datetime