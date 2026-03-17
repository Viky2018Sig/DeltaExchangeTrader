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

from .telegram import TelegramNotifier

from .paper_trader import PaperTrader

from .scheduler import Scheduler, PositionUpdater

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
    'MultiagentOrchestrator',
    
    # Telegram & Automation
    'TelegramNotifier',
    'PaperTrader',
    'Scheduler',
    'PositionUpdater'
]
