from enum import Enum


class Category(str, Enum):
    INDIAN_STOCK = "INDIAN_STOCK"
    SG_STOCK = "SG_STOCK"
    US_STOCK = "US_STOCK"
    INDIAN_MF = "INDIAN_MF"
    SG_MF = "SG_MF"
    PRECIOUS_METAL = "PRECIOUS_METAL"


CATEGORY_LABELS = {
    Category.INDIAN_STOCK: "Indian Stocks (NSE/BSE)",
    Category.SG_STOCK: "Singapore Stocks (SGX)",
    Category.US_STOCK: "US Stocks (NYSE/NASDAQ)",
    Category.INDIAN_MF: "Indian Mutual Funds (Zerodha)",
    Category.SG_MF: "Singapore Mutual Funds (Tiger Trade)",
    Category.PRECIOUS_METAL: "Precious Metals (OCBC)",
}

CATEGORY_CURRENCIES = {
    Category.INDIAN_STOCK: "INR",
    Category.SG_STOCK: "SGD",
    Category.US_STOCK: "USD",
    Category.INDIAN_MF: "INR",
    Category.SG_MF: "SGD",
    Category.PRECIOUS_METAL: "SGD",
}

CURRENCY_SYMBOLS = {
    "INR": "\u20b9",
    "SGD": "S$",
    "USD": "$",
}

EXCHANGE_SUFFIXES = {
    "NSE": ".NS",
    "BSE": ".BO",
    "SGX": ".SI",
    "NYSE": "",
    "NASDAQ": "",
}

TROY_OZ_TO_GRAMS = 31.1035

DB_PATH = "db/portfolio.db"
