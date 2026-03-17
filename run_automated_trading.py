#!/usr/bin/env python3
"""
Automated trading system with Telegram notifications
Runs paper trading for 7 days to validate strategy authenticity
"""

import os
import sys
import logging
from dotenv import load_dotenv
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '...'))

from src.agents import MultiagentOrchestrator
from src.agents.telegram import TelegramNotifier
from src.agents.paper_trader import PaperTrader
from src.agents.scheduler import Scheduler, PositionUpdater
from src.agents.market_data import BinanceDataFeed, DeltaDataFeed, MarketDataAggregator
from src.delta_trader import DeltaTrader


class AutomatedTradingSystem:
    """Main automated trading system with Telegram integration"""
    
    def __init__(self, bot_token: str, chat_id: str, scan_interval_minutes: int = 30):
        """Initialize automated trading system"""
        
        load_dotenv()
        
        # Get API credentials
        delta_api_key = os.getenv('DELTA_API_KEY')
        delta_api_secret = os.getenv('DELTA_API_SECRET')
        
        if not delta_api_key or not delta_api_secret:
            raise ValueError("Missing Delta Exchange API credentials in .env")
        
        logger.info("Initializing Automated Trading System...")
        
        # Initialize components
        self.telegram = TelegramNotifier(bot_token, chat_id)
        self.paper_trader = PaperTrader()
        
        # Initialize trader and orchestrator
        self.trader = DeltaTrader(api_key=delta_api_key, api_secret=delta_api_secret)
        self.orchestrator = MultiagentOrchestrator(
            trader=self.trader,
            delta_api_key=delta_api_key,
            delta_api_secret=delta_api_secret,
            dry_run=True
        )
        
        # Initialize market data aggregator for updates
        self.market_aggregator = MarketDataAggregator(
            self.orchestrator.binance_feed,
            self.orchestrator.delta_feed
        )
        
        # Initialize scheduler and position updater
        self.scheduler = Scheduler(interval_minutes=scan_interval_minutes)
        self.position_updater = PositionUpdater(
            self.paper_trader,
            self.market_aggregator,
            self.telegram
        )
        
        # Set callbacks
        self.scheduler.set_scan_callback(self.run_market_scan)
        self.scheduler.set_update_callback(self.update_positions)
        
        self.scan_interval = scan_interval_minutes
        logger.info(f"System initialized. Scanning every {scan_interval_minutes} minutes.")
    
    def run_market_scan(self) -> None:
        """Run market scan and process signals"""
        try:
            # Run orchestrator scan
            results = self.orchestrator.run_scan_and_analyze(max_opportunities=5)
            
            signals_count = 0
            
            # Process each signal
            for consensus in results['signals_generated']:
                symbol = consensus.symbol
                
                # Skip if position already open
                if self.paper_trader.get_position(symbol):
                    logger.info(f"Position already open for {symbol}, skipping")
                    continue
                
                if consensus.final_signal == 'hold':
                    logger.debug(f"Hold signal for {symbol}, not opening position")
                    continue
                
                # Get risk assessment
                side = 'BUY' if consensus.final_signal == 'buy' else 'SELL'
                
                # Find corresponding risk assessment (re-run without trading)
                risk_assessment = self._assess_risk_for_signal(consensus, side)
                
                if not risk_assessment or not risk_assessment.is_safe:
                    logger.warning(f"Risk check failed for {symbol}")
                    continue
                
                # Open paper position
                self.paper_trader.open_position(
                    symbol=symbol,
                    side=side,
                    entry_price=risk_assessment.entry_price,
                    stop_loss=risk_assessment.stop_loss,
                    take_profit=risk_assessment.take_profit,
                    position_size=risk_assessment.position_size,
                    consensus_strength=consensus.consensus_strength,
                    agent_votes=str(consensus.voting_distribution),
                    risk_reward=risk_assessment.risk_reward_ratio
                )
                
                # Send Telegram notification
                signal_data = {
                    'symbol': symbol,
                    'side': side,
                    'entry_price': risk_assessment.entry_price,
                    'stop_loss': risk_assessment.stop_loss,
                    'take_profit': risk_assessment.take_profit,
                    'risk_reward_ratio': risk_assessment.risk_reward_ratio,
                    'consensus_strength': consensus.consensus_strength,
                    'agent_votes': consensus.voting_distribution
                }
                
                self.telegram.send_signal_notification(signal_data)
                signals_count += 1
                logger.info(f"Signal #{signals_count} sent: {symbol} {side}")
            
            # Send scan report
            scan_data = {
                'timestamp': results['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC'),
                'opportunities': len(results['signals_generated']),
                'signals_sent': signals_count,
                'active_positions': len(self.paper_trader.get_active_positions()),
                'top_coins': []
            }
            
            if signals_count > 0:
                self.telegram.send_scan_report(scan_data)
        
        except Exception as e:
            logger.error(f"Error in market scan: {e}", exc_info=True)
            self.telegram.send_error_alert(f"Scan error: {str(e)}")
    
    def update_positions(self) -> None:
        """Update all active positions"""
        try:
            self.position_updater.update_all_positions()
            
            # Check for closed positions
            closed_trades = [t for t in self.paper_trader.get_trade_history() if t.get('status') == 'closed']
            
            for trade in closed_trades[-1:]:  # Send notification for most recent closed trade
                close_data = {
                    'symbol': trade['symbol'],
                    'side': trade['side'],
                    'entry_price': trade['entry_price'],
                    'current_price': trade['exit_price'],
                    'pnl_pct': trade['pnl_pct'],
                    'reason': trade['reason'],
                    'days_held': trade['days_held']
                }
                
                self.telegram.send_close_signal(close_data)
                logger.info(f"Close signal sent for {trade['symbol']}: {trade['pnl_pct']:+.2f}%")
        
        except Exception as e:
            logger.error(f"Error updating positions: {e}", exc_info=True)
    
    def _assess_risk_for_signal(self, consensus, side):
        """Assess risk for a signal"""
        try:
            risk_assessment = self.orchestrator.risk_manager.assess_risk(
                symbol=consensus.symbol,
                side=side,
                current_price=consensus.agent_signals[0].technical_indicators.get('price', 0),
                consensus_strength=consensus.consensus_strength,
                volatility=0.05  # default 5%
            )
            return risk_assessment
        except:
            return None
    
    def send_weekly_report(self) -> None:
        """Send weekly summary report"""
        try:
            summary = self.paper_trader.get_summary()
            
            summary_data = {
                'total_signals': summary['total_trades'],
                'closed_trades': summary['closed_trades'],
                'active_trades': summary['active_trades'],
                'total_pnl_pct': summary['total_pnl_pct'],
                'win_rate': summary['win_rate'],
                'avg_risk_reward': summary['avg_risk_reward']
            }
            
            self.telegram.send_summary_report(summary_data)
            self.paper_trader.export_summary()
            
            logger.info("Weekly report sent and exported")
        except Exception as e:
            logger.error(f"Error sending weekly report: {e}")
    
    def start(self) -> None:
        """Start automated trading system"""
        try:
            logger.info("\n" + "="*70)
            logger.info("STARTING AUTOMATED TRADING SYSTEM")
            logger.info("="*70)
            logger.info(f"Mode: PAPER TRADING (7-day validation)")
            logger.info(f"Scan Interval: Every {self.scan_interval} minutes")
            logger.info(f"Telegram: Enabled")
            logger.info("="*70 + "\n")
            
            # Send startup message to Telegram
            self.telegram.send_startup_message()
            
            # Start scheduler
            self.scheduler.start()
            
            # Keep system running
            def signal_handler(sig, frame):
                logger.info("\nShutdown signal received")
                self.stop()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Sleep indefinitely
            import time
            while True:
                time.sleep(1)
        
        except Exception as e:
            logger.error(f"Error starting system: {e}", exc_info=True)
            self.telegram.send_error_alert(f"Startup error: {str(e)}")
            raise
    
    def stop(self) -> None:
        """Stop automated trading system"""
        logger.info("Stopping automated trading system...")
        self.scheduler.stop()
        self.paper_trader.save_trades()
        logger.info("System stopped. Trades saved.")


def main():
    """Main entry point"""
    
    # Check for Telegram credentials
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID') or os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        logger.error("Missing Telegram credentials!")
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
        logger.error("\nTo get these:")
        logger.error("1. Create bot with @BotFather on Telegram")
        logger.error("2. Get your Chat ID by messaging @userinfobot")
        logger.error("3. Add to .env:")
        logger.error("   TELEGRAM_BOT_TOKEN=your_bot_token")
        logger.error("   TELEGRAM_CHAT_ID=your_chat_id")
        sys.exit(1)
    
    # Optional: get scan interval from environment
    scan_interval = int(os.getenv('SCAN_INTERVAL_MINUTES', '30'))
    
    # Initialize and start system
    system = AutomatedTradingSystem(
        bot_token=bot_token,
        chat_id=chat_id,
        scan_interval_minutes=scan_interval
    )
    
    system.start()


if __name__ == '__main__':
    main()
