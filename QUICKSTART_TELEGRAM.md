# Quick Start: Telegram Automated Trading

## Get Started in 5 Minutes

### 1️⃣ Create a Telegram Bot (2 min)

Open Telegram and message **@BotFather**:
```
/newbot
```

**BotFather will ask:**
- Choose a name: `My Delta Trader` 
- Choose a username: `my_delta_trader_bot`

**BotFather will reply with:**
```
Use this token to access the HTTP API:
1234567890:ABCDefGHIJklmnoPQRstuvWXY-zABCDeFGhI
```

**Copy this token** ← You need this!

---

### 2️⃣ Get Your Chat ID (1 min)

Open Telegram and message **@userinfobot** anything (e.g., "hi")

**Bot will reply with your ID:**
```json
{
  "id": 123456789,
  ...
}
```

**Copy this number** ← You need this!

---

### 3️⃣ Update Configuration (1 min)

Edit `.env` file in project root:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCDefGHIJklmnoPQRstuvWXY-zABCDeFGhI
TELEGRAM_CHAT_ID=123456789

# Scan every 30 minutes
SCAN_INTERVAL_MINUTES=30
```

**Save file** ✓

---

### 4️⃣ Start Automation (1 min)

Run the system:
```bash
python run_automated_trading.py
```

You should see:
```
2026-03-17 12:00:00 - __main__ - INFO - Initializing Automated Trading System...
2026-03-17 12:00:01 - __main__ - INFO - System initialized
2026-03-17 12:00:02 - src.agents.scheduler - INFO - Scheduler started (interval: 30 minutes)
```

**Check Telegram** ✓ - You should receive startup message!

---

### 5️⃣ Watch Your First Signals

Every 30 minutes, the system will:
1. Scan top momentum opportunities
2. Analyze with 5 different agents
3. Generate consensus signal
4. Send you Telegram notification with:
   - **Price Entry Level**
   - **Stop-Loss Level**
   - **Take-Profit Level**  
   - **Risk/Reward Ratio**
   - **Consensus Strength**

Track the position in your Telegram for 7 days!

---

## What You'll Receive

### Screenshot: Signal Notification
```
🟢 BUY SIGNAL: BTCUSD

📊 Price Levels:
• Entry: $42,500.00
• Stop-Loss: $35,499.00
• Take-Profit: $58,499.00

📈 Trade Metrics:
• Risk/Reward Ratio: 2.29x
• Consensus Strength: 60.0%

⏰ Time: 2026-03-17 12:23:30 UTC

💡 Paper trading mode - validating strategy
```

### Screenshot: Update Notification (Daily)
```
📍 POSITION UPDATE: BTCUSD

📈 P&L: +5.23%
• Current: $44,725.00
• Entry: $42,500.00

📊 Levels:
• Stop-Loss: $35,499.00 (25.8% away)
• Take-Profit: $58,499.00 (30.9% away)

⏱️ Held: 2.5 days
```

### Screenshot: Close Signal (After 7 days)
```
🚪 CLOSE SIGNAL: BTCUSD

✅ Final P&L: +8.56%
• Entry: $42,500.00
• Exit: $46,137.00

📊 Duration: 4.2 days
🎯 Reason: Time limit reached (7 days)
```

---

## 7-Day Validation Process

The system automatically:

| Day | Action | Telegram |
|-----|--------|----------|
| 1 | Open position | 🟢 Signal with price levels |
| 1-6 | Track price daily | 📍 Updates with P&L |
| 3 | Mid-week check | 📊 Summary so far |
| 6-7 | Close position | 🚪 Final result |
| 7 | Generate report | 📋 Weekly summary |

**After 7 days:** You'll have authentic validation of strategy!

---

## Configuration Options

### Scan More Frequently (Aggressive)
```env
SCAN_INTERVAL_MINUTES=15  # Check every 15 min instead of 30
```

### Scan Less Frequently (Conservative)
```env
SCAN_INTERVAL_MINUTES=60  # Check every hour
```

### Override Defaults
Edit `run_automated_trading.py` line 80:
```python
scanner = HyperMomentumScanner(
    min_volume_premium=1.5,     # Higher = fewer signals
    min_volume_usd=100000       # Higher = only big coins
)
```

---

## Troubleshooting

### No Telegram Messages?

**Check 1: Did you send `/start` to your bot?**
```
Go to Telegram and find your newly created bot
Send: /start
Check logs to get your chat ID
```

**Check 2: Verify credentials**
```bash
# Check .env file
cat .env | grep TELEGRAM
```

Should show:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_id_here
```

**Check 3: Check internet**
```bash
# Try sending test message manually
python -c "
from src.agents.telegram import TelegramNotifier
n = TelegramNotifier('YOUR_TOKEN', 'YOUR_ID')
n.send_message('Test!')
"
```

### System Won't Start?

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check Delta API keys in .env
cat .env | grep DELTA

# Check logs
tail -f trading_system.log
```

### Want to Stop?

Press `Ctrl+C` in terminal:
- System gracefully shuts down
- All trades saved to `paper_trades.json`
- Next run will resume from saved state

---

## After 7 Days: Next Steps

1. **Review Summary**
   ```bash
   cat paper_trading_report.json
   ```

2. **Check Performance**
   - Total P&L: Did system make money?
   - Win Rate: Percentage of winning trades?
   - Risk/Reward: Are winners bigger than losers?

3. **Decide: Live or Adjust?**
   - If results good: Ready for live trading!
   - If results bad: Adjust thresholds and re-validate
   - If mixed: Paper trade another week

4. **Enable Live Trading**
   Edit `run_automated_trading.py`:
   ```python
   dry_run=True   # Change to False for live
   ```

---

## File Structure

```
DeltaExc-Trader/
├── .env                          ← YOUR CREDENTIALS HERE
├── run_automated_trading.py      ← START THIS
├── paper_trades.json             ← Position log (auto-created)
├── trading_system.log            ← System logs
├── paper_trading_report.json     ← Weekly summary (auto-created)
└── src/agents/
    ├── telegram.py               ← Telegram module
    ├── paper_trader.py           ← Trading tracker
    ├── scheduler.py              ← Automation engine
    └── orchestrator.py           ← Strategy engine
```

---

## Example Output

After first scan, check:
1. **Terminal**: See scan results
2. **Telegram**: Receive signal notification
3. **Logs**: `trading_system.log` for details
4. **Storage**: `paper_trades.json` growing

```bash
# Watch real-time logs
tail -f trading_system.log

# Check current positions
cat paper_trades.json | jq '.positions'

# View trade history
cat paper_trades.json | jq '.trade_history'
```

---

## Support & Help

1. Read [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for detailed documentation
2. Check [TRADE_EXAMPLE.md](TRADE_EXAMPLE.md) for how system works
3. Review logs in `trading_system.log`
4. Check `.env` configuration
5. Test Telegram bot manually

---

## Ready?

```bash
# 1. Set up .env with Telegram credentials
# 2. Run the system
python run_automated_trading.py

# 3. Wait for first signal (within 30 minutes)
# 4. Check Telegram for notifications
# 5. Review results daily
# 6. After 7 days: Decide live trading readiness
```

**Good luck! 🚀**
