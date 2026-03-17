#!/usr/bin/env python3
"""
Place a successful micro-order that the account can actually afford
"""

import os
from dotenv import load_dotenv
from src.delta_trader.trader import DeltaTrader
from src.delta_trader.api import DeltaExchangeAPI

def place_micro_order():
    load_dotenv()
    api_key = os.getenv('DELTA_API_KEY', '')
    api_secret = os.getenv('DELTA_API_SECRET', '')
    base_url = os.getenv('DELTA_BASE_URL', 'https://api.india.delta.exchange')

    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False

    print("=" * 70)
    print("PLACING SUCCESSFUL MICRO-ORDER")
    print("=" * 70)
    
    trader = DeltaTrader(api_key, api_secret, base_url)
    api = DeltaExchangeAPI(api_key, api_secret, base_url)

    try:
        # Get current balance
        print("\n1. Checking account balance...")
        wallet = api._request('GET', '/v2/wallet/balances')
        usd_balance = None
        for asset in wallet['result']:
            if asset['asset_symbol'] == 'USD':
                usd_balance = float(asset['available_balance'])
                print(f"   Available USD: ${usd_balance:.8f}")
                break

        if not usd_balance or usd_balance < 0.00001:
            print("❌ Insufficient balance even for micro-order")
            return False

        # Get BTCUSD product
        print("\n2. Getting BTCUSD product details...")
        products = trader.get_futures_products()
        btcusd = next((p for p in products if p['symbol'] == 'BTCUSD'), None)
        
        if not btcusd:
            print("❌ BTCUSD not found")
            return False
        
        product_id = btcusd['id']
        initial_margin = float(btcusd['initial_margin'])
        print(f"   Product ID: {product_id}")
        print(f"   Initial Margin Requirement: {initial_margin * 100}%")

        # Get current price
        print("\n3. Getting current market price...")
        ticker = api._request('GET', f'/v2/tickers/BTCUSD', auth=False)
        mark_price = float(ticker['result']['mark_price'])
        print(f"   Current BTC Price: ${mark_price:.2f}")

        # Calculate affordable size
        print("\n4. Calculating affordable order size...")
        # Margin needed = size * price * initial_margin_requirement
        # size = available_balance / (price * initial_margin_requirement)
        affordable_size = usd_balance / (mark_price * initial_margin)
        
        # Round down to ensure we have enough
        affordable_size = int(affordable_size) if affordable_size >= 1 else 0.5
        if affordable_size < 0.5:
            affordable_size = 0.5
        
        margin_needed = affordable_size * mark_price * initial_margin
        
        print(f"   Max Affordable Size: {affordable_size} contracts")
        print(f"   Margin Needed: ${margin_needed:.8f}")
        print(f"   Available Balance: ${usd_balance:.8f}")
        
        if margin_needed > usd_balance:
            print(f"\n⚠️  Still not enough balance for even 0.5 contracts")
            print(f"   Your balance of ${usd_balance:.8f} is insufficient")
            print(f"   This account appears to be for demonstration only")
            return False

        # Place the order
        print(f"\n5. Placing LIMIT order...")
        print(f"   - Size: {affordable_size} BTC")
        print(f"   - Side: BUY")
        print(f"   - Limit Price: ${mark_price * 0.98:.2f} (2% below market)")
        
        limit_price = str(mark_price * 0.98)
        
        order_response = trader.place_limit_order(
            product_id=product_id,
            size=int(affordable_size) if affordable_size >= 1 else 1,
            side='buy',
            limit_price=limit_price
        )
        
        if order_response.get('success'):
            result = order_response['result']
            print("\n✅ ORDER PLACED SUCCESSFULLY!")
            print(f"   Order ID: {result['id']}")
            print(f"   State: {result['state']}")
            print(f"   Size: {result['size']}")
            print(f"   Limit Price: ${result['limit_price']}")
            print(f"   Commission: {result.get('commission', 'N/A')}")
            return True
        else:
            error = order_response.get('error', {})
            print(f"\n❌ Order Failed")
            print(f"   Code: {error.get('code', 'Unknown')}")
            print(f"   Context: {error.get('context', {})}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    place_micro_order()
