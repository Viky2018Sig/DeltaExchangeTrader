#!/usr/bin/env python3
"""
Test script to check order placement capabilities
"""

import os
import json
from dotenv import load_dotenv
from src.delta_trader.trader import DeltaTrader

def test_place_order():
    load_dotenv()
    api_key = os.getenv('DELTA_API_KEY', '')
    api_secret = os.getenv('DELTA_API_SECRET', '')
    base_url = os.getenv('DELTA_BASE_URL', 'https://cdn-ind.testnet.deltaex.org')  # Use testnet

    if not api_key or not api_secret:
        print("❌ No API credentials found in .env file")
        print("   Please set DELTA_API_KEY and DELTA_API_SECRET")
        return False

    print("✓ API Credentials found")
    trader = DeltaTrader(api_key, api_secret, base_url)

    # Get available products first
    print("\nFetching BTCUSD product info...")
    try:
        products = trader.get_futures_products()
        btcusd = next((p for p in products if p['symbol'] == 'BTCUSD'), None)
        
        if not btcusd:
            print("❌ BTCUSD product not found")
            return False
        
        print(f"✓ Found BTCUSD (ID: {btcusd['id']})")
        
        # Try to place a small test order
        print("\nAttempting to place test order...")
        print("  - Product: BTCUSD")
        print("  - Side: buy")
        print("  - Size: 1 contract")
        print("  - Order Type: limit_order")
        print("  - Limit Price: 50000 (below current market)")
        
        order_response = trader.place_limit_order(
            product_id=btcusd['id'],
            size=1,
            side='buy',
            limit_price='50000'
        )
        
        if order_response.get('success'):
            print("✓ Order placed successfully!")
            print(f"  Order ID: {order_response['result']['id']}")
            print(f"  State: {order_response['result']['state']}")
            return True
        else:
            print("❌ Order placement failed")
            print(f"  Error: {order_response.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during order placement: {str(e)}")
        print(f"   Exception type: {type(e).__name__}")
        return False

if __name__ == '__main__':
    success = test_place_order()
    exit(0 if success else 1)
