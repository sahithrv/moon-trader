from decimal import Decimal
from sqlalchemy.orm import Session
from db.models import SignalORM, SymbolORM

class SignalService:
    def __init__(self, db: Session):
        self.db=db
    
    def create_signal(
            self,
            *,
            symbol: str,
            timeframe: str,
            strategy_name: str,
            action:str,
            confidence: str,
            reason: str,
            bar_timestamp,
    ) -> SignalORM:
        normalized_symbol = symbol.upper()

        symbol_row = (
            self.db.query(SymbolORM)
            .filter(SymbolORM.symbol == normalized_symbol)
            .one_or_none()
        )

        if symbol_row is None:
            raise ValueError(f"Symbol not found: {normalized_symbol}")
        
        signal_row = SignalORM(
            symbol_id=symbol_row.id,
            side=action.lower(),
            confidence=Decimal(str(confidence)),
            strategy_name=strategy_name,
            timeframe=timeframe,
            reason=reason,
            bar_timestamp=bar_timestamp,
            features={}
        )

        self.db.add(signal_row)
        self.db.commit()
        self.db.refresh(signal_row)
        return signal_row