"""
텔레그램 설정 헬퍼 스크립트
봇 토큰과 Chat ID를 입력받아 테스트
"""

import requests
import sys


def test_telegram(bot_token, chat_id):
    """텔레그램 연결 테스트"""

    print("\n" + "=" * 60)
    print("📱 텔레그램 연결 테스트")
    print("=" * 60)

    # 1. 봇 정보 확인
    print("\n1️⃣  봇 정보 확인 중...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"   ✅ 봇 이름: {bot_info['first_name']}")
                print(f"   ✅ 봇 사용자명: @{bot_info['username']}")
            else:
                print(f"   ❌ 실패: {data.get('description')}")
                return False
        else:
            print(f"   ❌ HTTP 에러: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 에러: {e}")
        return False

    # 2. 테스트 메시지 전송
    print("\n2️⃣  테스트 메시지 전송 중...")
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': '🎉 <b>텔레그램 연동 성공!</b>\n\n자동매매 알림을 받을 준비가 되었습니다.',
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("   ✅ 메시지 전송 성공!")
                print("   ✅ 텔레그램 앱에서 메시지를 확인하세요!")
                return True
            else:
                print(f"   ❌ 실패: {data.get('description')}")
                return False
        else:
            print(f"   ❌ HTTP 에러: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ 에러: {e}")
        return False


def get_chat_id_from_updates(bot_token):
    """최근 메시지에서 Chat ID 찾기"""

    print("\n" + "=" * 60)
    print("🔍 Chat ID 찾기")
    print("=" * 60)
    print("\n먼저 봇에게 아무 메시지나 보내세요!")
    print("예: /start 또는 'hello'\n")

    input("메시지를 보냈으면 Enter를 누르세요...")

    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get('ok') and data.get('result'):
                updates = data['result']

                print(f"\n📬 {len(updates)}개의 메시지를 찾았습니다:\n")

                chat_ids = set()
                for update in updates:
                    if 'message' in update:
                        chat = update['message']['chat']
                        chat_id = chat['id']
                        chat_name = chat.get('first_name', 'Unknown')

                        chat_ids.add(chat_id)
                        print(f"   Chat ID: {chat_id} (이름: {chat_name})")

                if chat_ids:
                    print(f"\n✅ Chat ID를 찾았습니다!")
                    return list(chat_ids)[0]
                else:
                    print("\n❌ Chat ID를 찾지 못했습니다.")
                    print("   봇에게 메시지를 보냈는지 확인하세요.")
                    return None
            else:
                print("❌ 메시지가 없습니다.")
                print("   봇에게 /start를 보내세요.")
                return None
        else:
            print(f"❌ HTTP 에러: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 에러: {e}")
        return None


def main():
    print("\n" + "=" * 60)
    print("🤖 텔레그램 봇 설정 헬퍼")
    print("=" * 60)

    print("\n옵션을 선택하세요:")
    print("1. 봇 토큰과 Chat ID가 있음 (테스트)")
    print("2. Chat ID를 모름 (찾기)")

    choice = input("\n선택 (1 또는 2): ").strip()

    if choice == "1":
        # 토큰과 Chat ID 입력받기
        print("\n" + "-" * 60)
        bot_token = input("봇 토큰을 입력하세요: ").strip()
        chat_id = input("Chat ID를 입력하세요: ").strip()

        if bot_token and chat_id:
            success = test_telegram(bot_token, chat_id)

            if success:
                print("\n" + "=" * 60)
                print("✅ 설정 완료!")
                print("=" * 60)
                print("\n다음 단계:")
                print("1. .env 파일에 추가:")
                print(f"   TELEGRAM_BOT_TOKEN={bot_token}")
                print(f"   TELEGRAM_CHAT_ID={chat_id}")
                print("\n2. Koyeb 환경변수에도 추가하세요!")
            else:
                print("\n❌ 연결 실패. 토큰과 Chat ID를 확인하세요.")
        else:
            print("❌ 토큰과 Chat ID를 모두 입력해야 합니다.")

    elif choice == "2":
        # Chat ID 찾기
        print("\n" + "-" * 60)
        bot_token = input("봇 토큰을 입력하세요: ").strip()

        if bot_token:
            chat_id = get_chat_id_from_updates(bot_token)

            if chat_id:
                print("\n" + "=" * 60)
                print(f"✅ Chat ID: {chat_id}")
                print("=" * 60)
                print("\n이제 옵션 1번으로 테스트하세요!")
        else:
            print("❌ 봇 토큰을 입력해야 합니다.")

    else:
        print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n종료합니다.")
        sys.exit(0)
