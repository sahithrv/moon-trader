import os
from datetime import datetime
from typing import List

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

class AlpacaMarketDataClient:
    def __init__(self):
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_API_SECRET")

        if not api_key or not api_secret:
            raise RuntimeError("Missing Alpaca API credentials.")
        
        self.client = StockHistoricalDataClient(api_key, api_secret)
    
    def get_daily_bars(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime
    ):
        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start,
            end=end,
        )
        return self.client.get_stock_bars(request)