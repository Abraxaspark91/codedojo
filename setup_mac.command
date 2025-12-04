#!/bin/bash

# ====================================================================
# CodeDojo 설치 스크립트 (Mac용)
# ====================================================================
# 이 프로그램은 CodeDojo를 사용하기 위해 필요한 것들을 설치합니다.
# ====================================================================

# 현재 스크립트가 위치한 디렉토리로 이동
cd "$(dirname "$0")" || exit 1

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    CodeDojo 설치 프로그램                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "안녕하세요! CodeDojo 설치를 시작합니다."
echo ""
echo "[무엇을 설치하나요?]"
echo "  1. 파이썬 가상환경 (.venv 폴더)"
echo "  2. 필요한 프로그램들 (gradio, requests 등)"
echo ""
echo "[얼마나 걸리나요?]"
echo "  - 인터넷 속도에 따라 1~3분 정도 걸립니다."
echo ""
echo "[어디에 설치되나요?]"
echo "  - 지금 이 폴더: $(pwd)"
echo ""

read -p "설치를 시작할까요? (Y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo ""
    echo "설치를 취소했습니다. 다음에 또 만나요!"
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 0
fi

echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ 1단계: Python이 설치되어 있는지 확인하고 있어요...            │"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""

# Python 확인 (python3 우선, python도 체크)
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}[X] Python을 찾을 수 없어요!${NC}"
    echo ""
    echo "[해결 방법]"
    echo "  1. https://python.org 에 접속하세요"
    echo "  2. 'Downloads'를 클릭하세요"
    echo "  3. Python 3.8 이상 버전을 다운로드하세요"
    echo "  4. 또는 Homebrew로 설치: brew install python3"
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[√]${NC} Python $PYTHON_VERSION 를 찾았어요!"

echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ 2단계: 가상환경을 만들고 있어요...                            │"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""
echo "[가상환경이 뭔가요?]"
echo "  프로그램들을 따로 보관하는 방입니다."
echo "  다른 프로젝트와 섞이지 않게 해줘요!"
echo ""

if [ -d ".venv" ]; then
    echo -e "${YELLOW}[!]${NC} 이미 .venv 폴더가 있어요. 건너뛸게요."
else
    echo ".venv 폴더를 만들고 있어요..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] 가상환경을 만드는데 실패했어요!${NC}"
        echo ""
        read -p "아무 키나 눌러 종료하세요..."
        exit 1
    fi
    echo -e "${GREEN}[√]${NC} 가상환경을 만들었어요!"
fi

echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ 3단계: 필요한 프로그램들을 설치하고 있어요...                 │"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""
echo "[어떤 프로그램들인가요?]"
echo "  - Gradio: 웹 화면을 만들어주는 프로그램"
echo "  - Requests: 인터넷으로 정보를 주고받는 프로그램"
echo "  - 그 외 필요한 것들"
echo ""
echo "잠깐만 기다려주세요... (1~3분 소요)"
echo ""

# 가상환경 활성화
source .venv/bin/activate

# pip 업그레이드
$PYTHON_CMD -m pip install --upgrade pip --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] pip 업그레이드에 실패했어요!${NC}"
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

# requirements.txt 설치
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[X] 프로그램 설치에 실패했어요!${NC}"
    echo ""
    echo "[해결 방법]"
    echo "  1. 인터넷 연결을 확인하세요"
    echo "  2. requirements.txt 파일이 있는지 확인하세요"
    echo "  3. 위의 에러 메시지를 확인하세요"
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

echo ""
echo "┌────────────────────────────────────────────────────────────────┐"
echo "│ 4단계: 설치가 완료되었는지 확인하고 있어요...                 │"
echo "└────────────────────────────────────────────────────────────────┘"
echo ""

$PYTHON_CMD -c "import gradio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] 설치 확인에 실패했어요!${NC}"
    echo ""
    read -p "아무 키나 눌러 종료하세요..."
    exit 1
fi

echo -e "${GREEN}[√]${NC} 모든 프로그램이 제대로 설치되었어요!"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    설치 완료! 🎉                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "[다음 단계]"
echo "  1. LM Studio를 실행하세요"
echo "  2. 모델을 로드하세요 (Server 시작)"
echo "  3. 'CodeDojo.app' 또는 'run_codedojo.command' 파일을 더블클릭하세요"
echo ""
echo "즐거운 코딩 되세요! 🥋"
echo ""
read -p "아무 키나 눌러 종료하세요..."
