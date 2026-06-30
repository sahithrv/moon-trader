from decimal import Decimal
from typing import List

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from clients.alpaca_market_data import AlpacaMarketDataClient
from db.models import BarORM, SymbolORM

WATCHLIST = [
    "SPY",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
    "AVGO",
    "ORCL",
    "CRM",
    "JPM",
    "V",
    "MA",
    "COST",
    "RDDT",
    "NBIS",
]

class MarketDataService:
    def __init__(self, db: Session):
        self.db = db
        self.alpaca = AlpacaMarketDataClient()

    def backfill_bars(self, symbols: List[str], start, end, timeframe: str = "1Day") -> int:
        normalized_symbols = [symbol.upper() for symbol in symbols]
        self._ensure_symbols_exist(normalized_symbols)

        #finds the row for the symbol in the DB based on what is in normalized_symbols
        symbol_rows = (
            self.db.query(SymbolORM)
            .filter(SymbolORM.symbol.in_(normalized_symbols))
            .all()
        )

        symbol_id_by_symbol = {
            row.symbol: row.id
            for row in symbol_rows
        }

        #get bars 
        barset = self.alpaca.get_bars(
            symbols = normalized_symbols,
            start=start,
            end=end,
            timeframe=timeframe,
        )

        rows = []

        for symbol, bars in barset.data.items():
            symbol_id = symbol_id_by_symbol[symbol]

            for bar in bars:
                rows.append(
                    {
                        "symbol_id": symbol_id,
                        "timeframe": timeframe,
                        "opened_at": bar.timestamp,
                        "open": Decimal(str(bar.open)),
                        "high": Decimal(str(bar.high)),
                        "low": Decimal(str(bar.low)),
                        "close": Decimal(str(bar.close)),
                        "volume": int(bar.volume),
                        "source": "alpaca"
                    }
                )
        
        if not rows:
            return 0

        stmt = insert(BarORM).values(rows)

        stmt = stmt.on_conflict_do_update(
            constraint="uq_bars_symbol_timeframe_opened_at_source",
            set_ = {
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
            },
        )

        result = self.db.execute(stmt)
        self.db.commit()
        return len(rows) or 0

    def backfill_daily_bars(self, symbols: List[str], start, end) -> int:
        return self.backfill_bars(
            symbols=symbols,
            start=start,
            end=end,
            timeframe="1Day",
        )
    

    # Make sure that symbol actually exists in DB and if not existing - adds them.
    def _ensure_symbols_exist(self, symbols: List[str]) -> None:
        existing_rows = (
            self.db.query(SymbolORM)
            .filter(SymbolORM.symbol.in_(symbols))
            .all()
        )
        #above gets the rows that are in the DB currently

        existing = {row.symbol for row in existing_rows}
        missing = [symbol for symbol in symbols if symbol not in existing]

        for symbol in missing:
            self.db.add(
                SymbolORM(
                    symbol=symbol,
                    name=None,
                    asset_type="stock",
                    exchange=None,
                    enabled=True,
                )
            )
        
        if missing:
            self.db.commit()
