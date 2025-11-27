# SQL & PySpark 연습 스테이션 (LM Studio)

Gradio 기반으로 SQL/PySpark 문제를 풀고, 로컬 LLM(LM Studio)로 피드백을 받는 작은 실습용 앱입니다.

## 주요 기능
- 난이도(Lv1~Lv5)를 선택해 문제를 출제.
- 코드 에디터에 SQL 또는 PySpark 코드를 작성 후 **제출** 버튼으로 채점.
- LLM 응답은 `stream=false`로 받아 오며, 채점 중에는 Gradio 프로그레스 스피너가 표시됩니다.
- 실행 결과 추정 → LLM 평가 → 보완점/해설 순으로 피드백.
- **문법 힌트** 버튼으로 해당 문제 유형(SQL/PySpark)의 핵심 문법 확인.
- 오답노트(`data/wrong_notes.md`)에 문제, 제출 코드, 점수, 피드백을 마크다운으로 기록.
- 오답노트에서 재도전할 문제를 선택하거나, 무작위 재도전 출제(확률적) 기능 제공.

문제 은행은 `problem_bank.py`에서 관리하며 SQL/PySpark 각각 난이도 5단계를 고르게 커버하도록 구성했습니다.

## 실행 방법
1. LM Studio 서버를 켜고 Chat Completion 엔드포인트를 엽니다. 기본 주소는 `http://localhost:1234/v1/chat/completions`입니다. 다른 주소를 쓰려면 `.env` 파일에 `LM_STUDIO_ENDPOINT=<엔드포인트>`를 적어주세요.
2. 필요한 패키지를 설치합니다. (Python 3.12 이상에서는 `audioop-lts`가 `pyaudioop` 모듈을 제공해 Gradio의 오디오 의존성 문제를 방지합니다.)
   ```bash
   pip install -r requirements.txt
   ```
3. 앱을 실행합니다.
   ```bash
   python app.py
   ```
4. 브라우저로 Gradio가 안내하는 주소에 접속해 문제를 풀고 제출하세요.

## 오답노트 포맷
`data/wrong_notes.md`에 각 시도마다 메타데이터(JSON), 문제, 제출 코드, 피드백, 보완점, 해설이 순서대로 마크다운으로 추가됩니다. 점수 80점 미만의 항목이 재도전 후보가 됩니다.

## 주의
- LLM 서버 연결이 실패하면 기본 휴리스틱 점수와 힌트를 제공합니다.
- 실제 데이터베이스/스파크 클러스터는 포함되어 있지 않으며, 키워드 기반으로 실행 결과를 추정합니다.
