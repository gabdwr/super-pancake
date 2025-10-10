"""
Telegram Alert System
Send notifications for token discoveries, trades, and errors
"""

import logging
from typing import Optional, Dict
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramAlert:
    """
    Telegram notification system for trading bot alerts

    Usage:
        1. Create bot via @BotFather on Telegram
        2. Get bot token
        3. Get your chat ID by messaging bot and checking:
           https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates
        4. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram alerting

        Args:
            bot_token: Telegram bot token (optional, loads from config if not provided)
            chat_id: Your Telegram chat ID (optional, loads from config if not provided)
        """
        # Try to load from config if not provided
        if bot_token is None or chat_id is None:
            try:
                from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
                self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
                self.chat_id = chat_id or TELEGRAM_CHAT_ID
            except ImportError:
                self.bot_token = bot_token
                self.chat_id = chat_id
        else:
            self.bot_token = bot_token
            self.chat_id = chat_id

        # Validate credentials
        self.enabled = bool(self.bot_token and self.chat_id)

        if not self.enabled:
            logger.warning("⚠️  Telegram alerts disabled: Missing bot token or chat ID")
        else:
            logger.info("✅ Telegram bot is enabled (token and chat id are working!)")

    def send_message(self, message: str, parse_mode: str = "Markdown", disable_preview: bool = True) -> bool:
        """
        Send a message via Telegram

        Args:
            message: Message text (supports Markdown formatting)
            parse_mode: Telegram parse mode (Markdown or HTML)
            disable_preview: Disable link previews

        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram not enabled, skipping message")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": disable_preview
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.debug("✅ Telegram message sent")
                return True
            else:
                logger.error(f"❌ Telegram error: HTTP {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
            return False

    def send_token_discovery_alert(self, token_info: Dict) -> bool:
        """
        Send formatted alert for discovered token

        Args:
            token_info: Token information dictionary from DexScreener

        Returns:
            True if sent successfully
        """
        try:
            # Extract token data
            name = token_info.get('name', 'Unknown')
            symbol = token_info.get('symbol', '???')
            address = token_info.get('address', 'N/A')
            liquidity = token_info.get('liquidity_usd', 0)
            market_cap = token_info.get('market_cap', 0)
            volume_24h = token_info.get('volume_24h', 0)
            price_change = token_info.get('price_change_24h', 0)
            age_days = token_info.get('age_days')
            url = token_info.get('url', '')

            # Liquidity analysis
            liq_analysis = token_info.get('liquidity_analysis')

            # Build message
            message = "🚨 *TOKEN DISCOVERED*\n\n"
            message += f"*{name}* (${symbol})\n"
            message += f"`{address}`\n\n"

            # Basic metrics
            message += "📊 *Metrics:*\n"
            if age_days is not None:
                message += f"Age: {age_days} days\n"
            message += f"Liquidity: ${liquidity:,.0f}\n"
            message += f"Market Cap: ${market_cap:,.0f}\n"
            message += f"24h Volume: ${volume_24h:,.0f}\n"
            message += f"24h Change: {price_change:+.2f}%\n\n"

            # Liquidity analysis (if available)
            if liq_analysis:
                score = liq_analysis.get('total_score', 0)
                recommendation = liq_analysis.get('recommendation', 'N/A')
                flags = liq_analysis.get('flags', [])

                # Score emoji
                if score >= 80:
                    score_emoji = "🟢"
                elif score >= 60:
                    score_emoji = "🟡"
                else:
                    score_emoji = "🔴"

                message += f"{score_emoji} *Liquidity Score: {score}/100*\n"
                message += f"Recommendation: {recommendation}\n\n"

                # Detailed analysis
                analysis = liq_analysis.get('analysis', {})

                # Concentration
                if 'concentration' in analysis:
                    conc = analysis['concentration']
                    message += f"🔹 Concentration: {conc['concentration_ratio']:.1%} ({conc['pair_count']} pairs)\n"

                # Lock status
                if 'lock' in analysis:
                    lock = analysis['lock']
                    if lock['is_locked']:
                        message += f"🔒 Locked: {lock['locked_percentage']:.1f}% ({lock['locker_name']})\n"
                    else:
                        message += "⚠️ Not locked\n"

                # Wash trading
                if 'wash_trading' in analysis:
                    wash = analysis['wash_trading']
                    message += f"📈 Vol/Liq Ratio: {wash['volume_liquidity_ratio']:.2f}x\n"

                # Slippage
                if 'slippage' in analysis:
                    slip = analysis['slippage']
                    message += f"💧 Slippage: {slip['estimated_slippage_percent']:.3f}% (${slip['trade_size_usd']})\n"

                # Rugpull risk
                if 'rugpull' in analysis:
                    rug = analysis['rugpull']
                    message += f"⚠️ Rug Risk: {rug['risk_score']}\n"

                # Flags
                if flags:
                    message += "\n🚩 *Flags:*\n"
                    for flag in flags[:5]:  # Limit to 5 flags
                        message += f"• {flag}\n"

            # Link
            if url:
                message += f"\n[View on DexScreener]({url})"

            return self.send_message(message)

        except Exception as e:
            logger.error(f"Failed to format token alert: {e}")
            return False

    def send_script_start_alert(self, script_name: str, filters: Dict = None) -> bool:
        """
        Send alert when script starts running

        Args:
            script_name: Name of the script
            filters: Dictionary of filter parameters

        Returns:
            True if sent successfully
        """
        message = f"🚀 *{script_name} Started*\n"

        # if filters:
        #     message += "📋 *Filters:*\n"
        #     for key, value in filters.items():
        #         message += f"• {key}: {value}\n"

        message += "\nScanning for tokens..."

        return self.send_message(message)

    def send_script_complete_alert(self, script_name: str, tokens_found: int, tokens_passed: int) -> bool:
        """
        Send alert when script completes

        Args:
            script_name: Name of the script
            tokens_found: Total tokens discovered
            tokens_passed: Tokens that passed filters

        Returns:
            True if sent successfully
        """
        if tokens_passed > 0:
            emoji = "✅"
        elif tokens_found > 0:
            emoji = "⚠️"
        else:
            emoji = "ℹ️"

        message = f"{emoji} *{script_name} Complete*\n\n"
        message += f"Tokens scanned: {tokens_found}\n"
        message += f"Tokens passed filters: {tokens_passed}\n"

        if tokens_passed > 0:
            message += f"\n🎯 {tokens_passed} opportunity(ies) found!"
        elif tokens_found > 0:
            message += "\n📉 No tokens met quality criteria"
        else:
            message += "\n🔍 No tokens found matching search"

        return self.send_message(message)

    def send_error_alert(self, error_message: str, context: str = "") -> bool:
        """
        Send error notification

        Args:
            error_message: Error description
            context: Additional context (script name, function, etc.)

        Returns:
            True if sent successfully
        """
        message = "❌ *ERROR*\n\n"

        if context:
            message += f"Context: {context}\n\n"

        message += f"```\n{error_message}\n```"

        return self.send_message(message)


# Convenience singleton instance
_telegram_alert_instance = None

def get_telegram_alert() -> TelegramAlert:
    """Get or create singleton TelegramAlert instance"""
    global _telegram_alert_instance

    if _telegram_alert_instance is None:
        _telegram_alert_instance = TelegramAlert()

    return _telegram_alert_instance


# Convenience functions
def send_alert(message: str) -> bool:
    """Send a simple text alert"""
    return get_telegram_alert().send_message(message)


def send_token_alert(token_info: Dict) -> bool:
    """Send formatted token discovery alert"""
    return get_telegram_alert().send_token_discovery_alert(token_info)


def send_error(error: str, context: str = "") -> bool:
    """Send error alert"""
    return get_telegram_alert().send_error_alert(error, context)


# Example usage
if __name__ == "__main__":
    # Test the alert system
    alert = TelegramAlert()

    if alert.enabled:
        print("Testing Telegram alerts...")

        # Test simple message
        alert.send_message("🥞 Test message from Super Pancake bot!")

        # Test token alert
        test_token = {
            'name': 'Test Token',
            'symbol': 'TEST',
            'address': '0x1234567890abcdef1234567890abcdef12345678',
            'liquidity_usd': 125000,
            'market_cap': 850000,
            'volume_24h': 45000,
            'price_change_24h': 15.5,
            'age_days': 14,
            'url': 'https://dexscreener.com/bsc/0x1234567890abcdef',
            'liquidity_analysis': {
                'total_score': 85,
                'recommendation': 'SAFE',
                'flags': ['Good liquidity depth', 'Locked liquidity'],
                'analysis': {
                    'concentration': {'concentration_ratio': 0.75, 'pair_count': 2},
                    'lock': {'is_locked': True, 'locked_percentage': 95.0, 'locker_name': 'Unicrypt'},
                    'wash_trading': {'volume_liquidity_ratio': 1.2},
                    'slippage': {'estimated_slippage_percent': 0.5, 'trade_size_usd': 50},
                    'rugpull': {'risk_score': 'LOW'}
                }
            }
        }

        alert.send_token_discovery_alert(test_token)

        print("✅ Test alerts sent! Check your Telegram.")
    else:
        print("❌ Telegram not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
