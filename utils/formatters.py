from utils.constants import CURRENCY_SYMBOLS


def format_currency(value: float, currency: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    if abs(value) >= 1_000_000:
        return f"{symbol}{value:,.0f}"
    return f"{symbol}{value:,.2f}"


def format_pnl(value: float, currency: str) -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    sign = "+" if value >= 0 else ""
    return f"{sign}{symbol}{value:,.2f}"


def format_percentage(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"
