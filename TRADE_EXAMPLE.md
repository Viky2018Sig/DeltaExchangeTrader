# Multiagent System Trade Example

This document walks through a complete trading scenario using the multiagent system.

## Scenario: BTC/USD Perpetual Opportunity

### Step 1: Market Data & Opportunity Scanning

**Market Data Snapshot:**
```
Time: 2026-03-17 12:23:24

DELTA EXCHANGE (BTC/USD perpetual)
- Price: $42,500
- 24h Volume: $250M
- Open Interest: $8.5B
- Bid-Ask Spread: 0.01%
- Funding Rate: +0.045% (bullish)

BINANCE (BTC/USDT spot)
- Price: $42,480
- 24h Volume: $120M  
- Bid-Ask Spread: 0.005%

OPPORTUNITY METRICS
- Volume Premium: 2.08x (250M / 120M)
- Price Premium on Delta: +$20 (0.047%)
- Liquidity Score: Excellent (tight spreads)
```

**Scanner Decision:** ✓ PASSED
- Volume premium 2.08x > threshold 1.5x
- Volume $250M > minimum $100k
- **Status: Added to analysis queue**

---

## Step 2: Signal Generation from 5 Agents

Each agent analyzes the market independently:

### Agent 1: TrendAgent (SMA Crossover)
```python
Analysis:
- Last 5 prices: [42150, 42200, 42300, 42450, 42500]
- Last 20 prices: average = 42100
- SMA(5) = 42320
- SMA(20) = 42100

Decision: SMA(5) > SMA(20) × 1.02
- 42320 > 42100 × 1.02 = 42882?
- 42320 > 42882? NO
- Signal: HOLD (borderline)

Output AgentSignal:
{
  signal_type: 'hold',
  confidence: 0.55,
  strength: 0.45,
  reasoning: 'SMA(5) just above SMA(20) but not past 2% threshold'
}
```

### Agent 2: MomentumAgent (Rate of Change)
```python
Analysis:
- 5-period ROC: (42500 - 42300) / 42300 = +0.47%
- 10-period ROC: (42500 - 42100) / 42100 = +0.95%
- Both positive ROC values indicate momentum

Decision: Check ±3% threshold
- +0.95% > +3%? NO
- Signal: HOLD (weak momentum)

Output AgentSignal:
{
  signal_type: 'hold',
  confidence: 0.62,
  strength: 0.35,
  reasoning: 'Positive ROC but below +3% threshold'
}
```

### Agent 3: VolumeSpikAgent (Volume Analysis)
```python
Analysis:
- Current 5m volume: 250M
- Historical average: 120M
- Volume ratio: 250M / 120M = 2.08x

Decision: Threshold 2.0x
- 2.08x > 2.0x? YES
- Signal: BUY

Output AgentSignal:
{
  signal_type: 'buy',
  confidence: 0.85,
  strength: 0.78,
  reasoning: 'Volume spike 2.08x above average - capitulation or breakout'
}
```

### Agent 4: OIExpansionAgent (Open Interest)
```python
Analysis:
- Current OI: 8.5B
- OI 1-hour ago: 8.3B
- Recent expansion: (8.5B - 8.3B) / 8.3B = +2.4%
- 7-day trend OI: +12% (strong uptrend)

Decision thresholds:
- Recent +2.4% > +5%? NO
- Trend +12% > +10%? YES
- Combined signal: HOLD (conflicting)

Output AgentSignal:
{
  signal_type: 'hold',
  confidence: 0.58,
  strength: 0.52,
  reasoning: 'Trend OI strong but recent expansion weak'
}
```

### Agent 5: VolatilityBreakoutAgent (Volatility Analysis)
```python
Analysis:
- Recent volatility (5m): 0.85%
- Historical volatility (24h): 1.20%
- Ratio: 0.85 / 1.20 = 0.708
- Price position: $42,500 is at 75th percentile of 24h range

Decision:
- Vol ratio < 1.0 means compression (before breakout)
- Price at resistance level
- Combined: Signal BUY on breakout

Output AgentSignal:
{
  signal_type: 'buy',
  confidence: 0.72,
  strength: 0.68,
  reasoning: 'Volatility compression with price at resistance - breakout setup'
}
```

---

## Step 3: Consensus Generation

**ConsensusEngine aggregates signals:**

```
Agent Signals:
1. TrendAgent:      HOLD (conf: 0.55, str: 0.45)
2. MomentumAgent:   HOLD (conf: 0.62, str: 0.35)
3. VolumeSpikAgent: BUY  (conf: 0.85, str: 0.78) ← Strong buy
4. OIExpansionAgent:HOLD (conf: 0.58, str: 0.52)
5. VolatilityAgent: BUY  (conf: 0.72, str: 0.68) ← Buy

Vote Distribution:
- BUY votes: 2 (VolumeSpikAgent, VolatilityBreakoutAgent)
- SELL votes: 0
- HOLD votes: 3 (TrendAgent, MomentumAgent, OIExpansionAgent)

Weighted Scoring:
- BUY weight: (0.85 × 0.78) + (0.72 × 0.68) = 0.663 + 0.490 = 1.153
- HOLD weight: (0.55 × 0.45) + (0.62 × 0.35) + (0.58 × 0.52) = 0.248 + 0.217 + 0.302 = 0.767
- Total weight: 1.920

Normalized:
- BUY weight: 1.153 / 1.920 = 60.0%
- HOLD weight: 0.767 / 1.920 = 40.0%

CONSENSUS DECISION: BUY (60.0% strength)
- Met threshold: 60% > 50% ✓
- Met quorum: 2 agents ≥ 2 minimum ✓

ConsensusResult Output:
{
  symbol: 'BTCUSD',
  final_signal: 'buy',
  consensus_strength: 0.60,
  voting_distribution: {buy: 2, sell: 0, hold: 3},
  agent_signals: [5 AgentSignal objects]
}
```

---

## Step 4: Risk Assessment

**RiskManager evaluates trade safety:**

```python
Input Parameters:
- symbol: 'BTCUSD'
- side: 'BUY'
- current_price: $42,500
- consensus_strength: 0.60
- volatility: (250M / 42,500) = 5.88% (volume-normalized)
- portfolio_size: $10,000 (assumed)
- daily_loss_so_far: $0

Position Sizing Calculation:
1. Volatility: 5.88%
   - Stop-loss: 42500 × (1 - 5.88% × 3) = 42500 × (1 - 0.1765) = $35,499
   - Take-profit: 42500 × (1 + 5.88% × 6) = 42500 × (1 + 0.3528) = $58,499

2. Position size:
   - Risk per trade: $10,000 × 1% = $100
   - Position risk: |42500 - 35499| = $7,001
   - Position size: $100 / $7,001 = 0.0143 BTC

3. Apply limits:
   - Max position (5% portfolio): $10,000 × 0.05 / 42500 = 0.0118 BTC
   - Position size capped to: 0.0118 BTC

4. Scale by consensus:
   - Final position: 0.0118 × 0.60 = 0.0071 BTC

5. Risk/Reward validation:
   - Potential loss: $42,500 - $35,499 = $7,001
   - Potential gain: $58,499 - $42,500 = $15,999
   - Risk/reward ratio: 15,999 / 7,001 = 2.29x
   - Passes threshold: 2.29x > 2.0x minimum ✓

Safety Checks:
- Consensus strength: 0.60 > 0.60 minimum ✓
- Risk/reward: 2.29x > 2.0x minimum ✓
- Daily loss: $51 < $200 allowance ✓
- Position size: 0.0071 < 0.0118 max ✓

RiskAssessment Output - SAFE:
{
  symbol: 'BTCUSD',
  position_size: 0.0071,
  entry_price: 42500,
  stop_loss: 35499,
  take_profit: 58499,
  risk_reward_ratio: 2.29,
  is_safe: True,
  reason: 'Trade passes all risk checks'
}
```

---

## Step 5: Trade Execution

**ExecutionEngine places the order:**

```python
Pre-Execution Checks:
✓ Consensus signal: BUY
✓ Safety: is_safe = True
✓ Risk/reward ratio: 2.29x valid
✓ Account balance: Sufficient margin

Order Details:
- Exchange: Delta Exchange
- Pair: BTC/USD (perpetual)
- Side: BUY
- Type: LIMIT
- Quantity: 0.0071 BTC
- Price: $42,500
- Stop-Loss: $35,499
- Take-Profit: $58,499

API Call:
POST /v2/orders
{
  "product_id": 259,  # BTC/USD perpetual
  "limit_price": 42500,
  "quantity": 7100,    # microBTC
  "side": "BUY",
  "order_type": "POST_ONLY"
}

Response:
{
  "id": "1748293749",
  "status": "open",
  "product_id": 259,
  "limit_price": 42500,
  "quantity": 7100,
  "order_type": "POST_ONLY",
  ...
}

Execution Result - SUCCESS:
- Order ID: 1748293749
- Status: PLACED
- Timestamp: 2026-03-17T12:23:30Z

TradeSignal Output:
{
  symbol: 'BTCUSD',
  side: 'BUY',
  quantity: 0.0071,
  entry_price: 42500,
  stop_loss: 35499,
  take_profit: 58499,
  order_id: '1748293749',
  status: 'placed',
  timestamp: 2026-03-17T12:23:30Z
}
```

---

## Step 6: Position Management

**Active Position Tracking:**

```python
Active Positions:
{
  'BTCUSD': {
    'side': 'BUY',
    'quantity': 0.0071,
    'entry_price': 42500,
    'stop_loss': 35499,
    'take_profit': 58499,
    'timestamp': '2026-03-17T12:23:30Z',
    'unrealized_pnl': $0,
    'unrealized_pnl_pct': 0%
  }
}

Trade History Entry:
{
  'order_id': '1748293749',
  'signal': ConsensusResult,
  'risk_assessment': RiskAssessment,
  'execution_time': '2026-03-17T12:23:30Z',
  'status': 'active'
}
```

---

## Possible Outcomes

### OUTCOME 1: BUY Target Hit ($58,499)
```
Exit: $58,499
Gross P&L: 0.0071 × ($58,499 - $42,500) = $113.59
Risk taken: $50
Reward earned: $113.59
Risk/Reward achieved: 2.27x ✓
```

### OUTCOME 2: Stop-Loss Hit ($35,499)
```
Exit: $35,499
Gross P&L: 0.0071 × ($35,499 - $42,500) = -$49.71 ≈ -$50
Risk taken: -$50
Trade closes at maximum acceptable loss
```

### OUTCOME 3: Price Reverses ($40,000)
```
Exit: Manual closure at $40,000
PNL: 0.0071 × ($40,000 - $42,500) = -$17.75
Event: Partial loss but above stop-loss
Recovery: Can be managed with position averaging
```

---

## Key Metrics Summary

| Metric | Value | Status |
|--------|-------|--------|
| Agents Signaling BUY | 2 of 5 | Weak |
| Consensus Strength | 60% | Acceptable |  
| Risk/Reward Ratio | 2.29x | Good |
| Position Size | 0.71% portfolio | Appropriate |
| Daily Risk | 0.5% portfolio | Safe |
| Safety Check | PASS | Approved |

---

## Architecture Validation

✓ Market opportunity identified through volume analysis
✓ Multi-agent consensus generated (60% buy signal)
✓ Risk properly assessed and sized
✓ Trade executed within safety parameters
✓ Position tracked and managed
✓ Stop-loss and take-profit set

This example demonstrates the complete system working as designed.
