from __future__ import annotations

from ai.tools.registry import ToolRegistry
from db import database as db


def register_portfolio_tools(registry: ToolRegistry) -> None:

    def get_all_holdings(category: str | None = None) -> dict:
        """Get current portfolio holdings, optionally filtered by category."""
        holdings = db.get_holdings(category)
        return {"holdings": holdings, "count": len(holdings)}

    registry.register(
        func=get_all_holdings,
        description="Get current portfolio holdings. Optionally filter by category: INDIAN_STOCK, SG_STOCK, US_STOCK, INDIAN_MF, SG_MF, PRECIOUS_METAL.",
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["INDIAN_STOCK", "SG_STOCK", "US_STOCK", "INDIAN_MF", "SG_MF", "PRECIOUS_METAL"],
                    "description": "Filter by holding category.",
                },
            },
            "required": [],
        },
    )

    def get_portfolio_summary() -> dict:
        """Get high-level portfolio summary with totals by category."""
        holdings = db.get_holdings()
        summary = {}
        total_invested = 0
        for h in holdings:
            cat = h["category"]
            if cat not in summary:
                summary[cat] = {"total_invested": 0, "count": 0, "currency": h["currency"]}
            cost = h["quantity"] * h["buy_price"]
            summary[cat]["total_invested"] += cost
            summary[cat]["count"] += 1
            total_invested += cost

        return {
            "by_category": summary,
            "total_invested": total_invested,
            "total_holdings": len(holdings),
        }

    registry.register(
        func=get_portfolio_summary,
        description="Get a high-level portfolio summary with total invested amount and breakdown by category (market/asset type).",
        parameters={"type": "object", "properties": {}, "required": []},
    )

    def get_top_performers(n: int = 5, worst: bool = False) -> dict:
        """Get top or worst performers by return percentage (based on buy price vs current cached price)."""
        holdings = db.get_holdings()
        performers = []
        for h in holdings:
            cached = db.get_cached_price(h["symbol"], ttl_minutes=1440)
            if cached and cached.get("current_price"):
                current = cached["current_price"]
                ret = (current - h["buy_price"]) / h["buy_price"] * 100
                performers.append({
                    "name": h["name"],
                    "symbol": h["symbol"],
                    "category": h["category"],
                    "buy_price": h["buy_price"],
                    "current_price": current,
                    "return_pct": round(ret, 2),
                    "currency": h["currency"],
                })
        performers.sort(key=lambda x: x["return_pct"], reverse=not worst)
        return {"performers": performers[:n], "type": "worst" if worst else "best"}

    registry.register(
        func=get_top_performers,
        description="Get the top N best or worst performing holdings by percentage return.",
        parameters={
            "type": "object",
            "properties": {
                "n": {"type": "integer", "description": "Number of results. Default 5.", "default": 5},
                "worst": {"type": "boolean", "description": "If true, return worst performers.", "default": False},
            },
            "required": [],
        },
    )

    def get_holding_detail(symbol: str) -> dict:
        """Get detailed info about a specific holding by symbol."""
        holdings = db.get_holdings()
        for h in holdings:
            if h["symbol"].upper() == symbol.upper():
                cached = db.get_cached_price(h["symbol"], ttl_minutes=1440)
                if cached:
                    h["current_price"] = cached.get("current_price")
                    h["all_time_high"] = cached.get("all_time_high")
                    h["all_time_low"] = cached.get("all_time_low")
                    h["trend"] = cached.get("trend")
                return h
        return {"error": f"No holding found with symbol {symbol}"}

    registry.register(
        func=get_holding_detail,
        description="Get detailed information about a specific holding by its ticker symbol.",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Ticker symbol (e.g. RELIANCE.NS, D05.SI, AAPL, GOLD)."},
            },
            "required": ["symbol"],
        },
    )

    def search_holdings(query: str) -> dict:
        """Search holdings by name or symbol (partial match)."""
        holdings = db.get_holdings()
        q = query.lower()
        results = [h for h in holdings if q in h["name"].lower() or q in h["symbol"].lower()]
        return {"results": results, "count": len(results)}

    registry.register(
        func=search_holdings,
        description="Search portfolio holdings by name or symbol using partial matching.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term (company name or partial ticker symbol)."},
            },
            "required": ["query"],
        },
    )

    def get_allocation_breakdown(group_by: str = "category") -> dict:
        """Get portfolio allocation breakdown by category or currency."""
        holdings = db.get_holdings()
        breakdown = {}
        for h in holdings:
            key = h.get(group_by, "unknown")
            if key not in breakdown:
                breakdown[key] = {"total_invested": 0, "count": 0}
            breakdown[key]["total_invested"] += h["quantity"] * h["buy_price"]
            breakdown[key]["count"] += 1

        grand_total = sum(v["total_invested"] for v in breakdown.values())
        for v in breakdown.values():
            v["pct"] = round(v["total_invested"] / grand_total * 100, 1) if grand_total else 0

        return {"breakdown": breakdown, "group_by": group_by, "grand_total": grand_total}

    registry.register(
        func=get_allocation_breakdown,
        description="Get portfolio allocation breakdown. Group by 'category' or 'currency'.",
        parameters={
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "string",
                    "enum": ["category", "currency"],
                    "description": "How to group. Default 'category'.",
                    "default": "category",
                },
            },
            "required": [],
        },
    )
