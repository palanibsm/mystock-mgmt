from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Holding:
    id: int | None
    category: str
    name: str
    symbol: str
    quantity: float
    buy_price: float
    buy_date: str | None
    currency: str
    broker: str | None
    notes: str | None


@dataclass
class PriceData:
    current_price: float
    all_time_high: float
    all_time_low: float
    trend: str  # "UP" | "DOWN" | "SIDEWAYS"


@dataclass
class EnrichedHolding:
    holding: Holding
    current_price: float
    total_invested: float
    current_value: float
    pnl: float
    pnl_pct: float
    all_time_high: float
    all_time_low: float
    trend: str
    current_value_sgd: float
