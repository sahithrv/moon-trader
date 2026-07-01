from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

class SymbolORM(Base):
    __tablename__ = "symbols"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False, default="stock")
    exchange: Mapped[str] = mapped_column(String(64), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    bars: Mapped[list["BarORM"]] = relationship(back_populates="symbol")
    signals: Mapped[list["SignalORM"]] = relationship(back_populates="symbol")
    orders: Mapped[list["OrderORM"]] = relationship(back_populates="symbol")
    positions: Mapped[list["PositionORM"]] = relationship(back_populates="symbol")
    backtests: Mapped[list["BacktestORM"]] = relationship(back_populates="symbol")

class BarORM(Base):
    __tablename__ = "bars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), nullable=False, index=True)

    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    open: Mapped[Decimal] = mapped_column(Numeric(18,6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="alpaca")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    symbol: Mapped["SymbolORM"] = relationship(back_populates="bars")

    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "opened_at", "source", name="uq_bars_symbol_timeframe_opened_at_source"),
        Index("ix_bars_symbol_timeframe_opened_at", "symbol_id", "timeframe", "opened_at"),
    )

class SignalORM(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), nullable=False, index=True)

    side: Mapped[str] = mapped_column(String(16), nullable=False)  # buy, sell, hold
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(128), nullable=False)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    symbol: Mapped["SymbolORM"] = relationship(back_populates="signals")
    risk_decisions: Mapped[list["RiskDecisionORM"]] = relationship(back_populates="signal")
    orders: Mapped[list["OrderORM"]] = relationship(back_populates="signal")
    llm_memos: Mapped[list["LlmMemoORM"]] = relationship(back_populates="signal")
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    bar_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_signals_symbol_created_at", "symbol_id", "created_at"),
        Index("ix_signals_strategy_created_at", "strategy_name", "created_at"),
    )


class RiskDecisionORM(Base):
    __tablename__ = "risk_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    signal_id: Mapped[int] = mapped_column(ForeignKey("signals.id"), nullable=False, index=True)

    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    max_position_size: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    signal: Mapped["SignalORM"] = relationship(back_populates="risk_decisions")

    __table_args__ = (
        Index("ix_risk_decisions_signal_created_at", "signal_id", "created_at"),
    )


class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    signal_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("signals.id"),
        nullable=True,
        index=True,
    )
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), nullable=False, index=True)

    side: Mapped[str] = mapped_column(String(16), nullable=False)  # buy, sell
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False, default="market")
    limit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    broker_order_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)

    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    signal: Mapped[Optional["SignalORM"]] = relationship(back_populates="orders")
    symbol: Mapped["SymbolORM"] = relationship(back_populates="orders")
    fills: Mapped[list["FillORM"]] = relationship(back_populates="order")

    __table_args__ = (
        Index("ix_orders_symbol_created_at", "symbol_id", "created_at"),
        Index("ix_orders_status_created_at", "status", "created_at"),
    )


class FillORM(Base):
    __tablename__ = "fills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    filled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["OrderORM"] = relationship(back_populates="fills")

    __table_args__ = (
        Index("ix_fills_order_filled_at", "order_id", "filled_at"),
    )


class PositionORM(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbols.id"), nullable=False, index=True)

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    average_entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)

    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        index=True,
    )

    symbol: Mapped["SymbolORM"] = relationship(back_populates="positions")

    __table_args__ = (
        UniqueConstraint("symbol_id", name="uq_positions_symbol_id"),
    )


class LlmMemoORM(Base):
    __tablename__ = "llm_memos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    signal_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("signals.id"),
        nullable=True,
        index=True,
    )

    memo_type: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    signal: Mapped[Optional["SignalORM"]] = relationship(back_populates="llm_memos")

    __table_args__ = (
        Index("ix_llm_memos_signal_created_at", "signal_id", "created_at"),
        Index("ix_llm_memos_type_created_at", "memo_type", "created_at"),
    )


class BacktestORM(Base):
    __tablename__ = "backtests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("symbols.id"),
        nullable=True,
        index=True,
    )

    strategy_name: Mapped[str] = mapped_column(String(128), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    initial_cash: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    final_cash: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    total_return: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    max_drawdown: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    sharpe_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)

    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    symbol: Mapped[Optional["SymbolORM"]] = relationship(back_populates="backtests")

    __table_args__ = (
        Index("ix_backtests_strategy_created_at", "strategy_name", "created_at"),
        Index("ix_backtests_symbol_strategy", "symbol_id", "strategy_name"),
    )


class AppEventORM(Base):
    __tablename__ = "app_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    target_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    __table_args__ = (
        Index("ix_app_events_type_created_at", "event_type", "created_at"),
    )


