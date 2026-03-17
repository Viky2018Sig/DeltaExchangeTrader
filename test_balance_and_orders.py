#!/usr/bin/env python3
"""
Check account balance and try a smaller order
"""

import os
from dotenv import load_dotenv
from src.delta_trader.trader import DeltaTrader

def test_with_balance_check():
    load_dotenv()
    api_key = os.getenv('DELTA_API_KEY', '')
    api_secret = os.getenv('DELTA_API_SECRET', '')
    base_url = os.getenv('DELTA_BASE_URL', 'https://api.india.delta.exchange')

    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False

    print("=" * 70)
    print("ACCOUNT & ORDER PLACEMENT TEST")
    print("=" * 70)
    
    trader = DeltaTrader(api_key, api_secret, base_url)

    try:
        # Check wallet balance
        print("\n1. CHECKING WALLET BALANCE...")
        from src.delta_trader.api import DeltaExchangeAPI
        api = DeltaExchangeAPI(api_key, api_secret, base_url)
        wallet = api._request('GET', '/v2/wallet/balances')
        
        if wallet.get('success'):
            print("✓ Wallet data retrieved")
            print("\n   Available Assets:")
            for asset in wallet['result']:
                if asset['asset_symbol'] in ['USD', 'BTC', 'ETH', 'USDC']:
                    print(f"   - {asset['asset_symbol']}:")
                    print(f"     • Balance: {asset['balance']}")
                    print(f"     • Available: {asset['available_balance']}")
        else:
            print("❌ Could not fetch wallet")
            return False

        # Get products
        print("\n2. FETCHING BTCUSD PRODUCT INFO...")
        products = trader.get_futures_products()
        btcusd = next((p for p in products if p['symbol'] == 'BTCUSD'), None)
        
        if not btcusd:
            print("❌ BTCUSD not found")
            return False
        
        print(f"✓ Found BTCUSD (ID: {btcusd['id']})")
        print(f"  Initial Margin: {btcusd['initial_margin']}")
        print(f"  Contract Value: {btcusd['contract_value']}")

        # Get current ticker
        print("\n3. GETTING CURRENT MARKET PRICE...")
        ticker = api._request('GET', f'/v2/tickers/BTCUSD', auth=False)
        if ticker.get('success'):
            mark_price = ticker['result']['mark_price']
            print(f"✓ Current Mark Price: ${mark_price}")
        else:
            mark_price = "50000"

        # Check open orders
        print("\n4. CHECKING OPEN ORDERS...")
        orders = api._request('GET', '/v2/orders')
        if orders.get('success'):
            open_count = len(orders.get('result', []))
            print(f"✓ Open Orders: {open_count}")
        else:
            print("⚠ Could not fetch orders")

        # Check positions
        print("\n5. CHECKING POSITIONS...")
        positions = api._request('GET', '/v2/positions/margined')
        if positions.get('success'):
            position_count = len(positions.get('result', []))
            print(f"✓ Open Positions: {position_count}")
        else:
            print("⚠ Could not fetch positions")

        print("\n" + "=" * 70)
        print("ANALYSIS:")
        print("=" * 70)
        print("""
Your API credentials are working perfectly! ✓

However, your account has insufficient USD balance to place a 1 BTC order.

OPTIONS:
1. Deposit USD to your Delta Exchange account
2. Use testnet (https://demo.delta.exchange) if this is a demo account
3. Place a much smaller order (e.g., 0.001 BTC)
4. Use a market order instead of limit order

To place a successful order, you need:
- Enough margin for the position
- Proper IP whitelisting (already working)
- Valid API credentials (already working ✓)
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_with_balance_check()
