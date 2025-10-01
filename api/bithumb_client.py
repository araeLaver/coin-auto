"""
빗썸 API 클라이언트
REST API 및 WebSocket 연동
"""

import hashlib
import hmac
import time
import requests
import json
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any
import config


class BithumbAPI:
    """빗썸 REST API 클라이언트"""

    BASE_URL = "https://api.bithumb.com"

    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or config.BITHUMB_API_KEY
        self.secret_key = secret_key or config.BITHUMB_SECRET_KEY
        self.session = requests.Session()

    def _generate_signature(self, endpoint: str, params: Dict = None) -> Dict[str, str]:
        """API 서명 생성 (빗썸 공식 방식)"""
        import base64

        nonce = str(int(time.time() * 1000))

        if params:
            query_string = urlencode(params)
        else:
            query_string = ""

        # 빗썸 서명 생성: endpoint + null + params + null + nonce
        message = endpoint + chr(0) + query_string + chr(0) + nonce

        # HMAC-SHA512 해시 생성 후 hexdigest
        signature_hash = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # hexdigest를 Base64로 인코딩
        signature = base64.b64encode(signature_hash.encode('utf-8')).decode('utf-8')

        return {
            'Api-Key': self.api_key,
            'Api-Sign': signature,
            'Api-Nonce': nonce
        }

    def _request(self, method: str, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """HTTP 요청 처리"""
        url = f"{self.BASE_URL}{endpoint}"

        if signed:
            # Private API: Content-Type을 x-www-form-urlencoded로 설정
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            headers.update(self._generate_signature(endpoint, params))

            # POST 요청 시 데이터를 form-data로 전송
            try:
                from urllib.parse import urlencode
                body = urlencode(params) if params else ""
                response = self.session.post(url, data=body, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"API 요청 실패: {e}")
                return {'status': '5000', 'message': str(e)}
        else:
            # Public API
            headers = {'Content-Type': 'application/json'}
            try:
                if method == 'GET':
                    response = self.session.get(url, params=params, headers=headers, timeout=10)
                elif method == 'POST':
                    response = self.session.post(url, json=params, headers=headers, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"API 요청 실패: {e}")
                return {'status': '5000', 'message': str(e)}

    # ===========================
    # Public API (인증 불필요)
    # ===========================

    def get_ticker(self, symbol: str = "ALL") -> Dict:
        """
        현재가 정보 조회
        Args:
            symbol: 코인 심볼 (예: "BTC", "ETH") 또는 "ALL"
        """
        endpoint = f"/public/ticker/{symbol}_KRW"
        return self._request('GET', endpoint)

    def get_orderbook(self, symbol: str) -> Dict:
        """
        호가 정보 조회 (매수/매도 호가)
        Args:
            symbol: 코인 심볼 (예: "BTC")
        """
        endpoint = f"/public/orderbook/{symbol}_KRW"
        return self._request('GET', endpoint)

    def get_transaction_history(self, symbol: str, count: int = 20) -> Dict:
        """
        최근 체결 내역 조회
        Args:
            symbol: 코인 심볼
            count: 조회할 개수 (기본 20)
        """
        endpoint = f"/public/transaction_history/{symbol}_KRW"
        params = {'count': count}
        return self._request('GET', endpoint, params=params)

    def get_candlestick(self, symbol: str, interval: str = "24h") -> Dict:
        """
        캔들스틱 데이터 조회
        Args:
            symbol: 코인 심볼
            interval: 시간 간격 ("1m", "3m", "5m", "10m", "30m", "1h", "6h", "12h", "24h")
        """
        endpoint = f"/public/candlestick/{symbol}_KRW/{interval}"
        return self._request('GET', endpoint)

    # ===========================
    # Private API (인증 필요)
    # ===========================

    def get_balance(self, currency: str = "ALL") -> Dict:
        """
        잔고 조회
        Args:
            currency: 통화 (예: "BTC", "KRW") 또는 "ALL"
        """
        endpoint = "/info/balance"
        params = {
            'order_currency': currency,
            'payment_currency': 'KRW'
        }
        return self._request('POST', endpoint, params=params, signed=True)

    def get_wallet_address(self, currency: str) -> Dict:
        """
        입금 지갑 주소 조회
        Args:
            currency: 통화 (예: "BTC")
        """
        endpoint = "/info/wallet_address"
        params = {'currency': currency}
        return self._request('POST', endpoint, params=params, signed=True)

    def place_order(self, symbol: str, order_type: str, quantity: float, price: float = None) -> Dict:
        """
        주문 실행
        Args:
            symbol: 코인 심볼
            order_type: "bid" (매수) 또는 "ask" (매도)
            quantity: 주문 수량
            price: 주문 가격 (시장가일 경우 None)
        """
        endpoint = "/trade/place"
        params = {
            'order_currency': symbol,
            'payment_currency': 'KRW',
            'units': quantity,
            'type': order_type
        }

        if price:
            params['price'] = price

        return self._request('POST', endpoint, params=params, signed=True)

    def cancel_order(self, order_type: str, order_id: str, symbol: str) -> Dict:
        """
        주문 취소
        Args:
            order_type: "bid" 또는 "ask"
            order_id: 주문 ID
            symbol: 코인 심볼
        """
        endpoint = "/trade/cancel"
        params = {
            'type': order_type,
            'order_id': order_id,
            'order_currency': symbol,
            'payment_currency': 'KRW'
        }
        return self._request('POST', endpoint, params=params, signed=True)

    def get_order_detail(self, order_id: str, symbol: str, order_type: str) -> Dict:
        """
        주문 상세 조회
        Args:
            order_id: 주문 ID
            symbol: 코인 심볼
            order_type: "bid" 또는 "ask"
        """
        endpoint = "/info/order_detail"
        params = {
            'order_id': order_id,
            'order_currency': symbol,
            'payment_currency': 'KRW',
            'type': order_type
        }
        return self._request('POST', endpoint, params=params, signed=True)

    def get_orders(self, symbol: str, order_type: str = "bid", count: int = 100) -> Dict:
        """
        미체결 주문 조회
        Args:
            symbol: 코인 심볼
            order_type: "bid" 또는 "ask"
            count: 조회할 개수
        """
        endpoint = "/info/orders"
        params = {
            'order_currency': symbol,
            'payment_currency': 'KRW',
            'type': order_type,
            'count': count
        }
        return self._request('POST', endpoint, params=params, signed=True)

    def get_user_transactions(self, symbol: str, offset: int = 0, count: int = 20) -> Dict:
        """
        거래 내역 조회
        Args:
            symbol: 코인 심볼
            offset: 시작 위치
            count: 조회할 개수
        """
        endpoint = "/info/user_transactions"
        params = {
            'order_currency': symbol,
            'payment_currency': 'KRW',
            'offset': offset,
            'count': count
        }
        return self._request('POST', endpoint, params=params, signed=True)


class BithumbWebSocket:
    """
    빗썸 WebSocket 클라이언트
    실시간 데이터 수신용
    """

    WS_URL = "wss://pubwss.bithumb.com/pub/ws"

    def __init__(self):
        self.ws = None
        self.subscriptions = []

    def connect(self):
        """WebSocket 연결"""
        import websocket
        self.ws = websocket.WebSocketApp(
            self.WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

    def on_open(self, ws):
        """연결 성공 시 호출"""
        print("WebSocket 연결 성공")
        # 구독 메시지 전송
        for sub in self.subscriptions:
            ws.send(json.dumps(sub))

    def on_message(self, ws, message):
        """메시지 수신 시 호출"""
        data = json.loads(message)
        # 메시지 처리 로직 (상속받아 구현)
        self.handle_message(data)

    def on_error(self, ws, error):
        """에러 발생 시 호출"""
        print(f"WebSocket 에러: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        """연결 종료 시 호출"""
        print("WebSocket 연결 종료")

    def handle_message(self, data: Dict):
        """메시지 처리 (오버라이드 필요)"""
        pass

    def subscribe_ticker(self, symbols: List[str]):
        """
        실시간 시세 구독
        Args:
            symbols: 코인 심볼 리스트 (예: ["BTC", "ETH"])
        """
        symbols_str = [f"{s}_KRW" for s in symbols]
        subscription = {
            "type": "ticker",
            "symbols": symbols_str
        }
        self.subscriptions.append(subscription)
        if self.ws:
            self.ws.send(json.dumps(subscription))

    def subscribe_orderbook(self, symbols: List[str]):
        """
        실시간 호가 구독
        Args:
            symbols: 코인 심볼 리스트
        """
        symbols_str = [f"{s}_KRW" for s in symbols]
        subscription = {
            "type": "orderbookdepth",
            "symbols": symbols_str
        }
        self.subscriptions.append(subscription)
        if self.ws:
            self.ws.send(json.dumps(subscription))

    def subscribe_transaction(self, symbols: List[str]):
        """
        실시간 체결 구독
        Args:
            symbols: 코인 심볼 리스트
        """
        symbols_str = [f"{s}_KRW" for s in symbols]
        subscription = {
            "type": "transaction",
            "symbols": symbols_str
        }
        self.subscriptions.append(subscription)
        if self.ws:
            self.ws.send(json.dumps(subscription))

    def run(self):
        """WebSocket 실행 (블로킹)"""
        if self.ws:
            self.ws.run_forever()


# 테스트 코드
if __name__ == "__main__":
    # Public API 테스트
    api = BithumbAPI()

    print("=== 현재가 조회 ===")
    ticker = api.get_ticker("BTC")
    print(ticker)

    print("\n=== 호가 조회 ===")
    orderbook = api.get_orderbook("BTC")
    print(orderbook)
