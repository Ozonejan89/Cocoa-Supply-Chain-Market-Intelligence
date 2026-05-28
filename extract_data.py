import pandas as pd

def fetch_cocoa_prices():
    try:
        from typing import TYPE_CHECKING
        if not TYPE_CHECKING:
            import yfinance as yf
    except Exception:
        raise ImportError("yfinance is not installed. Install it with: pip install yfinance")

    print("Fetching live cocoa market data...")
    # Ticker for Cocoa Futures on ICE
    cocoa_ticker = "CC=F"

    # Fetch historical daily data up to today
    cocoa_data = yf.download(cocoa_ticker, start="2020-01-01")

    # Reset index so 'Date' becomes a usable column
    cocoa_data.reset_index(inplace=True)

    # Ensure the index column is properly named 'Date'
    if 'index' in cocoa_data.columns:
        cocoa_data.rename(columns={'index': 'Date'}, inplace=True)

    # Save it to a CSV file as our raw data landing zone
    cocoa_data.to_csv("raw_cocoa_prices.csv", index=False)
    print("Market data saved successfully to raw_cocoa_prices.csv!")


if __name__ == "__main__":
    fetch_cocoa_prices()