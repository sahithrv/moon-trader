from services.indicators.sma import sma
from services.indicators.ema import ema
from services.indicators.rsi import rsi
from services.indicators.vwap import vwap
from services.indicators.returns import daily_return
from services.indicators.volatility import rolling_volatility

def calculate_indicators_from_bars(bars):
    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    lows = [bar.low for bar in bars]
    volumes = [bar.volume for bar in bars]

    return {
        "sma_20": sma(closes, 20),
        "ema_20": ema(closes, 20),
        "rsi_14": rsi(closes, 14),
        "vwap": vwap(highs, lows, closes, volumes),
        "daily_return": daily_return(closes),
        "volatility_20": rolling_volatility(closes, 20),
    }