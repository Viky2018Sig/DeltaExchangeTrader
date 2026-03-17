# Multiagent Hyper-Momentum Trading System

## Architecture Overview

The system implements a sophisticated multiagent architecture for automated trading across Delta Exchange perpetual futures with Binance comparison:

```
┌─────────────────────────────────────────────────────────────────┐
│  Market Data Layer                                               │
│  ├─ BinanceDataFeed (public API)                                │
│  └─ DeltaDataFeed (authenticated REST)                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  Hyper-Momentum Scanner                                          │
│  ├─ Fetches top 50 volume symbols                                │
│  ├─ Identifies volume premium opportunities (>1.5x on Delta)    │
│  └─ Pre-filters candidates for analysis                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  Signal Agent Layer (5 agents analyze each opportunity)         │
│  ├─ TrendAgent: SMA crossover analysis                          │
│  ├─ MomentumAgent: Rate of change momentum                      │
│  ├─ VolumeSpikAgent: Volume explosion detection                 │
│  ├─ OIExpansionAgent: Open interest growth                       │
│  └─ VolatilityBreakoutAgent: Volatility breakout detection      │
│                                                                  │
│  Each agent generates AgentSignal with:                         │
│  - Signal type (buy/sell/hold)                                  │
│  - Confidence score (0-1)                                        │
│  - Strength metric (0-1)                                         │
│  - Technical indicators and reasoning                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  Consensus Engine                                                │
│  ├─ Aggregates all agent signals                                │
│  ├─ Weighted voting: signal_strength × confidence              │
│  ├─ Requires 2+ agents for buy/sell (quorum)                    │
│  └─ Outputs ConsensusResult with final_signal & confidence     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  Risk Manager                                                    │
│  ├─ Position sizing (% of portfolio per trade)                 │
│  ├─ Stop-loss/take-profit calculation (3x/6x volatility)       │
│  ├─ Risk/reward ratio validation (min 2:1)                     │
│  ├─ Daily loss limit enforcement                                │
│  └─ Outputs RiskAssessment with position safety check          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│  Execution Engine                                                │
│  ├─ Places limit orders on Delta Exchange                       │
│  ├─ Tracks active positions                                     │
│  ├─ Manages stop-loss and take-profit levels                   │
│  ├─ Dry-run mode for backtesting (default)                      │
│  └─ Produces TradeSignal confirmation with order ID             │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Data Models (`src/agents/models.py`)
```python
SignalStrength           # Enum: WEAK(0.2) → STRONG(0.9)
MarketData              # Exchange price/volume snapshot
ComparativeMarketData   # Dual-exchange comparison with volume_premium
AgentSignal             # Agent output: signal_type, confidence, strength
ConsensusResult         # Aggregated voting result
RiskAssessment          # Position safety evaluation
TradeSignal             # Executable trade instruction
```

### Market Data Feeds (`src/agents/market_data.py`)
- **BinanceDataFeed**: Public ticker data, top gainers, USD volume
- **DeltaDataFeed**: Perpetual futures data, open interest, volumes
- **MarketDataAggregator**: Cross-exchange comparison, opportunity detection

### Signal Agents (`src/agents/signal_agents.py`)
Each agent analyzes market data and generates trading signals:

1. **TrendAgent**: Detects trend reversals using SMA crossover (5/20)
2. **MomentumAgent**: Measures price acceleration with ROC(5,10)
3. **VolumeSpikAgent**: Identifies volume explosions (2x multiplier)
4. **OIExpansionAgent**: Tracks perpetual open interest growth
5. **VolatilityBreakoutAgent**: Detects volatility expansion trades

### Consensus Engine (`src/agents/consensus.py`)
```python
ConsensusEngine
├─ generate_consensus(agent_signals) → ConsensusResult
│  └─ Weighted voting: buy/sell need 2+ agents + 50% weight
└─ Voting distribution tracking

RiskManager  
├─ assess_risk(symbol, side, price, consensus_strength) → RiskAssessment
├─ Position sizing: 5% portfolio max per position
├─ Stop-loss: 3× volatility below entry
├─ Take-profit: 6× volatility above entry
└─ Risk/reward minimum: 2:1 ratio
```

### Execution Engine (`src/agents/execution.py`)
```python
ExecutionEngine
├─ execute_trade(consensus, risk_assessment) → TradeSignal
│  │
│  ├─ Pre-execution: safety checks
│  ├─ Execution: place limit orders on Delta
│  ├─ Tracking: maintain active_positions dict
│  └─ History: log all trades
│
├─ get_position_status(symbol) → position details
├─ close_position(symbol) → confirmation
└─ get_trade_history() → all trades
```

### Orchestrator (`src/agents/orchestrator.py`)
```
HyperMomentumScanner
├─ scan_opportunities() → high-volume premium symbols
└─ Filters by min_volume_premium (default 1.5x) and min_volume

MultiagentOrchestrator
├─ run_scan_and_analyze()
│  ├─ 1. Scan for opportunities
│  ├─ 2. Fetch market data for each
│  ├─ 3. Run all 5 signal agents
│  ├─ 4. Generate consensus
│  ├─ 5. Risk assessment
│  └─ 6. Execute trade (if safe)
│
├─ get_active_positions()
├─ get_trade_history()
└─ close_all_positions()
```

## Usage

### Quick Start
```python
from src.agents import MultiagentOrchestrator
from src.delta_trader import DeltaTrader

# Initialize system
trader = DeltaTrader(api_key=..., api_secret=...)
orchestrator = MultiagentOrchestrator(
    trader=trader,
    delta_api_key=...,
    delta_api_secret=...,
    dry_run=True  # Set to False for live trading
)

# Run full analysis
results = orchestrator.run_scan_and_analyze(max_opportunities=5)

# results contains:
# - results['signals_generated']: ConsensusResult objects
# - results['trades_executed']: TradeSignal objects
```

### Running the Test
```bash
python test_multiagent_system.py
```

Output shows:
- Opportunities scanned
- Consensus signals generated
- Trades executed (dry-run or live)
- Active positions
- Risk assessment details

## Key Design Decisions

1. **Consensus Voting**: Requires 2+ agents for buy/sell signal (prevents false signals from single agents)

2. **Position Sizing**: Dynamic based on:
   - Account balance
   - Consensus strength
   - Volatility
   - Risk/reward ratio
   
3. **Risk Controls**:
   - No single position > 5% portfolio
   - Risk/reward minimum 2:1
   - Daily loss limit: 2% portfolio
   - Stop-loss placement: 3× volatility below entry

4. **Dry-Run Default**: System runs in simulation mode by default for safety and backtesting

5. **Cross-Exchange Advantage**: Scans volume premiums between Delta (leverage) and Binance (spot) to identify opportunities

## Data Flow Example

```
BTC/USD perpetual has 2x volume premium on Delta vs Binance
  ↓
HyperMomentumScanner identifies $50M+ volume with 2.0x premium
  ↓
5 Signal Agents analyze:
- TrendAgent: bullish divergence (0.7 confidence, 0.8 strength)
- MomentumAgent: positive ROC acceleration (0.8 confidence, 0.6 strength)
- VolumeSpikAgent: 2.5x volume spike (0.6 confidence, 0.7 strength)
- OIExpansionAgent: +5% OI expansion (0.7 confidence, 0.5 strength)
- VolatilityBreakoutAgent: breakout conditions (0.5 confidence, 0.4 strength)
  ↓
ConsensusEngine votes: 5 agents → buy signal (91% consensus)
  ↓
RiskManager calculates:
- Entry: $42,000
- Stop-loss: $40,500 (3x vol)
- Take-profit: $44,500 (6x vol)
- Position size: 0.05 BTC (0.24x portfolio)
- Risk/reward: 4.0 (passes 2:1 minimum)
  ↓
ExecutionEngine places order: BUY 0.05 BTC @ $42,000
```

## Configuration

Tune scanner thresholds in `orchestrator.py`:
```python
scanner = HyperMomentumScanner(
    min_volume_premium=1.5,   # Minimum 1.5x volume on Delta vs Binance
    min_volume_usd=100000     # Minimum $100k daily volume on Delta
)
```

Tune risk parameters:
```python
risk_manager = RiskManager(
    max_position_size=0.05,    # 5% of portfolio per position
    max_daily_loss=0.02,       # 2% daily loss limit
    min_risk_reward=2.0        # Minimum 2:1 ratio
)
```

## Testing & Validation

✓ Data feed integration (Binance + Delta)
✓ Signal generation (5 agents working)
✓ Consensus calculation (weighted voting)
✓ Risk assessment (position sizing, stops)
✓ Execution framework (order placement ready)
✓ Dry-run simulation mode
✓ Full pipeline integration test

## Next Steps for Production

1. Add WebSocket real-time data feeds (current: REST polling)
2. Implement LiquidationHeatmapAgent (6th agent for liquidation clustering)
3. Add backtesting engine with historical data
4. Implement position monitoring and rebalancing
5. Add notifications (email/Discord for trades)
6. Optimize consensus thresholds based on live performance
7. Add multi-timeframe analysis
8. Implement stop-loss/take-profit triggers

## Notes

- System defaults to dry_run=True for safety
- Account balance: $0.000043 (test account)
- All orders use limit orders (not market)
- Position history tracked per symbol
- Full logging for debugging and audit trail
