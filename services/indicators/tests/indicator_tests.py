from services.indicators.sma import sma
from services.indicators.returns import daily_return
from services.indicators.rsi import rsi
from services.indicators.ema import ema
from services.indicators.vwap import vwap
from services.indicators.volatility import rolling_volatility


def test_sma_basic():
    assert sma([10, 20, 30, 40, 50], 3) == [None, None, 20, 30, 40]


def test_daily_return_basic():
    result = daily_return([100, 110, 99])

    assert result[0] is None
    assert round(result[1], 4) == 0.1
    assert round(result[2], 4) == -0.1


def test_indicators_return_same_length_as_input():
    closes = [100, 101, 102, 101, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]
    highs = [x + 1 for x in closes]
    lows = [x - 1 for x in closes]
    volumes = [1000 for _ in closes]

    assert len(ema(closes, 5)) == len(closes)
    assert len(rsi(closes, 14)) == len(closes)
    assert len(vwap(highs, lows, closes, volumes)) == len(closes)
    assert len(rolling_volatility(closes, 5)) == len(closes)