"""
빗썸에서 거래 가능한 모든 코인 가져오기
"""
import requests

url = "https://api.bithumb.com/v1/market/all"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # KRW 마켓만 추출
    coins = []
    if 'data' in data:
        for market in data['data']:
            if market.get('market', '').startswith('KRW-'):
                symbol = market['market'].replace('KRW-', '')
                coins.append(symbol)

    print(f"총 {len(coins)}개 코인:")
    print(coins)

    # config.py에 넣을 형식으로 출력
    print("\n\nconfig.py에 복사할 형식:")
    print("TARGET_PAIRS = [")
    for i in range(0, len(coins), 10):
        batch = coins[i:i+10]
        print(f"    {', '.join([repr(c) for c in batch])},")
    print("]")
else:
    print(f"API 실패: {response.status_code}")
    print("기본 빗썸 API로 재시도...")

    # 대체: ticker API로 ALL 조회
    url2 = "https://api.bithumb.com/public/ticker/ALL_KRW"
    response2 = requests.get(url2)

    if response2.status_code == 200:
        data2 = response2.json()
        if data2.get('status') == '0000':
            coins = [k for k in data2['data'].keys() if k not in ['date', 'timestamp']]
            print(f"총 {len(coins)}개 코인:")
            print(coins)

            # config.py에 넣을 형식으로 출력
            print("\n\nconfig.py에 복사할 형식:")
            print("TARGET_PAIRS = [")
            for i in range(0, len(coins), 10):
                batch = coins[i:i+10]
                print(f"    {', '.join([repr(c) for c in batch])},")
            print("]")
