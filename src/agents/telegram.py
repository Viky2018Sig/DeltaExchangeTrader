"""
Telegram notifier for sending trading signals and updates
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Sends trading signals and updates via Telegram bot"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token from BotFather
            chat_id: Your Telegram user ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str) -> bool:
        """Send text message to Telegram"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_signal_notification(self, signal_data: Dict) -> bool:
        """Send trading signal notification"""
        
        symbol = signal_data['symbol']
        side = signal_data['side']
        entry_price = signal_data['entry_price']
        stop_loss = signal_data['stop_loss']
        take_profit = signal_data['take_profit']
        risk_reward = signal_data['risk_reward_ratio']
        consensus_strength = signal_data['consensus_strength']
        
        # Format side with emoji
        side_emoji = "🟢 BUY" if side == "BUY" else "🔴 SELL"
        
        message = f"""
<b>{side_emoji} SIGNAL: {symbol}</b>

📊 <b>Price Levels:</b>
• Entry: ${entry_price:,.2f}
• Stop-Loss: ${stop_loss:,.2f}
• Take-Profit: ${take_profit:,.2f}

📈 <b>Trade Metrics:</b>
• Risk/Reward Ratio: {risk_reward:.2f}x
• Consensus Strength: {consensus_strength:.1%}
• Agents Agreeing: {signal_data.get('agent_votes', 'Unknown')}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

💡 <b>Note:</b> Paper trading mode - validating strategy
🔔 You will be notified when position should close (7 days)
"""
        
        return self.send_message(message)
    
    def send_position_update(self, position_data: Dict) -> bool:
        """Send position update/tracking notification"""
        
        symbol = position_data['symbol']
        side = position_data['side']
        entry_price = position_data['entry_price']
        current_price = position_data['current_price']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100 if side == "BUY" else ((entry_price - current_price) / entry_price) * 100
        
        pnl_emoji = "📈" if pnl_pct > 0 else "📉"
        
        stop_loss = position_data['stop_loss']
        take_profit = position_data['take_profit']
        days_held = position_data['days_held']
        
        # Check if close to stop or profit
        stop_distance = abs(current_price - stop_loss) / stop_loss * 100
        profit_distance = abs(current_price - take_profit) / take_profit * 100
        
        alert = ""
        if stop_distance < 2:
            alert = "\n⚠️ <b>ALERT:</b> Close to stop-loss!"
        elif profit_distance < 2:
            alert = "\n✅ <b>ALERT:</b> Close to take-profit!"
        
        message = f"""
📍 <b>POSITION UPDATE: {symbol}</b>

{pnl_emoji} <b>P&L:</b> {pnl_pct:+.2f}%
• Current Price: ${current_price:,.2f}
• Entry Price: ${entry_price:,.2f}

📊 <b>Level Status:</b>
• Stop-Loss: ${stop_loss:,.2f} ({stop_distance:.1f}% away)
• Take-Profit: ${take_profit:,.2f} ({profit_distance:.1f}% away)

⏱️ <b>Duration:</b> {days_held:.1f} days held{alert}

⏰ <b>Updated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_close_signal(self, close_data: Dict) -> bool:
        """Send close/exit signal notification"""
        
        symbol = close_data['symbol']
        side = close_data['side']
        entry_price = close_data['entry_price']
        current_price = close_data['current_price']
        pnl_pct = close_data['pnl_pct']
        close_reason = close_data['reason']
        days_held = close_data['days_held']
        
        pnl_emoji = "✅" if pnl_pct > 0 else "❌"
        
        message = f"""
<b>🚪 CLOSE SIGNAL: {symbol}</b>

{pnl_emoji} <b>Final P&L:</b> {pnl_pct:+.2f}%
• Entry Price: ${entry_price:,.2f}
• Exit Price: ${current_price:,.2f}

📊 <b>Trade Duration:</b> {days_held:.1f} days

🎯 <b>Close Reason:</b>
{close_reason}

ℹ️ <b>Strategy Validation:</b>
Paper trading completed for {symbol}
Results will be aggregated for authenticity check

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_summary_report(self, summary_data: Dict) -> bool:
        """Send weekly summary report"""
        
        total_signals = summary_data['total_signals']
        closed_trades = summary_data['closed_trades']
        active_trades = summary_data['active_trades']
        total_pnl_pct = summary_data['total_pnl_pct']
        win_rate = summary_data['win_rate']
        avg_rr = summary_data['avg_risk_reward']
        
        win_emoji = "📈" if total_pnl_pct > 0 else "📉"
        
        message = f"""
<b>📋 WEEK SUMMARY REPORT</b>

{win_emoji} <b>Overall Performance:</b>
• Total P&L: {total_pnl_pct:+.2f}%
• Closed Trades: {closed_trades}
• Win Rate: {win_rate:.1f}%
• Avg Risk/Reward: {avg_rr:.2f}x

📊 <b>Signal Status:</b>
• Total Signals Generated: {total_signals}
• Active Positions: {active_trades}
• Closed Positions: {closed_trades}

🎯 <b>Authenticity Assessment:</b>
Strategy validation week complete!
Review results to determine readiness for live trading.

⏰ <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        return self.send_message(message)
    
    def send_scan_report(self, scan_data: Dict) -> bool:
        """Send market scan report"""
        
        timestamp = scan_data['timestamp']
        opportunities = scan_data['opportunities']
        signals_sent = scan_data['signals_sent']
        active_positions = scan_data['active_positions']
        
        # Top 5 opportunities
        top_coins = scan_data.get('top_coins', [])
        coins_list = "\n".join([f"• {coin['symbol']}: {coin['volume_premium']:.2f}x volume premium" 
                                for coin in top_coins[:5]])
        
        message = f"""
<b>🔍 MARKET SCAN REPORT</b>

⏰ <b>Scan Time:</b> {timestamp}

📊 <b>Opportunities Found:</b>
{coins_list if coins_list else "No opportunities matching criteria"}

🎯 <b>Signals:</b>
• Just Sent: {signals_sent}
• Active Positions: {active_positions}

💡 <b>Next Scan:</b> Scheduled automatically
📢 You'll be notified of new signals as they occur
"""
        
        return self.send_message(message)
    
    def send_error_alert(self, error_msg: str) -> bool:
        """Send error alert notification"""
        
        message = f"""
⚠️ <b>SYSTEM ERROR ALERT</b>

{error_msg}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Please check logs for details and restart if needed.
"""
        
        return self.send_message(message)
    
    def send_startup_message(self) -> bool:
        """Send startup confirmation message"""
        
        message = """
✅ <b>AUTOMATED TRADING SYSTEM STARTED</b>

🤖 System Status: <b>ONLINE</b>
💼 Mode: <b>PAPER TRADING (Validation Week)</b>
📊 Timeframe: <b>7 Days</b>

🎯 What to expect:
• Signal notifications when opportunities found
• Price level tracking (Entry, Stop-Loss, Take-Profit)
• Position updates and alerts
• Close signals after 7 days or hit targets
• Weekly summary report

🔔 <b>Your Telegram is configured and receiving signals</b>

⏰ <b>Started:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        return self.send_message(message)
