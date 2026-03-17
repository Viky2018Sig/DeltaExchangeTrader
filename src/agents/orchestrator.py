"""
Multiagent orchestrator - coordinates all agents and system components
"""

from typing import List, Dict, Optional
import logging
from datetime import datetime
from .market_data import MarketDataAggregator, BinanceDataFeed, DeltaDataFeed
from .signal_agents import (
    TrendAgent, MomentumAgent, VolumeSpikAgent,
    OIExpansionAgent, VolatilityBreakoutAgent
)
from .consensus import ConsensusEngine, RiskManager
from .execution import ExecutionEngine
from .models import TradeSignal, ConsensusResult, RiskAssessment

logger = logging.getLogger(__name__)

class HyperMomentumScanner:
    """Scans for high-momentum trading opportunities across exchanges"""
    
    def __init__(
        self,
        binance_feed: BinanceDataFeed,
        delta_feed: DeltaDataFeed,
        min_volume_premium: float = 1.5,
        min_volume_usd: float = 100000
    ):
        self.binance_feed = binance_feed
        self.delta_feed = delta_feed
        self.aggregator = MarketDataAggregator(binance_feed, delta_feed)
        self.min_volume_premium = min_volume_premium
        self.min_volume_usd = min_volume_usd
    
    def scan_opportunities(self) -> List[str]:
        """Scan for high-momentum opportunities"""
        
        logger.info("Starting opportunity scan...")
        
        try:
            # Get top volume symbols from Delta
            top_symbols = self.delta_feed.get_top_volume_symbols(limit=50)
            logger.info(f"Found {len(top_symbols)} top volume symbols on Delta")
            
            opportunities = []
            
            for symbol in top_symbols:
                try:
                    comp_data = self.aggregator.get_comparative_data(
                        symbol_delta=symbol,
                        symbol_binance=self._convert_symbol_to_binance(symbol)
                    )
                    
                    if comp_data is None:
                        continue
                    
                    # Check volume premium threshold
                    if comp_data.volume_premium >= self.min_volume_premium:
                        if comp_data.delta_market.volume >= self.min_volume_usd:
                            opportunities.append(symbol)
                            logger.info(
                                f"{symbol}: {comp_data.volume_premium:.2f}x volume premium, "
                                f"Delta vol: ${comp_data.delta_market.volume:,.0f}"
                            )
                
                except Exception as e:
                    logger.debug(f"Error scanning {symbol}: {e}")
                    continue
            
            logger.info(f"Identified {len(opportunities)} high-momentum opportunities")
            return opportunities
        
        except Exception as e:
            logger.error(f"Error during scanning: {e}")
            return []
    
    def _convert_symbol_to_binance(self, delta_symbol: str) -> str:
        """Convert Delta symbol (e.g., BTCUSD) to Binance symbol (e.g., BTCUSDT)"""
        if delta_symbol.endswith('USD'):
            return delta_symbol[:-3] + 'USDT'
        return delta_symbol + 'USDT'


class MultiagentOrchestrator:
    """Orchestrates all agents and trading system"""
    
    def __init__(
        self,
        trader,
        binance_api_key: Optional[str] = None,
        delta_api_key: Optional[str] = None,
        delta_api_secret: Optional[str] = None,
        dry_run: bool = True
    ):
        # Initialize data feeds
        self.binance_feed = BinanceDataFeed()
        self.delta_feed = DeltaDataFeed(
            api_key=delta_api_key,
            api_secret=delta_api_secret
        )
        
        # Initialize scanner
        self.scanner = HyperMomentumScanner(self.binance_feed, self.delta_feed)
        
        # Initialize signal agents
        self.agents = [
            TrendAgent(),
            MomentumAgent(),
            VolumeSpikAgent(),
            OIExpansionAgent(),
            VolatilityBreakoutAgent()
        ]
        
        # Initialize consensus and risk management
        self.consensus_engine = ConsensusEngine()
        self.risk_manager = RiskManager()
        
        # Initialize execution engine
        self.execution_engine = ExecutionEngine(trader)
        
        self.dry_run = dry_run
        self.trader = trader
    
    def run_scan_and_analyze(self, max_opportunities: int = 10) -> Dict:
        """Run full scan and analysis pipeline"""
        
        logger.info("=" * 60)
        logger.info(f"Starting hyper-momentum analysis scan ({datetime.now()})")
        logger.info("=" * 60)
        
        results = {
            'timestamp': datetime.now(),
            'opportunities_found': [],
            'signals_generated': [],
            'trades_executed': []
        }
        
        try:
            # Step 1: Scan for opportunities
            opportunities = self.scanner.scan_opportunities()
            opportunities = opportunities[:max_opportunities]
            
            logger.info(f"\nAnalyzing {len(opportunities)} opportunities...")
            
            # Step 2: Analyze each opportunity
            for symbol in opportunities:
                logger.info(f"\n--- Analyzing {symbol} ---")
                
                # Get market data from both exchanges
                delta_market = self.delta_feed.get_ticker(symbol)
                binance_symbol = self.scanner._convert_symbol_to_binance(symbol)
                binance_market = self.binance_feed.get_ticker(binance_symbol)
                
                if not delta_market or not binance_market:
                    logger.warning(f"Could not fetch market data for {symbol}")
                    continue
                
                # Step 3: Run all signal agents
                agent_signals = []
                for agent in self.agents:
                    signal = agent.analyze(delta_market)
                    if signal:
                        agent_signals.append(signal)
                        logger.info(f"  {agent.__class__.__name__}: {signal.signal_type} "
                                   f"(confidence: {signal.confidence:.1%}, "
                                   f"strength: {signal.strength:.2f})")
                
                # Step 4: Generate consensus
                consensus = self.consensus_engine.generate_consensus(agent_signals, symbol)
                results['signals_generated'].append(consensus)
                
                # Step 5: Risk assessment
                if consensus.final_signal != 'hold':
                    side = 'buy' if consensus.final_signal == 'buy' else 'sell'
                    risk_assessment = self.risk_manager.assess_risk(
                        symbol=symbol,
                        side=side,
                        current_price=delta_market.price,
                        consensus_strength=consensus.consensus_strength,
                        volatility=delta_market.volume / delta_market.price if delta_market.price > 0 else 0.02
                    )
                    
                    # Step 6: Execute trade
                    if risk_assessment.is_safe:
                        trade = self.execution_engine.execute_trade(
                            consensus,
                            risk_assessment,
                            dry_run=self.dry_run
                        )
                        if trade:
                            results['trades_executed'].append(trade)
                            logger.info(f"  ✓ Trade executed: {trade.side} {trade.quantity:.4f} @ {trade.entry_price}")
                    else:
                        logger.warning(f"  ✗ Risk check failed: {risk_assessment.reason}")
            
            logger.info("\n" + "=" * 60)
            logger.info("Scan complete")
            logger.info(f"Opportunities analyzed: {len(opportunities)}")
            logger.info(f"Signals generated: {len(results['signals_generated'])}")
            logger.info(f"Trades executed: {len(results['trades_executed'])}")
            logger.info("=" * 60)
            
            return results
        
        except Exception as e:
            logger.error(f"Error during scan and analysis: {e}", exc_info=True)
            return results
    
    def get_active_positions(self) -> Dict:
        """Get active positions from execution engine"""
        return self.execution_engine.active_positions
    
    def get_trade_history(self) -> List:
        """Get trade history"""
        return self.execution_engine.get_trade_history()
    
    def close_all_positions(self) -> int:
        """Close all active positions"""
        closed_count = 0
        for symbol in list(self.execution_engine.active_positions.keys()):
            if self.execution_engine.close_position(symbol, dry_run=self.dry_run):
                closed_count += 1
        return closed_count
