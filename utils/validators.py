def validate_symbol(symbol: str, category: str) -> tuple[bool, str]:
    if not symbol or not symbol.strip():
        return False, "Symbol is required"
    return True, ""


def validate_quantity(qty: float) -> tuple[bool, str]:
    if qty is None or qty <= 0:
        return False, "Quantity must be a positive number"
    return True, ""


def validate_price(price: float) -> tuple[bool, str]:
    if price is None or price <= 0:
        return False, "Price must be a positive number"
    return True, ""
