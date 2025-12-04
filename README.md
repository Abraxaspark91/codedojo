# SQL & PySpark 연습 스테이션 (LM Studio)

Gradio 기반으로 SQL/PySpark 문제를 풀고, 로컬 LLM(LM Studio)로 피드백을 받는 작은 실습용 앱입니다.

## 주요 기능
- 난이도(Lv1~Lv5)를 선택해 문제를 출제.
- 코드 에디터에 SQL 또는 PySpark 코드를 작성 후 **제출** 버튼으로 채점.
- 실행 결과 추정 → LLM 평가 → 보완점/해설 순으로 피드백.
- **문법 힌트** 버튼으로 해당 문제 유형(SQL/PySpark)의 핵심 문법 확인.
- 오답노트(`data/wrong_notes.md`)에 문제, 제출 코드, 점수, 피드백을 마크다운으로 기록.
- 오답노트에서 재도전할 문제를 선택.

문제 은행은 `data/problems.json`에서 관리하며, 본문과 함께 스키마, 샘플 데이터, 예상 키워드, 힌트를 구조화해 두었습니다. 앱 기동 시 JSON을 로드해 SQL/PySpark 난이도 5단계를 고르게 출제합니다.

## 🚀 빠른 시작

### 1단계: 설치하기
더블클릭으로 간단하게 설치할 수 있습니다!

**Windows 사용자:**
- `setup_windows.bat` 파일을 더블클릭하세요
- "Y"를 입력해서 설치를 시작하세요

**Mac 사용자:**
- `setup_mac.command` 파일을 더블클릭하세요
- "Y"를 입력해서 설치를 시작하세요

설치가 완료되면 `.venv` 폴더와 필요한 모든 프로그램이 자동으로 설치됩니다.

### 2단계: 실행하기

**먼저 LM Studio를 준비하세요:**
1. LM Studio를 실행하세요
2. 모델을 로드하세요 (추천: Llama 3.2 3B Instruct 이상)
3. "Start Server" 버튼을 클릭하세요

**그 다음 CodeDojo를 실행하세요:**

**Windows 사용자:**
- `run_codedojo.bat` 파일을 더블클릭하세요

**Mac 사용자:**
- `run_codedojo.command` 파일을 더블클릭하세요
- (또는 `CodeDojo.app`을 사용하세요 - 추후 제공 예정)

자동으로 브라우저가 열리고 CodeDojo가 실행됩니다!

---

## 🎯 Windows 고급 기능

Windows 사용자를 위한 더 편리한 기능들입니다!

### 콘솔 창 없이 실행 (VBS 래퍼)

콘솔 창이 보기 싫다면 VBS 래퍼를 사용하세요:

**설치:**
- `setup_windows.vbs` 더블클릭
- (콘솔 창이 표시되어 진행 상황을 볼 수 있습니다)

**실행:**
- `run_codedojo.vbs` 더블클릭
- 콘솔 창 없이 깔끔하게 실행됩니다!
- 메시지박스로 상태를 알려줍니다
- Python이나 가상환경이 없으면 친절하게 안내해줍니다

### 데스크톱 바로가기 만들기

`create_shortcuts.vbs`를 더블클릭하면:
- 데스크톱에 "CodeDojo 설치" 바로가기 생성
- 데스크톱에 "CodeDojo 실행" 바로가기 생성
- 커스텀 아이콘 지원 (아래 참조)

### 커스텀 아이콘 추가

1. `.ico` 형식의 아이콘 파일을 준비하세요
2. 파일 이름을 `icon.ico`로 변경
3. CodeDojo 프로젝트 폴더에 넣으세요
4. `create_shortcuts.vbs`를 실행하세요

📖 자세한 가이드: [ICON_GUIDE.md](ICON_GUIDE.md) 참조

---

## 수동 설치 및 실행 (개발자용)

### 설치
1. Python 3.8 이상이 설치되어 있는지 확인하세요.
2. 필요한 패키지를 설치합니다.
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   # 또는
   .venv\Scripts\activate.bat  # Windows

   pip install -r requirements.txt
   ```

### 실행
1. LM Studio 서버를 켜고 Chat Completion 엔드포인트를 엽니다. 기본 주소는 `http://localhost:1234/v1/chat/completions`입니다. 다른 주소를 쓰려면 `.env` 파일에 `LM_STUDIO_ENDPOINT=<엔드포인트>`를 적어주세요.
2. 앱을 실행합니다.
   ```bash
   python app.py
   ```
3. 브라우저로 Gradio가 안내하는 주소(보통 `http://127.0.0.1:7860`)에 접속해 문제를 풀고 제출하세요.

## 오답노트 포맷
`data/wrong_notes.md`에 각 시도마다 메타데이터(JSON), 문제, 제출 코드, 피드백, 보완점, 해설이 순서대로 마크다운으로 추가됩니다.

## 주의
- LLM 서버 연결이 실패하면 오류가 발생합니다.
- 실제 데이터베이스/스파크 클러스터는 포함되어 있지 않으며, 키워드 기반으로 실행 결과를 추정합니다.
