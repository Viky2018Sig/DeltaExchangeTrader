"""
Paper trader for tracking and validating trading signals
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class PaperTrader:
    """Tracks paper trades for strategy validation"""
    
    def __init__(self, storage_file: str = "paper_trades.json"):
        """Initialize paper trader"""
        self.storage_file = Path(storage_file)
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.validation_period_days = 7
        self.load_trades()
    
    def open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        consensus_strength: float,
        agent_votes: str,
        risk_reward: float
    ) -> None:
        """Open a new paper trading position"""
        
        position = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'consensus_strength': consensus_strength,
            'agent_votes': agent_votes,
            'risk_reward': risk_reward,
            'entry_time': datetime.now().isoformat(),
            'status': 'open',
            'updates': []
        }
        
        self.positions[symbol] = position
        logger.info(f"Opened paper position: {symbol} {side} @ {entry_price}")
        self.save_trades()
    
    def update_position(
        self,
        symbol: str,
        current_price: float
    ) -> Optional[Dict]:
        """Update position with current price"""
        
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        if position['status'] != 'open':
            return position
        
        entry_price = position['entry_price']
        side = position['side']
        
        # Calculate PnL
        if side == 'BUY':
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl_pct = ((entry_price - current_price) / entry_price) * 100
        
        # Add update
        position['updates'].append({
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'pnl_pct': pnl_pct
        })
        
        # Check for close conditions
        close_reason = self._check_close_conditions(position, current_price, pnl_pct)
        
        if close_reason:
            self.close_position(symbol, current_price, close_reason)
        
        return position
    
    def _check_close_conditions(
        self,
        position: Dict,
        current_price: float,
        pnl_pct: float
    ) -> Optional[str]:
        """Check if position should be closed"""
        
        entry_time = datetime.fromisoformat(position['entry_time'])
        days_held = (datetime.now() - entry_time).days
        
        # Check time limit (7 days)
        if days_held >= self.validation_period_days:
            return f"Time limit reached ({self.validation_period_days} days)"
        
        # Check stop-loss hit
        if position['side'] == 'BUY':
            if current_price <= position['stop_loss']:
                return f"Stop-loss hit at ${current_price:,.2f}"
        else:
            if current_price >= position['stop_loss']:
                return f"Stop-loss hit at ${current_price:,.2f}"
        
        # Check take-profit hit
        if position['side'] == 'BUY':
            if current_price >= position['take_profit']:
                return f"Take-profit hit at ${current_price:,.2f}"
        else:
            if current_price <= position['take_profit']:
                return f"Take-profit hit at ${current_price:,.2f}"
        
        return None
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str
    ) -> Optional[Dict]:
        """Close a paper trading position"""
        
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        entry_price = position['entry_price']
        side = position['side']
        
        # Calculate final PnL
        if side == 'BUY':
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        else:
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100
        
        # Calculate absolute P&L
        position_value = position['position_size'] * entry_price
        pnl_amount = (pnl_pct / 100) * 10000  # Assuming $10k account
        
        # Update position
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now().isoformat()
        position['exit_reason'] = reason
        position['pnl_pct'] = pnl_pct
        position['pnl_amount'] = pnl_amount
        position['status'] = 'closed'
        
        # Move to history
        entry_time = datetime.fromisoformat(position['entry_time'])
        days_held = (datetime.now() - entry_time).days + 1
        
        trade_record = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_time': position['entry_time'],
            'exit_time': position['exit_time'],
            'days_held': days_held,
            'pnl_pct': pnl_pct,
            'pnl_amount': pnl_amount,
            'reason': reason,
            'risk_reward': position['risk_reward'],
            'consensus_strength': position['consensus_strength']
        }
        
        self.trade_history.append(trade_record)
        
        logger.info(f"Closed paper position: {symbol} - P&L: {pnl_pct:+.2f}% ({reason})")
        self.save_trades()
        
        return position
    
    def get_active_positions(self) -> List[Dict]:
        """Get all active positions"""
        return [p for p in self.positions.values() if p['status'] == 'open']
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get specific position"""
        return self.positions.get(symbol)
    
    def get_trade_history(self) -> List[Dict]:
        """Get closed trade history"""
        return self.trade_history
    
    def get_summary(self) -> Dict:
        """Get paper trading summary"""
        
        if not self.trade_history:
            return {
                'total_trades': 0,
                'closed_trades': 0,
                'active_trades': len(self.get_active_positions()),
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl_pct': 0.0,
                'avg_pnl_pct': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'avg_risk_reward': 0.0
            }
        
        closed_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t['pnl_pct'] > 0)
        losing_trades = sum(1 for t in self.trade_history if t['pnl_pct'] < 0)
        win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
        
        total_pnl_pct = sum(t['pnl_pct'] for t in self.trade_history)
        avg_pnl_pct = total_pnl_pct / closed_trades if closed_trades > 0 else 0
        
        best_trade = max((t['pnl_pct'] for t in self.trade_history), default=0)
        worst_trade = min((t['pnl_pct'] for t in self.trade_history), default=0)
        
        avg_rr = sum(t['risk_reward'] for t in self.trade_history) / closed_trades if closed_trades > 0 else 0
        
        return {
            'total_trades': closed_trades + len(self.get_active_positions()),
            'closed_trades': closed_trades,
            'active_trades': len(self.get_active_positions()),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl_pct': total_pnl_pct,
            'avg_pnl_pct': avg_pnl_pct,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'avg_risk_reward': avg_rr
        }
    
    def save_trades(self) -> None:
        """Save trades to persistent storage"""
        try:
            data = {
                'positions': self.positions,
                'trade_history': self.trade_history,
                'saved_at': datetime.now().isoformat()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Trades saved to {self.storage_file}")
        except Exception as e:
            logger.error(f"Error saving trades: {e}")
    
    def load_trades(self) -> None:
        """Load trades from persistent storage"""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.positions = data.get('positions', {})
                    self.trade_history = data.get('trade_history', [])
                logger.info(f"Loaded {len(self.positions)} positions and {len(self.trade_history)} trades")
        except Exception as e:
            logger.error(f"Error loading trades: {e}")
    
    def export_summary(self, filename: str = "paper_trading_report.json") -> None:
        """Export paper trading summary"""
        try:
            summary = {
                'summary': self.get_summary(),
                'active_positions': self.get_active_positions(),
                'closed_trades': self.get_trade_history(),
                'exported_at': datetime.now().isoformat()
            }
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Summary exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting summary: {e}")
