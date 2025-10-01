"""
텔레그램 알림 시스템
중요 이벤트를 텔레그램으로 전송
"""

import requests
from typing import Optional
from datetime import datetime
import config


class TelegramNotifier:
    """텔레그램 알림 시스템"""

    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        텔레그램 메시지 전송
        Args:
            message: 전송할 메시지
            parse_mode: 'HTML' 또는 'Markdown'
        Returns:
            성공 여부
        """
        if not self.bot_token or not self.chat_id:
            print("텔레그램 설정 없음")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"텔레그램 전송 실패: {str(e)}")
            return False

    def notify_trade_open(self, position_data: dict):
        """포지션 오픈 알림"""
        message = f"""
🟢 <b>포지션 오픈</b>

💰 코인: {position_data['symbol']}
📊 방향: {position_data['position_type']}
💵 진입가: {position_data['entry_price']:,.0f}원
📦 수량: {position_data['quantity']:.8f}
💸 투자금: {position_data['investment']:,.0f}원

🎯 익절가: {position_data['take_profit']:,.0f}원
🛡 손절가: {position_data['stop_loss']:,.0f}원

📈 전략: {position_data['strategy_name']}
🔍 신뢰도: {position_data['confidence']:.1%}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_trade_close(self, trade_data: dict):
        """포지션 청산 알림"""
        pnl = trade_data['pnl']
        pnl_percent = trade_data['pnl_percent']
        emoji = "🟢" if pnl > 0 else "🔴"

        message = f"""
{emoji} <b>포지션 청산</b>

💰 코인: {trade_data['symbol']}
📊 방향: {trade_data['position_type']}
💵 진입가: {trade_data['entry_price']:,.0f}원
💵 청산가: {trade_data['exit_price']:,.0f}원

{'💰' if pnl > 0 else '💸'} <b>손익: {pnl:+,.0f}원 ({pnl_percent:+.2f}%)</b>

⏱ 보유시간: {trade_data['holding_time']}
📝 청산이유: {trade_data['exit_reason']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_signal(self, signal_data: dict):
        """시그널 감지 알림"""
        signal_type = signal_data['signal_type']
        emoji = "🔵" if signal_type == 'BUY' else "🟠"

        message = f"""
{emoji} <b>시그널 감지</b>

💰 코인: {signal_data['symbol']}
📊 시그널: {signal_type}
⚡️ 강도: {signal_data['strength']:.0f}/100
🔍 신뢰도: {signal_data['confidence']:.1%}

💵 가격: {signal_data['entry_price']:,.0f}원
🎯 목표가: {signal_data['take_profit']:,.0f}원
🛡 손절가: {signal_data['stop_loss']:,.0f}원

📈 전략: {signal_data['strategy_name']}
📝 근거: {signal_data['reasoning']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_risk_alert(self, alert_data: dict):
        """리스크 경고 알림"""
        message = f"""
⚠️ <b>리스크 경고</b>

🚨 경고: {alert_data['alert_type']}
📊 상세: {alert_data['message']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_daily_summary(self, summary_data: dict):
        """일일 요약 알림"""
        total_pnl = summary_data['total_pnl']
        emoji = "📈" if total_pnl > 0 else "📉"

        message = f"""
{emoji} <b>일일 거래 요약</b>

📅 날짜: {summary_data['date']}

💰 시작 잔고: {summary_data['starting_balance']:,.0f}원
💰 종료 잔고: {summary_data['ending_balance']:,.0f}원
{'💰' if total_pnl > 0 else '💸'} <b>손익: {total_pnl:+,.0f}원 ({summary_data['pnl_percent']:+.2f}%)</b>

📊 총 거래: {summary_data['total_trades']}건
✅ 수익: {summary_data['winning_trades']}건
❌ 손실: {summary_data['losing_trades']}건
📈 승률: {summary_data['win_rate']:.1%}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_error(self, error_message: str):
        """에러 알림"""
        message = f"""
❌ <b>에러 발생</b>

🚨 {error_message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_system_start(self):
        """시스템 시작 알림"""
        message = f"""
🚀 <b>Auto Coin Trading 시작</b>

⚙️ 모드: {config.TRADE_MODE.upper()}
💰 초기자본: {config.INITIAL_CAPITAL:,.0f}원
🎯 대상코인: {', '.join(config.TARGET_PAIRS)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)

    def notify_system_stop(self):
        """시스템 중단 알림"""
        message = f"""
🛑 <b>Auto Coin Trading 중단</b>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        self.send_message(message)


# 테스트
if __name__ == "__main__":
    notifier = TelegramNotifier()

    test_data = {
        'symbol': 'BTC',
        'position_type': 'LONG',
        'entry_price': 50000000,
        'quantity': 0.001,
        'investment': 50000,
        'take_profit': 51000000,
        'stop_loss': 49000000,
        'strategy_name': 'Trend Following',
        'confidence': 0.85
    }

    notifier.notify_trade_open(test_data)
