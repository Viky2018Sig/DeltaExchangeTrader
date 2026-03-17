# Delta Exchange Futures Trading Agent

Complete automated trading system with multiagent consensus engine and Telegram notification for Delta Exchange perpetual futures.

## 🎯 What This Does

- ✅ Scans Delta Exchange perpetual futures every 30 minutes
- ✅ Analyzes opportunities with 5 independent signal agents
- ✅ Generates consensus trading signals
- ✅ Tracks paper trades for 7 days to validate strategy
- ✅ Sends real-time signals to Telegram with price levels
- ✅ Notifies you of position updates and close signals
- ✅ Evaluates strategy authenticity before live trading

## 🚀 Quick Start (5 minutes)

See [QUICKSTART_TELEGRAM.md](QUICKSTART_TELEGRAM.md) for step-by-step setup.

**TL;DR:**
1. Create Telegram bot with [@BotFather](https://t.me/botfather)
2. Get chat ID from [@userinfobot](https://t.me/userinfobot)
3. Update `.env` with credentials
4. Run: `python run_automated_trading.py`
5. Receive signals on Telegram!

## 📚 Documentation

### For Automation & Paper Trading:
- **[QUICKSTART_TELEGRAM.md](QUICKSTART_TELEGRAM.md)** ← Start here!
  - 5-minute setup guide
  - Telegram bot creation
  - Configuration examples
  - Troubleshooting

- **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** → Complete automation guide
  - Detailed component documentation
  - Notification format examples
  - Performance tuning
  - Advanced usage

### For System Architecture:
- **[MULTIAGENT_ARCHITECTURE.md](MULTIAGENT_ARCHITECTURE.md)** → How it works
  - System design and components
  - Signal agents (5 types)
  - Consensus mechanism
  - Risk management

- **[TRADE_EXAMPLE.md](TRADE_EXAMPLE.md)** → Walk-through
  - Complete trading scenario
  - Detailed calculations
  - Signal generation flow
  - Position management

### For Setup & API:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** → Delta Exchange API setup
  - API credential creation
  - IP whitelisting
  - Authentication details

## 📋 Features

### Market Scanning
- Analyzes top 50 volume symbols on Delta Exchange
- Compares with Binance for volume premiums
- Identifies high-momentum opportunities
- Configurable volume thresholds

### Signal Generation
- **TrendAgent**: SMA crossover analysis
- **MomentumAgent**: Rate of change indicators
- **VolumeSpikAgent**: Volume spike detection
- **OIExpansionAgent**: Open interest growth
- **VolatilityBreakoutAgent**: Volatility analysis

### Consensus Decision Making
- Weighted voting from 5 agents
- Requires 2+ agents for buy/sell
- Calculates confidence strength
- Voting distribution tracking

### Risk Management
- Dynamic position sizing
- Stop-loss at 3× volatility
- Take-profit at 6× volatility
- Risk/reward minimum (2:1)
- Daily loss limits

### Telegram Notifications
- Signal notifications with price levels
- Hourly position updates
- Close signals with final P&L
- Weekly performance reports
- System status alerts

### Paper Trading Validation
- Tracks positions for 7 days
- Auto-closes at targets or time limit
- Persistent JSON storage
- Trade history and analytics
- Win rate and performance metrics

## 🔧 Installation

```bash
# Clone repository
git clone https://github.com/Viky2018Sig/DeltaExchangeTrader.git
cd DeltaExc-Trader

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp .env.example .env
# Edit .env with your credentials
```

## 🎮 Usage

### Automated System (Recommended)
```bash
python run_automated_trading.py
```

Runs continuous market scanning, signal generation, and Telegram notifications.

### Manual Testing
```bash
# Test multiagent system
python test_multiagent_system.py

# Test market data fetching  
python main.py

# Test order placement
python test_order_placement.py
```

## 📡 Configuration

**`.env` file:**
```env
# Delta Exchange API
DELTA_API_KEY=your_key_here
DELTA_API_SECRET=your_secret_here
DELTA_BASE_URL=https://api.india.delta.exchange

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Automation Settings
SCAN_INTERVAL_MINUTES=30
```

## 📊 How It Works

```
Automated Scheduler (every 30 minutes)
    ↓
Market Scan (top 5 opportunities)
    ↓
5 Signal Agents Analyze
    ↓
Consensus Engine Votes
    ↓
Risk Manager Validates
    ↓
Send Telegram Signal
    ↓
Paper Trader Opens Position
    ↓
Track for 7 Days (daily Telegram updates)
    ↓
Auto-close + Report Result
```

## 🎯 Signals Example

You'll receive notifications like:

```
🟢 BUY SIGNAL: BTCUSD

📊 Price Levels:
• Entry: $42,500.00
• Stop-Loss: $35,499.00
• Take-Profit: $58,499.00

📈 Metrics:
• Risk/Reward: 2.29x
• Consensus: 60.0%
```

## 📈 After 7 Days

Receive weekly summary:
```
📋 WEEK SUMMARY
• Total P&L: +12.45%
• Closed Trades: 8
• Win Rate: 62.5%
• Avg Risk/Reward: 2.15x
```

## ✅ API Access Status

✅ **PUBLIC ENDPOINTS:**
- Product list
- Market tickers
- Order book data

✅ **PRIVATE ENDPOINTS (authenticated):**
- Place orders ✓
- Cancel orders ✓
- View positions ✓
- Get balances ✓
- Manage margins ✓

## 🔒 Safety Features

- ✓ Paper trading only (validate before live)
- ✓ Maximum 5% position per trade
- ✓ Automatic stop-loss placement
- ✓ Risk/reward validation
- ✓ Daily loss limits
- ✓ Error handling and alerts
- ✓ Complete audit trail

## 🐛 Troubleshooting

**No Telegram messages?**
- Verify bot token and chat ID in `.env`
- Ensure internet connectivity
- Check `trading_system.log` for errors

**System won't start?**
- Check Python version (3.8+)
- Verify all dependencies: `pip install -r requirements.txt`
- Check Delta API keys in `.env`

**Want to stop?**
- Press `Ctrl+C` (graceful shutdown)
- All positions saved to `paper_trades.json`

## 📝 Project Structure

```
DeltaExc-Trader/
├── src/
│   ├── delta_trader/        # API client
│   └── agents/              # Multiagent system
│       ├── telegram.py      # Telegram notifications
│       ├── paper_trader.py  # Position tracking
│       ├── scheduler.py     # Automation engine
│       ├── orchestrator.py  # Strategy engine
│       └── ...              # Other agents
├── run_automated_trading.py # Main entry point
├── test_multiagent_system.py
├── QUICKSTART_TELEGRAM.md   # 5-min setup guide
├── AUTOMATION_GUIDE.md      # Complete guide
└── README.md                # This file
```

## 📖 Learning Path

1. **First time?** → Start with [QUICKSTART_TELEGRAM.md](QUICKSTART_TELEGRAM.md)
2. **Want details?** → Read [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)
3. **Understand system?** → See [MULTIAGENT_ARCHITECTURE.md](MULTIAGENT_ARCHITECTURE.md)
4. **See example?** → Check [TRADE_EXAMPLE.md](TRADE_EXAMPLE.md)

## 🎓 Learning Resources

- [Delta Exchange API Docs](https://docs.delta.exchange/)
- [Binance API Docs](https://binance-docs.github.io/apidocs/)
- [Technical Analysis Guide](https://school.stockcharts.com/)
