# Delta Exchange Futures Trading Agent

A Python-based automated trading agent for Delta Exchange futures contracts.

## Features

- Connect to Delta Exchange API
- Fetch market data (tickers, products)
- Place limit and market orders
- Monitor positions and orders
- Basic trading strategy framework

## Setup

1. Clone or download this repository.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

4. Edit `.env` with your Delta Exchange API credentials:
   - Get API key and secret from [Delta Exchange](https://www.delta.exchange/app/account/manageapikeys)
   - For testing, use the testnet: `https://cdn-ind.testnet.deltaex.org`

5. Run the agent:
   ```
   python main.py
   ```

## Usage

The `main.py` script demonstrates basic usage. You can extend the `DeltaTrader` class to implement your own trading strategies.

## API Reference

See [Delta Exchange API Docs](https://docs.delta.exchange/) for full API details.

## Disclaimer

This is a basic framework. Use at your own risk. Always test on testnet first.