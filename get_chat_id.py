"""
Chat ID 조회 스크립트
"""
import requests

bot_token = '8289507874:AAHvAT9KNn-D7VkLrmyBzliw69UhEhiEgkM'

print("=" * 60)
print("Chat ID 조회 중...")
print("=" * 60)

url = f'https://api.telegram.org/bot{bot_token}/getUpdates'
response = requests.get(url)
data = response.json()

if data.get('ok'):
    updates = data.get('result', [])

    if updates:
        print(f"\n메시지 {len(updates)}개 발견!\n")

        chat_ids = set()
        for update in updates:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_name = chat.get('first_name', 'Unknown')

                chat_ids.add(chat_id)
                print(f"Chat ID: {chat_id}")
                print(f"이름: {chat_name}")
                print("-" * 60)

        if chat_ids:
            main_chat_id = list(chat_ids)[0]
            print(f"\n당신의 Chat ID: {main_chat_id}")
            print("\n.env 파일에 추가:")
            print(f"TELEGRAM_CHAT_ID={main_chat_id}")
    else:
        print("\n메시지가 없습니다!")
        print("1. 텔레그램에서 @auto_coin_down_bot 검색")
        print("2. /start 입력")
        print("3. 아무 메시지나 보내기")
        print("4. 이 스크립트 다시 실행")
else:
    print("에러:", data.get('description'))
