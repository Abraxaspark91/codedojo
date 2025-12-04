@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ====================================================================
:: CodeDojo 설치 스크립트 (Windows용)
:: ====================================================================
:: 이 프로그램은 CodeDojo를 사용하기 위해 필요한 것들을 설치합니다.
:: ====================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    CodeDojo 설치 프로그램                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 안녕하세요! CodeDojo 설치를 시작합니다.
echo.
echo [무엇을 설치하나요?]
echo   1. 파이썬 가상환경 (.venv 폴더)
echo   2. 필요한 프로그램들 (gradio, requests 등)
echo.
echo [얼마나 걸리나요?]
echo   - 인터넷 속도에 따라 1~3분 정도 걸립니다.
echo.
echo [어디에 설치되나요?]
echo   - 지금 이 폴더: %CD%
echo.

set /p CONFIRM="설치를 시작할까요? (Y/N): "
if /I not "%CONFIRM%"=="Y" (
    echo.
    echo 설치를 취소했습니다. 다음에 또 만나요!
    echo.
    pause
    exit /b 0
)

echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ 1단계: Python이 설치되어 있는지 확인하고 있어요...            │
echo └────────────────────────────────────────────────────────────────┘
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python을 찾을 수 없어요!
    echo.
    echo [해결 방법]
    echo   1. https://python.org 에 접속하세요
    echo   2. "Downloads"를 클릭하세요
    echo   3. Python 3.8 이상 버전을 다운로드하세요
    echo   4. 설치할 때 "Add Python to PATH"를 꼭 체크하세요!
    echo   5. 설치 후 컴퓨터를 재시작하세요
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [√] Python %PYTHON_VERSION% 를 찾았어요!

echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ 2단계: 가상환경을 만들고 있어요...                            │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo [가상환경이 뭔가요?]
echo   프로그램들을 따로 보관하는 방입니다.
echo   다른 프로젝트와 섞이지 않게 해줘요!
echo.

if exist ".venv\" (
    echo [!] 이미 .venv 폴더가 있어요. 건너뛸게요.
) else (
    echo .venv 폴더를 만들고 있어요...
    python -m venv .venv
    if errorlevel 1 (
        echo [X] 가상환경을 만드는데 실패했어요!
        echo.
        pause
        exit /b 1
    )
    echo [√] 가상환경을 만들었어요!
)

echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ 3단계: 필요한 프로그램들을 설치하고 있어요...                 │
echo └────────────────────────────────────────────────────────────────┘
echo.
echo [어떤 프로그램들인가요?]
echo   - Gradio: 웹 화면을 만들어주는 프로그램
echo   - Requests: 인터넷으로 정보를 주고받는 프로그램
echo   - 그 외 필요한 것들
echo.
echo 잠깐만 기다려주세요... (1~3분 소요)
echo.

call .venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [X] pip 업그레이드에 실패했어요!
    echo.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [X] 프로그램 설치에 실패했어요!
    echo.
    echo [해결 방법]
    echo   1. 인터넷 연결을 확인하세요
    echo   2. requirements.txt 파일이 있는지 확인하세요
    echo   3. 위의 에러 메시지를 확인하세요
    echo.
    pause
    exit /b 1
)

echo.
echo ┌────────────────────────────────────────────────────────────────┐
echo │ 4단계: 설치가 완료되었는지 확인하고 있어요...                 │
echo └────────────────────────────────────────────────────────────────┘
echo.

python -c "import gradio" 2>nul
if errorlevel 1 (
    echo [X] 설치 확인에 실패했어요!
    echo.
    pause
    exit /b 1
)

echo [√] 모든 프로그램이 제대로 설치되었어요!

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    설치 완료! 🎉                               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo [다음 단계]
echo   1. LM Studio를 실행하세요
echo   2. 모델을 로드하세요 (Server 시작)
echo   3. "run_codedojo.bat" 파일을 더블클릭하세요
echo.
echo 즐거운 코딩 되세요! 🥋
echo.
pause
