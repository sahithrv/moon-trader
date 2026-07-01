from dataclasses import dataclass
from typing import Literal

SignalAction = Literal["BUY", "HOLD", "SELL"]

@dataclass
class TradeSignal:
    symbol: str
    action: SignalAction
    confidence: float
    strategy_name: str
    reason: str