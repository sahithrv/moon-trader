from abc import ABC, abstractmethod
from .signals import TradeSignal

class Strategy(ABC):
    name: str

    @abstractmethod
    def generate_signal(self, symbol, bars, portfolio_state) -> TradeSignal:
        pass