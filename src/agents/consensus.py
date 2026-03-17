"""
Consensus engine and risk manager
"""

from typing import List, Dict, Tuple
from datetime import datetime
from .models import AgentSignal, ConsensusResult, RiskAssessment
import logging

logger = logging.getLogger(__name__)

class ConsensusEngine:
    """Aggregates signals from all agents and makes consensus decision"""
    
    def __init__(self, min_agents_threshold: int = 3):
        self.min_agents_threshold = min_agents_threshold
    
    def generate_consensus(self, signals: List[AgentSignal], symbol: str) -> ConsensusResult:
        """Generate consensus from agent signals"""
        
        if len(signals) < 1:
            return ConsensusResult(
                symbol=symbol,
                final_signal='hold',
                consensus_strength=0.0,
                agent_signals=signals,
                voting_distribution={'hold': 0},
                timestamp=datetime.now()
            )
        
        # Count votes
        votes = {'buy': 0, 'sell': 0, 'hold': 0}
        weighted_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        
        for signal in signals:
            signal_type = signal.signal_type
            votes[signal_type] += 1
            
            # Weight by confidence and strength
            weight = signal.confidence * signal.strength
            weighted_scores[signal_type] += weight
        
        # Determine final signal
        total_weight = sum(weighted_scores.values())
        if total_weight > 0:
            buy_weight = weighted_scores['buy'] / total_weight
            sell_weight = weighted_scores['sell'] / total_weight
            hold_weight = weighted_scores['hold'] / total_weight
        else:
            buy_weight = sell_weight = hold_weight = 1/3
        
        # Final decision
        if buy_weight > 0.5 and votes['buy'] >= 2:
            final_signal = 'buy'
            consensus_strength = buy_weight
        elif sell_weight > 0.5 and votes['sell'] >= 2:
            final_signal = 'sell'
            consensus_strength = sell_weight
        else:
            final_signal = 'hold'
            consensus_strength = max(buy_weight, sell_weight, hold_weight)
        
        result = ConsensusResult(
            symbol=symbol,
            final_signal=final_signal,
            consensus_strength=consensus_strength,
            agent_signals=signals,
            voting_distribution=votes,
            timestamp=datetime.now()
        )
        
        logger.info(
            f"Consensus for {symbol}: {final_signal} (strength: {consensus_strength:.2%}). "
            f"Votes: Buy={votes['buy']}, Sell={votes['sell']}, Hold={votes['hold']}"
        )
        
        return result

class RiskManager:
    """Manages position sizing and risk assessment"""
    
    def __init__(
        self,
        max_position_size: float = 0.05,  # 5% of portfolio per position
        max_daily_loss: float = 0.02,  # 2% max daily loss
        min_risk_reward: float = 2.0,  # Minimum 2:1 risk/reward
        volatility_scaling: bool = True
    ):
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.min_risk_reward = min_risk_reward
        self.volatility_scaling = volatility_scaling
    
    def assess_risk(
        self,
        symbol: str,
        side: str,
        current_price: float,
        consensus_strength: float,
        volatility: float = 0.02,
        portfolio_size: float = 10000,
        daily_loss_so_far: float = 0.0
    ) -> RiskAssessment:
        """Assess risk for a potential trade"""
        
        # Calculate stop loss and take profit based on volatility
        if side == 'buy':
            stop_loss = current_price * (1 - volatility * 3)  # 3x volatility
            take_profit = current_price * (1 + volatility * 6)  # 6x volatility
        else:
            stop_loss = current_price * (1 + volatility * 3)
            take_profit = current_price * (1 - volatility * 6)
        
        # Calculate position size
        risk_per_trade = portfolio_size * 0.01  # 1% per trade
        position_risk = abs(current_price - stop_loss)
        position_size = risk_per_trade / position_risk if position_risk > 0 else 0
        
        # Apply max position size limit
        max_position = portfolio_size * self.max_position_size
        if position_size * current_price > max_position:
            position_size = max_position / current_price
        
        # Scale by consensus strength
        position_size *= consensus_strength
        
        # Calculate risk/reward ratio
        potential_loss = abs(current_price - stop_loss)
        potential_gain = abs(take_profit - current_price)
        risk_reward_ratio = potential_gain / potential_loss if potential_loss > 0 else 0
        
        # Check remaining daily loss allowance
        remaining_daily_loss = self.max_daily_loss - daily_loss_so_far
        trade_risk = position_size * current_price * (position_risk / current_price)
        trade_risk_pct = trade_risk / portfolio_size
        
        is_safe = (
            risk_reward_ratio >= self.min_risk_reward and
            trade_risk_pct <= remaining_daily_loss and
            consensus_strength >= 0.6
        )
        
        reason = ""
        if risk_reward_ratio < self.min_risk_reward:
            reason += f"Risk/Reward ratio {risk_reward_ratio:.2f} < {self.min_risk_reward}. "
        if trade_risk_pct > remaining_daily_loss:
            reason += f"Trade risk would exceed daily loss allowance. "
        if consensus_strength < 0.6:
            reason += f"Consensus strength {consensus_strength:.2%} too low. "
        
        if not reason:
            reason = "Trade passes all risk checks"
        
        assessment = RiskAssessment(
            symbol=symbol,
            position_size=position_size,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            max_portfolio_allocation=self.max_position_size,
            volatility_score=volatility,
            is_safe=is_safe,
            reason=reason
        )
        
        logger.info(
            f"Risk assessment for {symbol}: Size={position_size:.4f}, "
            f"R/R={risk_reward_ratio:.2f}, Safe={is_safe}. {reason}"
        )
        
        return assessment
