#!/usr/bin/env python3
"""
Setup guide for Delta Exchange API credentials
"""

print("""
╔═══════════════════════════════════════════════════════════════════════╗
║          Delta Exchange Trading Agent - Setup Guide                  ║
╚═══════════════════════════════════════════════════════════════════════╝

TO GET API CREDENTIALS AND TEST ORDER PLACEMENT:

1. CREATE API KEYS:
   - Go to: https://www.delta.exchange/app/account/manageapikeys
   - (For testing, use testnet: https://demo.delta.exchange)
   - Click "Create New API Key"
   - Enable "Trading" permission
   - Add your IP address to whitelist
   - Copy the API Key and Secret

2. CONFIGURE .env FILE:
   - Copy .env.example to .env:
     cp .env.example .env
   
   - Edit .env and replace with your credentials:
     DELTA_API_KEY=your_api_key_here
     DELTA_API_SECRET=your_api_secret_here
   
   - For testing on testnet, use:
     DELTA_BASE_URL=https://cdn-ind.testnet.deltaex.org

3. TEST ORDER PLACEMENT:
   - Run: python test_order_placement.py
   - This will:
     ✓ Verify API credentials
     ✓ Fetch BTCUSD product info
     ✓ Attempt to place a test buy limit order
     ✓ Show the order ID and status

4. WHAT TO EXPECT:
   - Test order: 1 BTC limit at 50000 USD (below market)
   - If successful: Order ID returned with "pending" state
   - Order won't fill at that price unless market drops
   - You can view/cancel from: https://www.delta.exchange/app/orders

5. REQUIRED PERMISSIONS:
   - "Trading" permission enabled on API key
   - "Read Data" permission (for fetching market data)

6. IMPORTANT NOTES:
   - Always test on TESTNET first!
   - API key has 5-minute timestamp window
   - Keep API secret secure (never commit to git)
   - IP whitelist is enforced for trading keys
   - Rate limits: ~1000 requests/5 minutes

╔═══════════════════════════════════════════════════════════════════════╗
║ API Endpoints Used:                                                   ║
║ - GET /v2/products (public) - List available contracts               ║
║ - GET /v2/tickers (public) - Market data                             ║
║ - POST /v2/orders (private) - Place orders (requires auth)           ║
║ - DELETE /v2/orders (private) - Cancel orders                        ║
║ - GET /v2/positions (private) - View positions                       ║
║ - GET /v2/orders (private) - View order status                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")
