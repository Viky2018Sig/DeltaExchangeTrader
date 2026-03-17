from .api import DeltaExchangeAPI
from typing import Dict, Any, Optional
import time

class DeltaTrader:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.india.delta.exchange"):
        self.api = DeltaExchangeAPI(api_key, api_secret, base_url)

    def get_futures_products(self) -> list:
        response = self.api.get_products('perpetual_futures')
        return response.get('result', [])

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        return self.api.get_ticker(symbol)

    def get_tickers(self, contract_types: Optional[str] = None, underlying_asset_symbols: Optional[str] = None, expiry_date: Optional[str] = None) -> list:
        response = self.api.get_tickers(contract_types, underlying_asset_symbols, expiry_date)
        return response.get('result', [])

    def place_limit_order(self, product_id: int, size: int, side: str, limit_price: str) -> Dict[str, Any]:
        return self.api.place_order(product_id, size, side, 'limit_order', limit_price=limit_price)

    def place_market_order(self, product_id: int, size: int, side: str) -> Dict[str, Any]:
        return self.api.place_order(product_id, size, side, 'market_order')

    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        return self.api.cancel_order(order_id)

    def get_open_orders(self, product_id: Optional[int] = None) -> list:
        response = self.api.get_orders(product_id, 'open')
        return response.get('result', [])

    def get_positions(self) -> list:
        response = self.api.get_positions()
        return response.get('result', [])

    def close_position(self, product_id: int, size: int) -> Dict[str, Any]:
        # To close, place opposite order
        positions = self.get_positions()
        for pos in positions:
            if pos['product_id'] == product_id:
                side = 'sell' if pos['size'] > 0 else 'buy'
                return self.place_market_order(product_id, abs(pos['size']), side)
        raise ValueError("Position not found")

    # Example strategy: simple moving average crossover or something, but for now, just a placeholder
    def run_strategy(self):
        # Placeholder for trading strategy
        print("Running trading strategy...")
        # For example, get BTCUSD ticker, if price > some value, buy, etc.
        # But since no real strategy, just print
        products = self.get_futures_products()
        btcusd = next((p for p in products if p['symbol'] == 'BTCUSD'), None)
        if btcusd:
            ticker = self.get_ticker('BTCUSD')
            print(f"BTCUSD Mark Price: {ticker['result']['mark_price']}")
            # Example: if mark_price < 60000, buy 1 contract
            if float(ticker['result']['mark_price']) < 60000:
                order = self.place_limit_order(btcusd['id'], 1, 'buy', '59900')
                print(f"Placed order: {order}")
        time.sleep(60)  # Wait 1 min