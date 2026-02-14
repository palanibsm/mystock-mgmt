from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime

import yfinance as yf

from db import database as db

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    timestamp: datetime
    alert_type: str  # "price_move" | "threshold"
    severity: str  # "info" | "warning" | "critical"
    symbol: str
    title: str
    description: str
    dismissed: bool = False


class AlertStore:
    def __init__(self, max_alerts: int = 50):
        self._alerts: list[Alert] = []
        self._lock = threading.Lock()
        self._max = max_alerts

    def add(self, alert: Alert) -> None:
        with self._lock:
            self._alerts.insert(0, alert)
            if len(self._alerts) > self._max:
                self._alerts = self._alerts[:self._max]

    def get_active(self) -> list[Alert]:
        with self._lock:
            return [a for a in self._alerts if not a.dismissed]

    def dismiss(self, index: int) -> None:
        with self._lock:
            active = [a for a in self._alerts if not a.dismissed]
            if 0 <= index < len(active):
                active[index].dismissed = True

    def clear_all(self) -> None:
        with self._lock:
            for a in self._alerts:
                a.dismissed = True


class MonitorAgent:
    def __init__(self, alert_store: AlertStore, interval_seconds: int = 300,
                 threshold_pct: float = 5.0):
        self._store = alert_store
        self._interval = interval_seconds
        self._threshold = threshold_pct
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Monitor started (interval: %ds, threshold: %.1f%%)", self._interval, self._threshold)

    def stop(self) -> None:
        self._running = False

    def _run(self) -> None:
        while self._running:
            try:
                self._check()
            except Exception as e:
                logger.error("Monitor check failed: %s", e)
            time.sleep(self._interval)

    def _check(self) -> None:
        holdings = db.get_holdings()
        stock_holdings = [
            h for h in holdings
            if h["category"] in ("INDIAN_STOCK", "SG_STOCK", "US_STOCK")
        ]
        if not stock_holdings:
            return

        symbols = [h["symbol"] for h in stock_holdings]
        symbol_map = {h["symbol"]: h for h in stock_holdings}

        try:
            tickers = yf.Tickers(" ".join(symbols))
            for symbol in symbols:
                try:
                    t = tickers.tickers.get(symbol)
                    if not t:
                        continue
                    hist = t.history(period="5d")
                    if hist.empty or len(hist) < 2:
                        continue

                    current = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change_pct = (current - prev) / prev * 100

                    if abs(change_pct) >= self._threshold:
                        h = symbol_map[symbol]
                        direction = "up" if change_pct > 0 else "down"
                        self._store.add(Alert(
                            timestamp=datetime.now(),
                            alert_type="price_move",
                            severity="warning" if abs(change_pct) < 10 else "critical",
                            symbol=symbol,
                            title=f"{h['name']} {direction} {abs(change_pct):.1f}%",
                            description=f"{symbol}: {prev:.2f} -> {current:.2f} ({change_pct:+.1f}%)",
                        ))

                    # Update price cache
                    db.upsert_price_cache(symbol, {
                        "current_price": current,
                        "all_time_high": None,
                        "all_time_low": None,
                        "trend": None,
                        "currency": None,
                    })

                except Exception as e:
                    logger.warning("Monitor check failed for %s: %s", symbol, e)

        except Exception as e:
            logger.error("Batch monitor fetch failed: %s", e)
