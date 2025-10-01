"""
빗썸 API 디버깅 테스트
"""

import sys
import os

# Windows 콘솔 UTF-8 설정
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import hashlib
import hmac
import time
import requests
import json
from urllib.parse import urlencode
import base64
import config

def test_api_signature():
    """API 서명 테스트"""
    print("빗썸 API 인증 디버깅")
    print("=" * 70)

    api_key = config.BITHUMB_API_KEY
    secret_key = config.BITHUMB_SECRET_KEY

    print(f"\nAPI Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"Secret Key: {secret_key[:10]}...{secret_key[-10:]}")

    # 빗썸 API 인증 테스트
    endpoint = "/info/balance"
    nonce = str(int(time.time() * 1000))

    params = {
        'order_currency': 'BTC',
        'payment_currency': 'KRW'
    }

    query_string = urlencode(params)
    print(f"\nQuery String: {query_string}")
    print(f"Nonce: {nonce}")

    # 메시지 생성
    message = endpoint + chr(0) + query_string + chr(0) + nonce
    print(f"\nMessage (before encoding): {repr(message)}")

    try:
        # Secret Key를 그대로 사용
        print(f"Secret Key length: {len(secret_key)} chars")

        # HMAC-SHA512 서명
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        print(f"Signature: {signature[:20]}...")

        # HTTP 요청
        url = f"https://api.bithumb.com{endpoint}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Api-Key': api_key,
            'Api-Sign': signature,
            'Api-Nonce': nonce
        }

        print(f"\nRequest URL: {url}")
        print(f"Request Headers:")
        for k, v in headers.items():
            if k in ['Api-Key', 'Api-Sign']:
                print(f"  {k}: {v[:20]}...")
            else:
                print(f"  {k}: {v}")

        print(f"\nRequest Body: {query_string}")

        # POST 요청
        response = requests.post(
            url,
            data=query_string,
            headers=headers,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '0000':
                print("\n✓ API 인증 성공!")
                return True
            else:
                print(f"\n✗ API 오류: {data.get('message')}")
                return False
        else:
            print(f"\n✗ HTTP 오류: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n✗ 예외 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_api_signature()
