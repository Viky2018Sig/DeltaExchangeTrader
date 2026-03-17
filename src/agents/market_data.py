"""
Market data feed connectors for Binance and Delta Exchange
"""

import requests
from datetime import datetime
from typing import List, Optional, Dict
from .models import MarketData, ComparativeMarketData
import logging

logger = logging.getLogger(__name__)

class BinanceDataFeed:
    """Binance market data connector"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.session = requests.Session()
    
    def get_ticker(self, symbol: str) -> Optional[MarketData]:
        """Get ticker data from Binance"""
        try:
            # Convert symbol (BTC -> BTCUSDT for Binance)
            binance_symbol = f"{symbol.upper()}USDT"
            
            # Get 24h ticker
            response = self.session.get(
                f"{self.base_url}/api/v3/ticker/24hr",
                params={'symbol': binance_symbol},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            # Get order book for bid/ask
            book_response = self.session.get(
                f"{self.base_url}/api/v3/depth",
                params={'symbol': binance_symbol, 'limit': 1},
                timeout=5
            )
            book_response.raise_for_status()
            book_data = book_response.json()
            
            bid = float(book_data['bids'][0][0]) if book_data['bids'] else float(data['lastPrice'])
            ask = float(book_data['asks'][0][0]) if book_data['asks'] else float(data['lastPrice'])
            
            return MarketData(
                symbol=symbol,
                exchange='binance',
                timestamp=datetime.fromtimestamp(data['closeTime'] / 1000),
                price=float(data['lastPrice']),
                volume_24h=float(data['volume']) * float(data['lastPrice']),  # USD volume
                volume_1h=0,  # Would need extended data
                high_24h=float(data['highPrice']),
                low_24h=float(data['lowPrice']),
                bid=bid,
                ask=ask
            )
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    def get_top_gainers(self, limit: int = 50) -> List[str]:
        """Get top gaining symbols in 24h"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/ticker/24hr",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter USDT pairs and sort by percentage change
            usdt_pairs = [
                item for item in data 
                if item['symbol'].endswith('USDT') and float(item['priceChangePercent']) > 0
            ]
            usdt_pairs.sort(key=lambda x: float(x['priceChangePercent']), reverse=True)
            
            # Extract symbols and convert back (remove USDT)
            symbols = [pair['symbol'].replace('USDT', '') for pair in usdt_pairs[:limit]]
            return symbols
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []

class DeltaDataFeed:
    """Delta Exchange market data connector"""
    
    def __init__(self, api_key: str = '', api_secret: str = ''):
        self.base_url = "https://api.india.delta.exchange"
        self.session = requests.Session()
        self.api_key = api_key
        self.api_secret = api_secret
    
    def get_ticker(self, symbol: str) -> Optional[MarketData]:
        """Get ticker data from Delta Exchange"""
        try:
            # Delta uses symbol as-is (e.g., BTCUSD)
            response = self.session.get(
                f"{self.base_url}/v2/tickers/{symbol}",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                return None
            
            result = data['result']
            
            return MarketData(
                symbol=symbol,
                exchange='delta',
                timestamp=datetime.fromtimestamp(result['timestamp'] / 1e6),
                price=float(result.get('close', result.get('mark_price', 0))),
                volume_24h=float(result.get('turnover_usd', 0)),
                volume_1h=0,
                high_24h=float(result.get('high', 0)),
                low_24h=float(result.get('low', 0)),
                bid=float(result.get('quotes', {}).get('best_bid', 0)),
                ask=float(result.get('quotes', {}).get('best_ask', 0)),
                mark_price=float(result.get('mark_price', 0)),
                funding_rate=float(result.get('funding_rate', 0)),
                open_interest=float(result.get('oi', 0))
            )
        except Exception as e:
            logger.error(f"Error fetching Delta data for {symbol}: {e}")
            return None
    
    def get_futures_products(self) -> List[str]:
        """Get list of available futures products"""
        try:
            response = self.session.get(
                f"{self.base_url}/v2/products",
                params={'contract_types': 'perpetual_futures', 'states': 'live'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                return []
            
            symbols = [product['symbol'] for product in data.get('result', [])]
            return symbols
        except Exception as e:
            logger.error(f"Error fetching Delta products: {e}")
            return []
    
    def get_top_volume_symbols(self, limit: int = 50) -> List[str]:
        """Get top trading volume symbols on Delta"""
        try:
            response = self.session.get(
                f"{self.base_url}/v2/tickers",
                params={
                    'contract_types': 'perpetual_futures',
                    'page_size': limit
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                return []
            
            # Sort by volume and get symbols
            tickers = sorted(
                data.get('result', []),
                key=lambda x: float(x.get('turnover_usd', 0)),
                reverse=True
            )
            
            symbols = [ticker['symbol'] for ticker in tickers[:limit]]
            return symbols
        except Exception as e:
            logger.error(f"Error fetching Delta volume symbols: {e}")
            return []

class MarketDataAggregator:
    """Aggregates data from multiple exchanges"""
    
    def __init__(self, api_key: str = '', api_secret: str = ''):
        self.binance_feed = BinanceDataFeed()
        self.delta_feed = DeltaDataFeed(api_key, api_secret)
    
    def get_comparative_data(self, symbol: str) -> Optional[ComparativeMarketData]:
        """Get comparative market data across exchanges"""
        binance_data = self.binance_feed.get_ticker(symbol)
        delta_symbol = symbol + 'USD'  # Convert BTC -> BTCUSD for delta
        delta_data = self.delta_feed.get_ticker(delta_symbol)
        
        if not binance_data or not delta_data:
            return None
        
        volume_premium = (delta_data.volume_24h / binance_data.volume_24h) if binance_data.volume_24h > 0 else 0
        price_diff = ((delta_data.price - binance_data.price) / binance_data.price) * 100
        
        return ComparativeMarketData(
            symbol=symbol,
            timestamp=datetime.now(),
            binance_data=binance_data,
            delta_data=delta_data,
            volume_premium=volume_premium,
            price_difference=price_diff
        )
    
    def find_trading_opportunities(self, min_volume_premium: float = 1.5, limit: int = 20) -> List[str]:
        """Find symbols with high volume premium on Delta vs Binance"""
        opportunities = []
        
        # Get top symbols from delta
        delta_symbols = self.delta_feed.get_top_volume_symbols(limit * 2)
        
        for symbol_usd in delta_symbols:
            symbol = symbol_usd.replace('USD', '')
            comparative = self.get_comparative_data(symbol)
            
            if comparative and comparative.volume_premium >= min_volume_premium:
                opportunities.append(symbol)
            
            if len(opportunities) >= limit:
                break
        
        return opportunities
