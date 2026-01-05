# CodeDojo

SQL과 Python 코딩을 연습할 수 있는 AI 기반 학습 도구입니다. LM Studio의 로컬 AI 모델을 활용하여 문제 풀이, 피드백, 오답노트 관리 등의 기능을 제공합니다.

## 설치 및 실행 방법

### 1. LM Studio 설치
[LM Studio](https://lmstudio.ai/)를 다운로드하여 설치합니다. 로컬에서 AI 모델을 실행하여 코딩 문제에 대한 피드백과 힌트를 제공받을 수 있습니다.

### 2. 개발 환경 설치

**uv 설치** ([공식 사이트](https://docs.astral.sh/uv/)): Python 패키지 관리 도구로, 기존 pip보다 빠르고 효율적으로 의존성을 관리합니다.

**Node.js 설치** ([공식 사이트](https://nodejs.org/)): Electron 데스크톱 앱을 실행하기 위해 필요합니다.

**Git 설치** ([공식 사이트](https://git-scm.com/)): GitHub에서 소스 코드를 다운로드(clone)하기 위해 필요합니다.

### 3. 프로젝트 다운로드 및 설정

**GitHub에서 프로젝트 복사하기**
```bash
git clone https://github.com/Abraxaspark91/codedojo.git
```

**프로젝트 폴더로 이동**
```bash
cd codedojo
```

**Python 의존성 설치**
```bash
uv sync
```
이 명령어는 프로젝트에 필요한 Python 라이브러리(Gradio, requests 등)를 자동으로 설치합니다.

**Node.js 의존성 설치**
```bash
npm install
```
이 명령어는 Electron과 관련된 패키지들을 설치합니다.

### 4. 애플리케이션 실행

명령 프롬프트(cmd) 또는 터미널에서 다음 명령어를 실행합니다:
```bash
npm start
```

### 5. AI 모델 준비

**처음 사용하는 경우**: LM Studio를 열고 추천 모델을 다운로드합니다. 모델 선택 후 서버를 시작하세요.

**모델이 이미 있는 경우**: LM Studio에서 원하는 모델을 선택하고 로컬 서버를 시작합니다. 기본 엔드포인트는 `http://127.0.0.1:1234`입니다.

** VRAM/시스템RAM별 추천 모델 **
! GPU가 있으면 없을 때보다 15배정도 빨라요. 아래 모델들은 CPU로도 채점에 2분정도 걸리는 모델들이에요.
- 2GB~4GB : Qwen3-4B-Instruct-2507 Q4_K_M
- 4GB~6GB : Qwen3-4B-Instruct-2507 Q6_K
- 6GB~14GB : Qwen3-4B-Instruct-2507 Q8_0
- 14GB~20GB : GPT-OSS-20B MXFP4
- 20GB~24GB : Qwen3-30B-A3B Q4_K_M
- 24GB~30GB :  Qwen3-30B-A3B Q5_K_M
- 30GB~ : Qwen3-30B-A3B Q6_K

## 주요 기능

**문제 풀이**: 난이도별(Lv0~Lv3), 언어별(SQL, Python, PySpark)로 분류된 문제를 선택하여 풀 수 있습니다.

**AI 피드백**: 제출한 답안에 대해 AI가 피드백을 제공하고, 막힐 때 힌트를 요청할 수 있습니다.

**오답노트**: 틀린 문제를 별명을 지어서 저장하고, 나중에 다시 풀어볼 수 있습니다.

**즐겨찾기**: 자주 복습하고 싶은 문제를 즐겨찾기로 표시하여 빠르게 접근할 수 있습니다.

## 커스터마이징

`data/problems.json` 파일에서 문제 데이터를 확인할 수 있습니다. 아래 스키마 형식을 맞추면 직접 문제를 추가하거나 다른 문제 은행으로 교체할 수 있습니다:

```json
{
  "pid": "고유_문제_ID",
  "title": "문제 제목",
  "body": "문제 설명",
  "difficulty": "Lv0 입문",
  "kind": "SQL",
  "problem_type": "코딩",
  "schema": "테이블명(컬럼명 타입, ...)",
  "sample_rows": ["샘플 데이터"],
  "hint": "힌트 내용"
}
```

## 문제 발생 시

- LM Studio 서버가 실행 중인지 확인하세요
- `.env` 파일에서 `LM_STUDIO_ENDPOINT` 설정을 확인하세요
- Python 또는 Node.js 버전 호환성 문제가 있다면 최신 LTS 버전 사용을 권장합니다
