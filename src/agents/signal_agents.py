"""
Base agent class and signal agents for the multiagent system
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import logging
from .models import AgentSignal, MarketData, ComparativeMarketData
import numpy as np

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all trading agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.signals_history: List[AgentSignal] = []
    
    @abstractmethod
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze market data and generate signal"""
        pass
    
    def add_signal(self, signal: AgentSignal):
        """Record signal in history"""
        self.signals_history.append(signal)

class TrendAgent(BaseAgent):
    """Analyzes price trends"""
    
    def __init__(self):
        super().__init__("TrendAgent")
        self.sma_short = 5  # 5-period
        self.sma_long = 20  # 20-period
        self.price_history: Dict[str, List[float]] = {}
    
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze price trend"""
        symbol = market_data.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(market_data.price)
        
        # Keep only last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        prices = self.price_history[symbol]
        
        # Need enough data
        if len(prices) < self.sma_long:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.3,
                reasoning="Insufficient data for trend analysis",
                timestamp=market_data.timestamp
            )
        
        sma_short = np.mean(prices[-self.sma_short:])
        sma_long = np.mean(prices[-self.sma_long:])
        
        if sma_short > sma_long * 1.02:  # 2% above
            signal_type = 'buy'
            strength = min((sma_short - sma_long) / sma_long, 1.0)
            confidence = 0.7
            reasoning = f"Price above both SMAs. SMA({self.sma_short})={sma_short:.2f} > SMA({self.sma_long})={sma_long:.2f}"
        elif sma_short < sma_long * 0.98:  # 2% below
            signal_type = 'sell'
            strength = min((sma_long - sma_short) / sma_long, 1.0)
            confidence = 0.7
            reasoning = f"Price below both SMAs. SMA({self.sma_short})={sma_short:.2f} < SMA({self.sma_long})={sma_long:.2f}"
        else:
            signal_type = 'hold'
            strength = 0.5
            confidence = 0.5
            reasoning = "Price between the moving averages"
        
        signal = AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=market_data.timestamp,
            technical_indicators={
                'sma_short': sma_short,
                'sma_long': sma_long,
                'current_price': market_data.price
            }
        )
        self.add_signal(signal)
        return signal

class MomentumAgent(BaseAgent):
    """Analyzes price momentum using rate of change"""
    
    def __init__(self):
        super().__init__("MomentumAgent")
        self.price_history: Dict[str, List[float]] = {}
    
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze momentum"""
        symbol = market_data.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(market_data.price)
        
        if len(self.price_history[symbol]) > 50:
            self.price_history[symbol] = self.price_history[symbol][-50:]
        
        prices = self.price_history[symbol]
        
        if len(prices) < 5:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.3,
                reasoning="Insufficient data for momentum analysis",
                timestamp=market_data.timestamp
            )
        
        # Calculate ROC (Rate of Change)
        roc_5 = (prices[-1] - prices[-5]) / prices[-5]
        roc_10 = (prices[-1] - prices[-10]) / prices[-10]
        
        momentum = (roc_5 + roc_10) / 2
        
        if momentum > 0.03:  # 3% positive momentum
            signal_type = 'buy'
            strength = min(abs(momentum) / 0.1, 1.0)
            confidence = 0.75
            reasoning = f"Strong positive momentum. ROC(5)={roc_5:.2%}, ROC(10)={roc_10:.2%}"
        elif momentum < -0.03:  # 3% negative momentum
            signal_type = 'sell'
            strength = min(abs(momentum) / 0.1, 1.0)
            confidence = 0.75
            reasoning = f"Strong negative momentum. ROC(5)={roc_5:.2%}, ROC(10)={roc_10:.2%}"
        else:
            signal_type = 'hold'
            strength = 0.5
            confidence = 0.5
            reasoning = "Momentum is neutral"
        
        signal = AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=market_data.timestamp,
            technical_indicators={
                'roc_5': roc_5,
                'roc_10': roc_10,
                'momentum': momentum
            }
        )
        self.add_signal(signal)
        return signal

class VolumeSpikAgent(BaseAgent):
    """Detects volume spikes"""
    
    def __init__(self):
        super().__init__("VolumeSpikAgent")
        self.volume_history: Dict[str, List[float]] = {}
    
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze volume spike"""
        symbol = market_data.symbol
        
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        self.volume_history[symbol].append(market_data.volume_1h)
        
        if len(self.volume_history[symbol]) > 50:
            self.volume_history[symbol] = self.volume_history[symbol][-50:]
        
        volumes = self.volume_history[symbol]
        
        if len(volumes) < 5:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.3,
                reasoning="Insufficient volume data",
                timestamp=market_data.timestamp
            )
        
        avg_volume = np.mean(volumes[:-1])
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 2.0:  # 2x average volume
            signal_type = 'buy'
            strength = min((volume_ratio - 1) / 2, 1.0)
            confidence = 0.8
            reasoning = f"Volume spike detected. Current volume is {volume_ratio:.1f}x average"
        elif volume_ratio < 0.5:  # Less than half average
            signal_type = 'sell'
            strength = 0.3
            confidence = 0.6
            reasoning = f"Low volume. Current volume is {volume_ratio:.1f}x average"
        else:
            signal_type = 'hold'
            strength = 0.5
            confidence = 0.5
            reasoning = "Volume is normal"
        
        signal = AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=market_data.timestamp,
            technical_indicators={
                'volume_ratio': volume_ratio,
                'average_volume': avg_volume,
                'current_volume': current_volume
            }
        )
        self.add_signal(signal)
        return signal

class OIExpansionAgent(BaseAgent):
    """Analyzes Open Interest expansion (delta perpetuals)"""
    
    def __init__(self):
        super().__init__("OIExpansionAgent")
        self.oi_history: Dict[str, List[float]] = {}
    
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze OI expansion"""
        symbol = market_data.symbol
        
        if not market_data.open_interest:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.2,
                reasoning="No Open Interest data available",
                timestamp=market_data.timestamp
            )
        
        if symbol not in self.oi_history:
            self.oi_history[symbol] = []
        
        self.oi_history[symbol].append(market_data.open_interest)
        
        if len(self.oi_history[symbol]) > 50:
            self.oi_history[symbol] = self.oi_history[symbol][-50:]
        
        ois = self.oi_history[symbol]
        
        if len(ois) < 3:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.3,
                reasoning="Insufficient OI data",
                timestamp=market_data.timestamp
            )
        
        oi_change_recent = (ois[-1] - ois[-2]) / ois[-2] if ois[-2] > 0 else 0
        oi_trend = (ois[-1] - np.mean(ois[:-5])) / np.mean(ois[:-5]) if np.mean(ois[:-5]) > 0 else 0
        
        if oi_change_recent > 0.05 and oi_trend > 0.1:  # 5% recent, 10% trend
            signal_type = 'buy'
            strength = min(oi_trend / 0.2, 1.0)
            confidence = 0.7
            reasoning = f"OI expansion detected. Change: {oi_change_recent:.2%}, Trend: {oi_trend:.2%}"
        elif oi_change_recent < -0.05 and oi_trend < -0.1:
            signal_type = 'sell'
            strength = min(abs(oi_trend) / 0.2, 1.0)
            confidence = 0.7
            reasoning = f"OI contraction detected. Change: {oi_change_recent:.2%}, Trend: {oi_trend:.2%}"
        else:
            signal_type = 'hold'
            strength = 0.5
            confidence = 0.5
            reasoning = "OI is stable"
        
        signal = AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=market_data.timestamp,
            technical_indicators={
                'oi_recent_change': oi_change_recent,
                'oi_trend': oi_trend,
                'current_oi': market_data.open_interest
            }
        )
        self.add_signal(signal)
        return signal

class VolatilityBreakoutAgent(BaseAgent):
    """Analyzes volatility breakouts"""
    
    def __init__(self):
        super().__init__("VolatilityBreakoutAgent")
        self.price_history: Dict[str, List[float]] = {}
    
    def analyze(self, market_data: MarketData) -> AgentSignal:
        """Analyze volatility breakout"""
        symbol = market_data.symbol
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(market_data.price)
        
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        prices = self.price_history[symbol]
        
        if len(prices) < 20:
            return AgentSignal(
                agent_name=self.name,
                symbol=symbol,
                signal_type='hold',
                strength=0.5,
                confidence=0.3,
                reasoning="Insufficient data for volatility analysis",
                timestamp=market_data.timestamp
            )
        
        recent_volatility = np.std(prices[-10:]) / np.mean(prices[-10:])
        historical_volatility = np.std(prices[:-10]) / np.mean(prices[:-10])
        
        volatility_ratio = recent_volatility / historical_volatility if historical_volatility > 0 else 1
        
        if volatility_ratio > 1.5:  # Recent vol 50% higher
            # Check if price is at extremes
            high = np.max(prices[-20:])
            low = np.min(prices[-20:])
            current = prices[-1]
            
            position = (current - low) / (high - low) if high > low else 0.5
            
            if position > 0.7:
                signal_type = 'buy'
                reasoning = "High volatility breakout, price near highs"
            elif position < 0.3:
                signal_type = 'sell'
                reasoning = "High volatility breakout, price near lows"
            else:
                signal_type = 'hold'
                reasoning = "High volatility, price neutral"
            
            strength = min(volatility_ratio - 1, 1.0)
            confidence = 0.75
        else:
            signal_type = 'hold'
            strength = 0.5
            confidence = 0.5
            reasoning = "Volatility is normal"
        
        signal = AgentSignal(
            agent_name=self.name,
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=market_data.timestamp,
            technical_indicators={
                'recent_volatility': recent_volatility,
                'historical_volatility': historical_volatility,
                'volatility_ratio': volatility_ratio
            }
        )
        self.add_signal(signal)
        return signal
