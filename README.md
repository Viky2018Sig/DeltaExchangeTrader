# Delta Exchange Futures Trading Agent

A Python-based automated trading agent for Delta Exchange futures contracts.

## Features

- Connect to Delta Exchange API
- Fetch market data (tickers, products)
- **Place limit and market orders** (with proper authentication)
- Monitor positions and orders
- Cancel orders
- Basic trading strategy framework

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Get API credentials:
   - Sign up on [Delta Exchange](https://www.delta.exchange/)
   - Create API key with "Trading" permission
   - Whitelist your IP address

3. Create `.env` file:
   ```
   cp .env.example .env
   ```
   Then edit with your credentials:
   ```
   DELTA_API_KEY=your_key_here
   DELTA_API_SECRET=your_secret_here
   DELTA_BASE_URL=https://api.india.delta.exchange
   ```

4. Test order placement:
   ```
   python test_order_placement.py
   ```
   This will attempt to place a small test buy order at 50000 USD.

5. Run the trading agent:
   ```
   python main.py
   ```

## API Access Status

✅ **PUBLIC ENDPOINTS** (no auth required):
- Get products list
- Fetch market tickers
- Get orderbook data

✅ **PRIVATE ENDPOINTS** (with API key):
- **Place orders** ✓
- Cancel orders ✓
- View positions ✓
- View order status ✓
- Manage margins ✓

## Testing

1. **Market Data Test**:
   ```bash
   python main.py
   ```
   Fetches and displays BTCUSD ticker info

2. **Order Placement Test**:
   ```bash
   python test_order_placement.py
   ```
   Attempts to place a limit buy order (for testing)

## Configuration

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions.

## Usage Example

```python
from src.delta_trader.trader import DeltaTrader

trader = DeltaTrader(api_key, api_secret)

# Get market data
tickers = trader.get_tickers('perpetual_futures')

# Place an order
order = trader.place_limit_order(
    product_id=27,  # BTCUSD
    size=1,
    side='buy',
    limit_price='60000'
)

# Get positions
positions = trader.get_positions()

# Cancel order
trader.cancel_order(order_id=12345)
```

## API Reference

See [Delta Exchange API Docs](https://docs.delta.exchange/) for full API details.

## Disclaimer

This is a basic framework. Use at your own risk. Always test on testnet first before live trading.