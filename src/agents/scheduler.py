"""
Automated scheduler for running market scans at regular intervals
"""

import logging
import asyncio
from typing import Callable, Optional
from datetime import datetime, timedelta
import time
import threading

logger = logging.getLogger(__name__)

class Scheduler:
    """Schedules automated market scans"""
    
    def __init__(self, interval_minutes: int = 30):
        """
        Initialize scheduler
        
        Args:
            interval_minutes: Run scan every N minutes
        """
        self.interval_minutes = interval_minutes
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.scan_callback: Optional[Callable] = None
        self.update_callback: Optional[Callable] = None
        self.scan_count = 0
        self.last_scan_time: Optional[datetime] = None
    
    def set_scan_callback(self, callback: Callable) -> None:
        """Set callback function to run on each scan"""
        self.scan_callback = callback
    
    def set_update_callback(self, callback: Callable) -> None:
        """Set callback function to update positions"""
        self.update_callback = callback
    
    def start(self) -> None:
        """Start scheduler in background thread"""
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"Scheduler started (interval: {self.interval_minutes} minutes)")
    
    def stop(self) -> None:
        """Stop scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_loop(self) -> None:
        """Main scheduler loop"""
        try:
            while self.is_running:
                self.last_scan_time = datetime.now()
                self.scan_count += 1
                
                logger.info(f"\n{'='*60}")
                logger.info(f"SCAN #{self.scan_count} - {self.last_scan_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                logger.info(f"{'='*60}")
                
                # Run scan callback
                if self.scan_callback:
                    try:
                        self.scan_callback()
                    except Exception as e:
                        logger.error(f"Error in scan callback: {e}", exc_info=True)
                
                # Run update callback every 5 minutes
                if self.scan_count % max(1, (5 // self.interval_minutes)) == 0:
                    if self.update_callback:
                        try:
                            self.update_callback()
                        except Exception as e:
                            logger.error(f"Error in update callback: {e}", exc_info=True)
                
                # Calculate next scan time
                next_scan = self.last_scan_time + timedelta(minutes=self.interval_minutes)
                sleep_seconds = (next_scan - datetime.now()).total_seconds()
                
                if sleep_seconds > 0:
                    logger.info(f"Next scan in {sleep_seconds:.0f} seconds ({next_scan.strftime('%H:%M:%S UTC')})")
                    time.sleep(sleep_seconds)
        
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            self.is_running = False
    
    def get_next_scan_time(self) -> Optional[datetime]:
        """Get next scheduled scan time"""
        if not self.last_scan_time:
            return datetime.now() + timedelta(minutes=self.interval_minutes)
        return self.last_scan_time + timedelta(minutes=self.interval_minutes)
    
    def get_scan_count(self) -> int:
        """Get total number of scans run"""
        return self.scan_count
    
    def get_uptime(self) -> Optional[str]:
        """Get scheduler uptime"""
        if not self.is_running or not self.last_scan_time:
            return None
        
        elapsed = datetime.now() - self.last_scan_time + timedelta(minutes=self.scan_count * self.interval_minutes)
        hours = elapsed.total_seconds() / 3600
        return f"{hours:.1f} hours"


class PositionUpdater:
    """Updates paper trading positions with latest market data"""
    
    def __init__(self, paper_trader, market_data_aggregator, telegram_notifier):
        """Initialize position updater"""
        self.paper_trader = paper_trader
        self.market_data_aggregator = market_data_aggregator
        self.telegram_notifier = telegram_notifier
        self.last_notification_time = {}  # Track last notification per symbol
        self.notification_interval = 3600  # 1 hour between updates
    
    def update_all_positions(self) -> None:
        """Update all active paper trading positions"""
        
        active_positions = self.paper_trader.get_active_positions()
        
        if not active_positions:
            logger.info("No active positions to update")
            return
        
        logger.info(f"Updating {len(active_positions)} active positions...")
        
        for position in active_positions:
            symbol = position['symbol']
            
            try:
                # Fetch current market data
                market_data = self._get_current_price(symbol)
                
                if not market_data:
                    logger.warning(f"Could not fetch current price for {symbol}")
                    continue
                
                current_price = market_data['price']
                
                # Update position
                self.paper_trader.update_position(symbol, current_price)
                
                # Send notification if enough time has passed
                if self._should_notify(symbol):
                    entry_time = datetime.fromisoformat(position['entry_time'])
                    days_held = (datetime.now() - entry_time).days + 1
                    
                    update_data = {
                        'symbol': symbol,
                        'side': position['side'],
                        'entry_price': position['entry_price'],
                        'current_price': current_price,
                        'stop_loss': position['stop_loss'],
                        'take_profit': position['take_profit'],
                        'days_held': days_held
                    }
                    
                    self.telegram_notifier.send_position_update(update_data)
                    self.last_notification_time[symbol] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error updating position {symbol}: {e}")
    
    def _get_current_price(self, symbol: str) -> Optional[dict]:
        """Get current market price for symbol"""
        try:
            # Try to get from Delta first
            market_data = self.market_data_aggregator.delta_feed.get_ticker(symbol)
            if market_data:
                return {'price': market_data.price}
            
            # Fallback to Binance
            binance_symbol = symbol.replace('USD', 'USDT')
            market_data = self.market_data_aggregator.binance_feed.get_ticker(binance_symbol)
            if market_data:
                return {'price': market_data.price}
            
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    
    def _should_notify(self, symbol: str) -> bool:
        """Check if it's time to send update notification"""
        if symbol not in self.last_notification_time:
            return True
        
        elapsed = (datetime.now() - self.last_notification_time[symbol]).total_seconds()
        return elapsed >= self.notification_interval
