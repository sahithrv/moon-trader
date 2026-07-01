from services.indicators.ema import ema
from services.indicators.rsi import rsi
from services.indicators.sma import sma
from .base import Strategy
from .signals import TradeSignal

class EmaRsiVolumeStrategy(Strategy):
    name = "ema_rsi_volume_v1"

    def __init__(
        self, 
        short_window=9,
        long_window=21,
        rsi_window=14,
        rsi_overbought=70,
        volume_window=20
    ):
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.volume_window = volume_window
    
    def generate_signal(self, symbol, bars, portfolio_state):
        if len(bars) < max(self.long_window, self.rsi_window + 1, self.volume_window):
            return TradeSignal(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                strategy_name=self.name,
                reason="Not enough bars to calculate strategy indicators",
            )
        
        closes = [bar.close for bar in bars]
        volumes = [bar.volume for bar in bars]

        short_ema_values = ema(closes, self.short_window)
        long_ema_values = ema(closes, self.long_window)
        rsi_values = rsi(closes, self.rsi_window)
        volume_avg_values = sma(volumes, self.volume_window)

        short_ema = short_ema_values[-1]
        long_ema = long_ema_values[-1]
        latest_rsi = rsi_values[-1]
        avg_volume = volume_avg_values[-1]
        latest_volume = volumes[-1]

        if short_ema is None or long_ema is None or latest_rsi is None or avg_volume is None:
            return TradeSignal(
                symbol=symbol,
                action="HOLD",
                confidence=0.0,
                strategy_name=self.name,
                reason="One or more indicators are unavailable",
            )
        
        if short_ema < long_ema:
            return TradeSignal(
                symbol=symbol,
                action="SELL",
                confidence=0.7,
                strategy_name=self.name,
                reason="Short EMA is below long EMA.",
            )

        if short_ema > long_ema and latest_rsi < self.rsi_overbought and latest_volume > avg_volume:
            return TradeSignal(
                symbol=symbol,
                action="BUY",
                confidence=0.75,
                strategy_name=self.name,
                reason="Short EMA above long EMA, RSI not overbough, and volume confirmed",
            )

        return TradeSignal(
            symbol=symbol,
            action="HOLD",
            confidence=0.5,
            strategy_name=self.name,
            reason="Conditions for BUY or SELL were not fully met",
        )