#!/usr/bin/env python3
"""
Multiagent trading system test and demonstration
Tests full pipeline: scanning -> analysis -> consensus -> risk assessment -> execution
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents import MultiagentOrchestrator
from src.delta_trader import DeltaTrader

def main():
    """Run multiagent system demonstration"""
    
    load_dotenv()
    
    # Get API credentials
    delta_api_key = os.getenv('DELTA_API_KEY')
    delta_api_secret = os.getenv('DELTA_API_SECRET')
    
    if not delta_api_key or not delta_api_secret:
        logger.error("Missing Delta Exchange API credentials. Check .env file")
        return
    
    logger.info("=" * 70)
    logger.info("DELTA EXCHANGE MULTIAGENT HYPER-MOMENTUM TRADING SYSTEM")
    logger.info("=" * 70)
    
    # Initialize trader
    trader = DeltaTrader(
        api_key=delta_api_key,
        api_secret=delta_api_secret
    )
    
    # Initialize multiagent orchestrator
    logger.info("Initializing multiagent orchestrator...")
    orchestrator = MultiagentOrchestrator(
        trader=trader,
        delta_api_key=delta_api_key,
        delta_api_secret=delta_api_secret,
        dry_run=True  # Set to False for actual trading
    )
    
    logger.info("✓ System initialized\n")
    
    # Run scan and analysis
    logger.info("Starting full scan and analysis pipeline...\n")
    results = orchestrator.run_scan_and_analyze(max_opportunities=5)
    
    # Display results
    print("\n" + "=" * 70)
    print("SCAN RESULTS")
    print("=" * 70)
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Opportunities Found: {len(results['signals_generated'])}")
    print(f"Trades Executed: {len(results['trades_executed'])}")
    
    # Display signal details
    if results['signals_generated']:
        print("\nConsensus Signals Generated:")
        print("-" * 70)
        for signal in results['signals_generated']:
            print(f"\n{signal.symbol}:")
            print(f"  Final Signal: {signal.final_signal.upper()}")
            print(f"  Consensus Strength: {signal.consensus_strength:.1%}")
            print(f"  Agent Votes: Buy={signal.voting_distribution['buy']}, "
                  f"Sell={signal.voting_distribution['sell']}, "
                  f"Hold={signal.voting_distribution['hold']}")
            print(f"  Agent Count: {len(signal.agent_signals)}")
    
    # Display trade details
    if results['trades_executed']:
        print("\nTrades Executed:")
        print("-" * 70)
        for trade in results['trades_executed']:
            print(f"\n{trade.symbol}:")
            print(f"  Side: {trade.side}")
            print(f"  Quantity: {trade.quantity:.4f}")
            print(f"  Entry: ${trade.entry_price:.2f}")
            print(f"  Stop Loss: ${trade.stop_loss:.2f}")
            print(f"  Take Profit: ${trade.take_profit:.2f}")
            print(f"  Status: {trade.status}")
            if trade.order_id:
                print(f"  Order ID: {trade.order_id}")
    
    # Display active positions
    positions = orchestrator.get_active_positions()
    if positions:
        print("\nActive Positions:")
        print("-" * 70)
        for symbol, position in positions.items():
            print(f"\n{symbol}:")
            print(f"  Side: {position['side']}")
            print(f"  Quantity: {position['quantity']:.4f}")
            print(f"  Entry Price: ${position['entry_price']:.2f}")
            print(f"  Stop Loss: ${position['stop_loss']:.2f}")
            print(f"  Take Profit: ${position['take_profit']:.2f}")
    
    print("\n" + "=" * 70)
    logger.info("Scan and analysis complete!")
    logger.info(f"For live trading, set dry_run=False in orchestrator initialization")
    logger.info("=" * 70)

if __name__ == '__main__':
    main()
