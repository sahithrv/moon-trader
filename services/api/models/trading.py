from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class TradeSignal(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=6)
    side: Literal["buy", "sell", "hold"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    strategy: str
    features: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class OrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=6)
    side: Literal["buy", "sell"]
    quantity: int = Field(..., gt=0)
    order_type: Literal["market", "limit"]
    limit_price: Optional[float] = Field(default=None, gt=0)

class RiskDecision(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=6)
    approved: bool
    reason: str
    max_position_size: Optional[float] = Field(default=None, ge=0)
    risk_score = float = Field(..., ge=0.0, le=1.0)
    created_at: datetime
