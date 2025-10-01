#!/bin/bash

echo "===================================="
echo "Auto Coin Trading System"
echo "===================================="
echo ""

while true; do
    echo "[1] 데이터베이스 초기화"
    echo "[2] 데이터 수집 시작"
    echo "[3] 페이퍼 트레이딩 시작"
    echo "[4] 실전 트레이딩 시작"
    echo "[5] 종료"
    echo ""

    read -p "선택하세요 (1-5): " choice

    case $choice in
        1)
            echo ""
            echo "데이터베이스 초기화 중..."
            python3 main.py --mode init
            read -p "계속하려면 Enter를 누르세요..."
            ;;
        2)
            echo ""
            echo "데이터 수집 시작..."
            echo "(Ctrl+C로 중단)"
            python3 main.py --mode collect
            read -p "계속하려면 Enter를 누르세요..."
            ;;
        3)
            echo ""
            echo "페이퍼 트레이딩 시작..."
            echo "(Ctrl+C로 중단)"
            python3 main.py --mode run --interval 60
            read -p "계속하려면 Enter를 누르세요..."
            ;;
        4)
            echo ""
            echo "===================================="
            echo "     *** 경고: 실전 모드 ***"
            echo "===================================="
            echo ""
            echo "실전 거래를 시작합니다."
            echo "실제 자금이 사용됩니다!"
            echo ""
            read -p "정말 시작하시겠습니까? (yes/no): " confirm

            if [ "$confirm" = "yes" ]; then
                echo "실전 트레이딩 시작..."
                python3 main.py --mode run --interval 60
            else
                echo "취소되었습니다."
            fi
            read -p "계속하려면 Enter를 누르세요..."
            ;;
        5)
            echo ""
            echo "프로그램을 종료합니다."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다."
            ;;
    esac

    clear
done
