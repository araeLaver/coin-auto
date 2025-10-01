@echo off
echo ====================================
echo Auto Coin Trading System
echo ====================================
echo.

:menu
echo [1] 데이터베이스 초기화
echo [2] 데이터 수집 시작
echo [3] 페이퍼 트레이딩 시작
echo [4] 실전 트레이딩 시작
echo [5] 종료
echo.

set /p choice="선택하세요 (1-5): "

if "%choice%"=="1" goto init
if "%choice%"=="2" goto collect
if "%choice%"=="3" goto paper
if "%choice%"=="4" goto live
if "%choice%"=="5" goto end

echo 잘못된 선택입니다.
goto menu

:init
echo.
echo 데이터베이스 초기화 중...
python main.py --mode init
pause
goto menu

:collect
echo.
echo 데이터 수집 시작...
echo (Ctrl+C로 중단)
python main.py --mode collect
pause
goto menu

:paper
echo.
echo 페이퍼 트레이딩 시작...
echo (Ctrl+C로 중단)
python main.py --mode run --interval 60
pause
goto menu

:live
echo.
echo ====================================
echo     *** 경고: 실전 모드 ***
echo ====================================
echo.
echo 실전 거래를 시작합니다.
echo 실제 자금이 사용됩니다!
echo.
set /p confirm="정말 시작하시겠습니까? (yes/no): "

if /i "%confirm%"=="yes" (
    echo 실전 트레이딩 시작...
    python main.py --mode run --interval 60
) else (
    echo 취소되었습니다.
)
pause
goto menu

:end
echo.
echo 프로그램을 종료합니다.
exit
