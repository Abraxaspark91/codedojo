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
