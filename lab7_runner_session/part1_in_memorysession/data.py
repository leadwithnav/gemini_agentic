"""
Simulated CME Market Product Dataset for Lab 1 (1A & 1B).

IMPORTANT DISCLAIMER:
---------------------
This dataset contains simulated / fictional training data for educational purposes only.
It DOES NOT connect to live CME Group production systems or reflect real-time market data.
"""

PRODUCTS = {
    "ES": {
        "symbol": "ES",
        "name": "E-mini S&P 500 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$50 x index",
        "currency": "USD",
        "trading_status": "OPEN",
        "description": "Training data for E-mini S&P 500 equity index futures contract."
    },
    "NQ": {
        "symbol": "NQ",
        "name": "E-mini Nasdaq-100 Futures",
        "asset_class": "Equity Index",
        "exchange": "CME",
        "contract_size": "$20 x index",
        "currency": "USD",
        "trading_status": "OPEN",
        "description": "Training data for E-mini Nasdaq-100 equity index futures contract."
    },
    "CL": {
        "symbol": "CL",
        "name": "Crude Oil Futures",
        "asset_class": "Energy",
        "exchange": "NYMEX",
        "contract_size": "1,000 barrels",
        "currency": "USD",
        "trading_status": "OPEN",
        "description": "Training data for Light Sweet Crude Oil futures contract."
    },
    "GC": {
        "symbol": "GC",
        "name": "Gold Futures",
        "asset_class": "Metals",
        "exchange": "COMEX",
        "contract_size": "100 troy ounces",
        "currency": "USD",
        "trading_status": "CLOSED",
        "description": "Training data for benchmark 100 troy oz Gold futures contract."
    },
    "6E": {
        "symbol": "6E",
        "name": "Euro FX Futures",
        "asset_class": "FX",
        "exchange": "CME",
        "contract_size": "125,000 EUR",
        "currency": "USD",
        "trading_status": "OPEN",
        "description": "Training data for Euro / US Dollar currency futures contract."
    },
    "ZC": {
        "symbol": "ZC",
        "name": "Corn Futures",
        "asset_class": "Agriculture",
        "exchange": "CBOT",
        "contract_size": "5,000 bushels",
        "currency": "USD",
        "trading_status": "CLOSED",
        "description": "Training data for Agricultural Corn futures contract."
    }
}
