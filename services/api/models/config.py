from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

class SymbolConfig(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=6)
    enabled: bool = True
    name: Optional[str] = None
    asset_type: Literal["stock", "etf"] = "stock"
    exchange: Optional[str] = None

class SymbolCreate(SymbolConfig):
    pass

class Symbol(SymbolConfig):
    created_at: datetime