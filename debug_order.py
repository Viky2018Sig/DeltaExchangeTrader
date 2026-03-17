#!/usr/bin/env python3
"""
Debug script for order placement - shows exact request details
"""

import os
import json
import hashlib
import hmac
import time
from dotenv import load_dotenv

def debug_order_placement():
    load_dotenv()
    api_key = os.getenv('DELTA_API_KEY', '')
    api_secret = os.getenv('DELTA_API_SECRET', '')
    base_url = os.getenv('DELTA_BASE_URL', 'https://api.india.delta.exchange')

    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return

    print("=" * 70)
    print("DEBUG: Order Placement Request Details")
    print("=" * 70)
    
    # Request details
    method = 'POST'
    path = '/v2/orders'
    timestamp = str(int(time.time()))
    
    order_data = {
        'product_id': 27,  # BTCUSD
        'size': 1,
        'side': 'buy',
        'order_type': 'limit_order',
        'limit_price': '50000'
    }
    
    payload = json.dumps(order_data)
    query_string = ''
    
    print(f"\n1. REQUEST METHOD: {method}")
    print(f"2. REQUEST PATH: {path}")
    print(f"3. TIMESTAMP: {timestamp}")
    print(f"\n4. PAYLOAD (JSON):")
    print(f"   {payload}")
    
    # Signature calculation
    signature_data = method + timestamp + path + query_string + payload
    print(f"\n5. SIGNATURE DATA (concatenated):")
    print(f"   Method: '{method}'")
    print(f"   Timestamp: '{timestamp}'")
    print(f"   Path: '{path}'")
    print(f"   Query String: '{query_string}' (empty)")
    print(f"   Payload: '{payload}'")
    print(f"   Full: '{signature_data}'")
    
    # Generate signature
    message_bytes = signature_data.encode('utf-8')
    secret_bytes = api_secret.encode('utf-8')
    signature = hmac.new(secret_bytes, message_bytes, hashlib.sha256).hexdigest()
    
    print(f"\n6. GENERATED SIGNATURE:")
    print(f"   {signature}")
    
    print(f"\n7. HEADERS THAT WILL BE SENT:")
    print(f"   api-key: {api_key}")
    print(f"   timestamp: {timestamp}")
    print(f"   signature: {signature}")
    print(f"   Content-Type: application/json")
    print(f"   User-Agent: python-delta-trader/1.0")
    
    print(f"\n8. FULL REQUEST URL:")
    print(f"   {base_url}{path}")
    
    print("\n" + "=" * 70)
    print("Attempting actual request...")
    print("=" * 70)
    
    # Now try the actual request
    import requests
    
    url = base_url + path
    headers = {
        'api-key': api_key,
        'timestamp': timestamp,
        'signature': signature,
        'User-Agent': 'python-delta-trader/1.0',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=order_data, headers=headers, timeout=10)
        print(f"\nRESPONSE STATUS: {response.status_code}")
        print(f"RESPONSE HEADERS:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print(f"\nRESPONSE BODY:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code != 200:
            print(f"\n❌ Error: {response.status_code}")
            if response.status_code == 400:
                print("   Possible causes:")
                print("   - Invalid JSON payload")
                print("   - Missing required field")
                print("   - Signature mismatch")
                print("   - Timestamp too old (>5 seconds)")
                print("   - IP not whitelisted")
        else:
            print("\n✅ Order placed successfully!")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {str(e)}")

if __name__ == '__main__':
    debug_order_placement()
