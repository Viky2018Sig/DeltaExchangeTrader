# Automated Trading System with Telegram Integration

## Overview

Complete automated trading system that:
- Scans Delta Exchange perpetual futures every 30 minutes (configurable)
- Identifies high-momentum trading opportunities
- Sends signals via Telegram with price levels
- Tracks paper trades for 7 days to validate strategy
- Notifies you of position updates and close signals
- Provides weekly performance reports

## Setup Instructions

### Step 1: Create Telegram Bot

1. **Open Telegram** and find **@BotFather**
2. **Send message**: `/newbot`
3. **Choose a name** for your bot (e.g., "DeltaTraderBot")
4. **Choose a username** for your bot (e.g., "delta_trader_bot")
5. **Copy the bot token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Step 2: Get Your Chat ID

1. **Open Telegram** and find **@userinfobot**
2. **Send any message** (e.g., "hi")
3. **Copy your user ID** (a number like: `123456789`)

***Note**: You can also send `/start` to your new bot, then check the logs for the chat ID.

### Step 3: Configure Environment

1. **Copy .env.example to .env**:
   ```bash
   cp .env.example .env
   ```

2. **Edit .env** and add Telegram credentials:
   ```env
   # Telegram Configuration
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   TELEGRAM_CHAT_ID=123456789
   
   # Automation Settings
   SCAN_INTERVAL_MINUTES=30
   ```

3. **Save .env file**

### Step 4: Run Automated System

```bash
python run_automated_trading.py
```

## System Components

### TelegramNotifier (`src/agents/telegram.py`)
Sends formatted messages to your Telegram with:
- **Signal Notifications**: New buy/sell opportunities with price levels
- **Position Updates**: Current P&L, days held, distance to stop/profit
- **Close Signals**: Exit confirmation and final P&L
- **Summary Reports**: Weekly performance statistics
- **Error Alerts**: System issues and requirements

### PaperTrader (`src/agents/paper_trader.py`)
Tracks virtual trading positions:
- **Open Position**: Records entry, stops, targets
- **Update Position**: Tracks price changes and P&L
- **Close Position**: Auto-closes at 7 days, stop-loss, or take-profit
- **Trade History**: Maintains JSON log of all trades
- **Summary**: Calculates win rate, total P&L, risk/reward metrics

### Scheduler (`src/agents/scheduler.py`)
Automates the trading workflow:
- **Market Scans**: Runs every N minutes (default 30)
- **Position Updates**: Checks active trades every hour
- **Background Thread**: Runs without blocking main program
- **Callbacks**: Integrates with orchestrator and position updater

### AutomatedTradingSystem (`run_automated_trading.py`)
Orchestrates all components:
- Manual entry point for full system
- Integrates all modules
- Handles errors gracefully
- Sends alerts to Telegram

## How It Works

```
[Scheduler starts]
   ↓
Every 30 minutes:
   ├─ Run market scan (top 5 opportunities)
   ├─ Analyze with 5 agents
   ├─ Generate consensus signal
   ├─ Assess risk
   └─ If safe: Open paper position → Send Telegram signal
   
Every hour:
   ├─ Update prices for all active positions
   ├─ Check for stop-loss/take-profit hits
   ├─ Send position update to Telegram
   └─ If position closes: Send close signal with P&L

After 7 days:
   ├─ Automatically close old positions
   ├─ Export summary report
   └─ Send weekly performance to Telegram
```

## Notification Examples

### Signal Notification
```
🟢 BUY SIGNAL: BTCUSD

📊 Price Levels:
• Entry: $42,500.00
• Stop-Loss: $35,499.00
• Take-Profit: $58,499.00

📈 Trade Metrics:
• Risk/Reward Ratio: 2.29x
• Consensus Strength: 60.0%
• Agents Agreeing: {'buy': 2, 'sell': 0, 'hold': 3}

⏰ Time: 2026-03-17 12:23:30 UTC

💡 Note: Paper trading mode - validating strategy
🔔 You will be notified when position should close (7 days)
```

### Position Update
```
📍 POSITION UPDATE: BTCUSD

📈 P&L: +5.23%
• Current Price: $44,725.00
• Entry Price: $42,500.00

📊 Level Status:
• Stop-Loss: $35,499.00 (25.8% away)
• Take-Profit: $58,499.00 (30.9% away)

⏱️ Duration: 2.5 days held

⏰ Updated: 2026-03-17 14:45:00 UTC
```

### Close Signal
```
🚪 CLOSE SIGNAL: BTCUSD

✅ Final P&L: +8.56%
• Entry Price: $42,500.00
• Exit Price: $46,137.00

📊 Trade Duration: 4.2 days

🎯 Close Reason:
Position closed after 2 days (manual evaluation)

ℹ️ Strategy Validation:
Paper trading completed for BTCUSD
Results will be aggregated for authenticity check

⏰ Time: 2026-03-17 16:20:15 UTC
```

### Weekly Summary
```
📋 WEEK SUMMARY REPORT

📈 Overall Performance:
• Total P&L: +12.45%
• Closed Trades: 8
• Win Rate: 62.5%
• Avg Risk/Reward: 2.15x

📊 Signal Status:
• Total Signals Generated: 12
• Active Positions: 2
• Closed Positions: 8

🎯 Authenticity Assessment:
Strategy validation week complete!
Review results to determine readiness for live trading.

⏰ Report Generated: 2026-03-24 12:00:00 UTC
```

## Configuration Options

### Scan Interval
Control how often market scans run:

```env
# Very frequent (aggressive)
SCAN_INTERVAL_MINUTES=5

# Balanced (default)
SCAN_INTERVAL_MINUTES=30

# Low frequency (conservative)
SCAN_INTERVAL_MINUTES=60
```

### Paper Trading Duration
Default is 7 days. To change edit `src/agents/paper_trader.py`:
```python
self.validation_period_days = 7  # Change to desired days
```

### Volume Premium Threshold
Edit in `run_automated_trading.py`:
```python
scanner = HyperMomentumScanner(
    min_volume_premium=1.5,    # Change threshold here
    min_volume_usd=100000
)
```

## Monitoring the System

### View Real-time Logs
```bash
tail -f trading_system.log
```

### Check Paper Trading Progress
```bash
# View current positions and trades
cat paper_trades.json | jq
```

### Manual Telegram Test
```python
from src.agents.telegram import TelegramNotifier

notifier = TelegramNotifier(
    bot_token="YOUR_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

notifier.send_message("Test message from trading system!")
```

## Troubleshooting

### No Telegram Messages
1. **Check bot token**: Ensure `TELEGRAM_BOT_TOKEN` is correct
2. **Check chat ID**: Verify `TELEGRAM_CHAT_ID` is your user ID
3. **Check internet**: Ensure system has internet connectivity
4. **Check logs**: Review `trading_system.log` for errors

### System Crashes
1. **Check Python version**: Requires 3.8+
2. **Check dependencies**: Run `pip install -r requirements.txt`
3. **Check API keys**: Verify Delta Exchange credentials
4. **Review logs**: Check `trading_system.log` for exceptions

### No Trading Signals
1. **Check market conditions**: May not have opportunities meeting volume threshold
2. **Check logs**: Look for scan results
3. **Adjust thresholds**: Lower `min_volume_premium` in orchestrator
4. **Wait for next scan**: Default is 30 minutes between scans

### Stop System Gracefully
```bash
# Press Ctrl+C
# System will:
# - Stop scheduler
# - Save all paper trades
# - Close gracefully
```

## Performance Optimization

### Reduce API Calls
```env
# Increase scan interval
SCAN_INTERVAL_MINUTES=60
```

### Reduce Telegram Messages
- Position updates every 1 hour (built-in throttling)
- Only summary at end of week
- Errors only when they occur

### Reduce Memory Usage
- Deletes old update history after position closes
- Compresses JSON storage

## Advanced Usage

### Multiple Trading Pairs
The system already scans top 5 opportunities. To change:

Edit `run_automated_trading.py`:
```python
results = self.orchestrator.run_scan_and_analyze(max_opportunities=10)
```

### Custom Alerts
Add to `run_automated_trading.py`:
```python
if position['pnl_pct'] > 10:  # Alert on 10% profit
    self.telegram.send_message(f"🎉 {position['symbol']} up 10%!")
```

### Integration with Discord/Slack
Similar to Telegram integration. Create:
- `src/agents/discord_notifier.py`
- `src/agents/slack_notifier.py`

## Safety Features

✓ **Paper Trading Only**: No real orders placed during validation week
✓ **Risk Management**: Position sizing enforced
✓ **Auto-Close**: Positions close after 7 days
✓ **Stop-Loss**: Hard stop at calculated loss level
✓ **Error Handling**: Graceful error recovery with alerts
✓ **Position Tracking**: All trades logged permanently

## Next Steps After Validation Week

1. **Review Summary**: Check weekly report for authenticity
2. **Analyze Trades**: Review win rate, P&L, risk/reward
3. **Enable Live Trading**: Set `dry_run=False` for actual orders
4. **Start Small**: Trade small position sizes initially
5. **Monitor Closely**: Watch first few live trades

## Example: Full Workflow

```bash
# 1. Setup Telegram
# Get bot token from @BotFather
# Get chat ID from @userinfobot

# 2. Create .env file
cp .env.example .env
# Edit with your credentials

# 3. Start automated system
python run_automated_trading.py

# 4. Receive signals on Telegram for 7 days
# Check results weekly

# 5. After 7 days, review summary
# Decide if strategy is ready for live trading

# 6. If approved: set dry_run=False in orchestrator
# Start live trading with real orders
```

## Support

For issues:
1. Check `trading_system.log`
2. Verify all .env credentials
3. Ensure internet connectivity
4. Verify Telegram bot is working with test message
5. Review this documentation

## License

This system is part of the DeltaExchangeTrader project.
