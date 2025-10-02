"""
실제 빗썸 잔고 조회
"""

from api import BithumbAPI
import config

api = BithumbAPI()

# 실제 계좌 잔고 조회
result = api.get_balance('ALL')

if result.get('status') == '0000':
    data = result.get('data', {})
    total_krw = float(data.get('total_krw', 0))
    available_krw = float(data.get('available_krw', 0))

    print('=' * 60)
    print('빗썸 실제 잔고')
    print('=' * 60)
    print(f'총 KRW: {total_krw:,.0f}원')
    print(f'사용가능 KRW: {available_krw:,.0f}원')
    print(f'\n보유 코인:')

    total_crypto_value = 0

    for symbol in config.TARGET_PAIRS:
        coin_key = f'total_{symbol.lower()}'
        coin_balance = float(data.get(coin_key, 0))

        if coin_balance > 0:
            # 현재가 조회
            ticker = api.get_ticker(symbol)
            if ticker.get('status') == '0000':
                current_price = float(ticker['data'].get('closing_price', 0))
                coin_value = coin_balance * current_price
                total_crypto_value += coin_value

                print(f'  {symbol}: {coin_balance:.8f} 개')
                print(f'    현재가: {current_price:,.0f}원')
                print(f'    평가액: {coin_value:,.0f}원')

    print(f'\n총계:')
    print(f'  KRW: {total_krw:,.0f}원')
    print(f'  코인: {total_crypto_value:,.0f}원')
    print(f'  총 자산: {total_krw + total_crypto_value:,.0f}원')
    print('=' * 60)
else:
    print(f'잔고 조회 실패: {result.get("message")}')
