import os
from datetime import datetime
from typing import List

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed

SUPPORTED_TIMEFRAMES = {
    "1Day": TimeFrame.Day,
    "1Hour": TimeFrame.Hour,
    "15Min": TimeFrame(15, TimeFrameUnit.Minute),
    "1Min": TimeFrame.Minute,
}

class AlpacaMarketDataClient:
    def __init__(self):
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_API_SECRET")
        feed_name = os.getenv("ALPACA_DATA_FEED", "iex").upper()

        if not api_key or not api_secret:
            raise RuntimeError("Missing Alpaca API credentials.")
        
        self.feed = DataFeed[feed_name]
        self.client = StockHistoricalDataClient(api_key, api_secret)
    
    def get_bars(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ):
        if timeframe not in SUPPORTED_TIMEFRAMES:
            supported = ", ".join(SUPPORTED_TIMEFRAMES)
            raise ValueError(f"Unsupported timeframe {timeframe}. Supported values: {supported}")

        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=SUPPORTED_TIMEFRAMES[timeframe],
            start=start,
            end=end,
            feed=self.feed
        )
        return self.client.get_stock_bars(request)

    def get_daily_bars(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime
    ):
        return self.get_bars(
            symbols=symbols,
            start=start,
            end=end,
            timeframe="1Day",
        )
