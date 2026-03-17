#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from src.delta_trader.trader import DeltaTrader

def main():
    load_dotenv()
    api_key = os.getenv('DELTA_API_KEY', '')  # Default empty for public calls
    api_secret = os.getenv('DELTA_API_SECRET', '')
    base_url = os.getenv('DELTA_BASE_URL', 'https://api.india.delta.exchange')

    trader = DeltaTrader(api_key, api_secret, base_url)

    # Test getting list of tickers for perpetual futures
    print("Fetching tickers for perpetual futures...")
    tickers = trader.get_tickers(contract_types='perpetual_futures')
    print(f"Found {len(tickers)} tickers")
    for ticker in tickers[:5]:  # Print first 5
        print(f"Symbol: {ticker['symbol']}, Mark Price: {ticker.get('mark_price', 'N/A')}, Volume: {ticker.get('volume', 'N/A')}")

    # Example usage (commented out since needs auth)
    # print("Fetching futures products...")
    # products = trader.get_futures_products()
    # print(f"Found {len(products)} perpetual futures products")

    # trader.run_strategy()

if __name__ == '__main__':
    main()