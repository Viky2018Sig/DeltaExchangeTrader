"""
Agents module - multiagent trading system
"""

from .models import (
    SignalStrength,
    MarketData,
    ComparativeMarketData,
    AgentSignal,
    ConsensusResult,
    RiskAssessment,
    TradeSignal
)

from .market_data import (
    BinanceDataFeed,
    DeltaDataFeed,
    MarketDataAggregator
)

from .signal_agents import (
    BaseAgent,
    TrendAgent,
    MomentumAgent,
    VolumeSpikAgent,
    OIExpansionAgent,
    VolatilityBreakoutAgent
)

from .consensus import ConsensusEngine, RiskManager

from .execution import ExecutionEngine

from .orchestrator import HyperMomentumScanner, MultiagentOrchestrator

__all__ = [
    # Models
    'SignalStrength',
    'MarketData',
    'ComparativeMarketData',
    'AgentSignal',
    'ConsensusResult',
    'RiskAssessment',
    'TradeSignal',
    
    # Data feeds
    'BinanceDataFeed',
    'DeltaDataFeed',
    'MarketDataAggregator',
    
    # Agents
    'BaseAgent',
    'TrendAgent',
    'MomentumAgent',
    'VolumeSpikAgent',
    'OIExpansionAgent',
    'VolatilityBreakoutAgent',
    
    # Engines
    'ConsensusEngine',
    'RiskManager',
    'ExecutionEngine',
    'HyperMomentumScanner',
    'MultiagentOrchestrator'
]
