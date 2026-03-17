"""
Execution engine for placing orders based on consensus and risk assessment
"""

from typing import Optional, Dict, List
from datetime import datetime
import logging
from .models import TradeSignal, ConsensusResult, RiskAssessment

logger = logging.getLogger(__name__)

class ExecutionEngine:
    """Executes trades based on consensus and risk assessment"""
    
    def __init__(self, trader):
        """Initialize with DeltaTrader instance"""
        self.trader = trader
        self.active_positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
    
    def execute_trade(
        self,
        consensus_result: ConsensusResult,
        risk_assessment: RiskAssessment,
        dry_run: bool = True
    ) -> Optional[TradeSignal]:
        """Execute trade if consensus and risk checks pass"""
        
        symbol = consensus_result.symbol
        final_signal = consensus_result.final_signal
        
        # Skip hold signals
        if final_signal == 'hold':
            logger.info(f"Hold signal for {symbol}, skipping execution")
            return None
        
        # Verify safety
        if not risk_assessment.is_safe:
            logger.warning(
                f"Risk assessment failed for {symbol}: {risk_assessment.reason}"
            )
            return None
        
        # Determine side
        side = 'BUY' if final_signal == 'buy' else 'SELL'
        quantity = risk_assessment.position_size
        price = risk_assessment.entry_price
        
        logger.info(
            f"Executing {side} {quantity:.4f} {symbol} @ {price} "
            f"(Stop: {risk_assessment.stop_loss}, Target: {risk_assessment.take_profit})"
        )
        
        if dry_run:
            logger.info("DRY RUN - Not placing actual order")
            trade_signal = TradeSignal(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry_price=price,
                stop_loss=risk_assessment.stop_loss,
                take_profit=risk_assessment.take_profit,
                timestamp=datetime.now(),
                order_id=None,
                status='simulated'
            )
        else:
            try:
                # Place actual order
                if side == 'BUY':
                    order_response = self.trader.place_limit_order(
                        symbol=symbol,
                        side='BUY',
                        size=quantity,
                        price=price
                    )
                else:
                    order_response = self.trader.place_limit_order(
                        symbol=symbol,
                        side='SELL',
                        size=quantity,
                        price=price
                    )
                
                order_id = order_response.get('id') if order_response else None
                
                trade_signal = TradeSignal(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry_price=price,
                    stop_loss=risk_assessment.stop_loss,
                    take_profit=risk_assessment.take_profit,
                    timestamp=datetime.now(),
                    order_id=order_id,
                    status='placed'
                )
                
                logger.info(f"Order placed successfully: {order_id}")
                
            except Exception as e:
                logger.error(f"Failed to place order: {e}")
                trade_signal = TradeSignal(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry_price=price,
                    stop_loss=risk_assessment.stop_loss,
                    take_profit=risk_assessment.take_profit,
                    timestamp=datetime.now(),
                    order_id=None,
                    status='failed'
                )
        
        # Track position
        self.active_positions[symbol] = {
            'side': side,
            'quantity': quantity,
            'entry_price': price,
            'stop_loss': risk_assessment.stop_loss,
            'take_profit': risk_assessment.take_profit,
            'timestamp': datetime.now()
        }
        
        self.trade_history.append({
            'signal': trade_signal,
            'consensus': consensus_result,
            'risk': risk_assessment
        })
        
        return trade_signal
    
    def get_position_status(self, symbol: str) -> Optional[Dict]:
        """Get current position status"""
        return self.active_positions.get(symbol)
    
    def close_position(self, symbol: str, dry_run: bool = True) -> bool:
        """Close open position"""
        
        if symbol not in self.active_positions:
            logger.warning(f"No active position for {symbol}")
            return False
        
        position = self.active_positions[symbol]
        
        logger.info(f"Closing position for {symbol}: {position}")
        
        if not dry_run:
            try:
                self.trader.close_position(symbol)
                logger.info(f"Position closed for {symbol}")
            except Exception as e:
                logger.error(f"Failed to close position: {e}")
                return False
        
        del self.active_positions[symbol]
        return True
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trade_history
