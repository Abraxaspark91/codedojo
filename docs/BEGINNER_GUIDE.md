# CodeDojo 초보자를 위한 완벽 가이드 🚀

이 문서는 프로그래밍을 처음 접하는 분들을 위해 작성되었습니다. Python, Git, 터미널 등의 개념을 처음 듣는 분들도 CodeDojo를 설치하고 사용할 수 있도록 최대한 자세히 설명합니다.

---

## 📚 목차

1. [시작하기 전에 - 기본 용어 설명](#1-시작하기-전에---기본-용어-설명)
2. [준비물 확인](#2-준비물-확인)
3. [Python 설치하기](#3-python-설치하기)
4. [Git 설치하기](#4-git-설치하기)
5. [LM Studio 설치하기](#5-lm-studio-설치하기)
6. [CodeDojo 다운로드하기](#6-codedojo-다운로드하기)
7. [CodeDojo 실행하기](#7-codedojo-실행하기)
8. [CodeDojo 사용하기](#8-codedojo-사용하기)
9. [문제 해결](#9-문제-해결)

---

## 1. 시작하기 전에 - 기본 용어 설명

프로그래밍을 처음 접하면 생소한 용어들이 많이 나옵니다. 먼저 자주 등장하는 용어들을 쉽게 설명하겠습니다.

### 💻 터미널(Terminal) / CMD / 명령 프롬프트란?
- **쉽게 말하면**: 컴퓨터에게 문자로 명령을 내리는 검은 화면
- **비유**: 마우스로 클릭하는 대신 키보드로 명령어를 타이핑해서 컴퓨터를 조작하는 도구
- **Windows에서는**: "명령 프롬프트(CMD)" 또는 "PowerShell"이라고 부름
- **Mac에서는**: "터미널(Terminal)"이라고 부름

### 🐍 Python이란?
- **쉽게 말하면**: 프로그래밍 언어 중 하나 (영어, 한국어처럼 컴퓨터와 대화하는 언어)
- **특징**: 배우기 쉽고, 많은 사람들이 사용하는 인기 있는 언어
- **CodeDojo에서의 역할**: CodeDojo는 Python으로 만들어진 프로그램입니다

### 📦 가상환경(Virtual Environment)이란?
- **쉽게 말하면**: 프로젝트마다 독립적인 작업 공간을 만드는 것
- **비유**:
  - 가상환경 없이 작업 = 모든 책을 한 방에 쌓아두기 (섞이고 헷갈림)
  - 가상환경 사용 = 과목별로 방을 나눠서 책을 정리 (깔끔하고 충돌 없음)
- **왜 필요한가**: 프로젝트마다 다른 버전의 도구를 사용할 수 있고, 서로 충돌하지 않음

### 🔗 의존성(Dependencies)이란?
- **쉽게 말하면**: 프로그램이 작동하기 위해 필요한 다른 프로그램들
- **비유**: 케이크를 만들려면 밀가루, 설탕, 계란 등이 필요하듯이, CodeDojo를 실행하려면 gradio, requests 같은 라이브러리가 필요
- **CodeDojo의 의존성**: `requirements.txt` 파일에 적혀있음

### 🌐 Git과 GitHub이란?
- **Git**: 코드의 변경 이력을 관리하는 도구 (마치 "실행 취소" 기능의 강력한 버전)
- **GitHub**: 코드를 저장하고 공유하는 온라인 저장소 (마치 코드를 위한 네이버 클라우드)
- **비유**:
  - Git = 사진 찍기 (변경사항을 기록)
  - GitHub = 사진 저장소 (온라인에 저장하고 공유)

### 🤖 LLM / LM Studio란?
- **LLM**: Large Language Model의 약자. ChatGPT처럼 사람과 대화할 수 있는 인공지능
- **LM Studio**: 자신의 컴퓨터에서 LLM을 실행할 수 있게 해주는 프로그램
- **CodeDojo에서의 역할**: 당신이 작성한 코드를 평가하고 피드백을 주는 AI 선생님

---

## 2. 준비물 확인

CodeDojo를 사용하려면 다음이 필요합니다:

✅ **컴퓨터 요구사항**
- Windows 10 이상 또는 macOS 10.13 이상
- 저장 공간: 최소 5GB 이상 (LM Studio 모델 포함)
- RAM: 8GB 이상 권장 (LLM 실행을 위해)

✅ **설치할 프로그램**
1. Python 3.8 이상
2. Git
3. LM Studio
4. CodeDojo (이 프로젝트)

✅ **인터넷 연결**
- 초기 설치 시 필요 (파일 다운로드용)

---

## 3. Python 설치하기

### 🪟 Windows 사용자

#### 3-1. Python 다운로드
1. 웹브라우저를 열고 https://www.python.org/downloads/ 접속
2. 노란색 "Download Python 3.x.x" 버튼 클릭
3. 다운로드된 파일(python-3.x.x-amd64.exe) 실행

#### 3-2. Python 설치
1. 설치 화면이 나타나면 **매우 중요**:
   - ✅ **"Add Python 3.x to PATH"** 체크박스를 **반드시 체크**
   - 이 체크박스를 놓치면 나중에 Python을 찾을 수 없습니다!
2. "Install Now" 클릭
3. 설치 완료까지 기다림 (1-2분 소요)
4. "Close" 버튼 클릭

#### 3-3. 설치 확인
1. **시작 메뉴**에서 "cmd" 또는 "명령 프롬프트" 검색
2. 명령 프롬프트 실행 (검은 화면이 나타남)
3. 다음 명령어 입력 후 Enter:
   ```
   python --version
   ```
4. `Python 3.x.x`라고 표시되면 성공!
   - 만약 "python은 내부 또는 외부 명령이 아닙니다" 에러가 나오면:
     - Python 설치 시 "Add to PATH" 체크를 안 했을 가능성이 높음
     - Python을 다시 설치하거나 [문제 해결](#9-문제-해결) 섹션 참조

### 🍎 Mac 사용자

#### 3-1. Python 다운로드
1. 웹브라우저를 열고 https://www.python.org/downloads/ 접속
2. 노란색 "Download Python 3.x.x" 버튼 클릭
3. 다운로드된 파일(python-3.x.x-macos11.pkg) 실행

#### 3-2. Python 설치
1. 설치 마법사가 나타나면 "계속" 버튼 클릭
2. 라이선스 동의 후 "계속" → "동의" 클릭
3. "설치" 버튼 클릭
4. Mac 비밀번호 입력
5. 설치 완료까지 기다림 (1-2분 소요)
6. "닫기" 버튼 클릭

#### 3-3. 설치 확인
1. **Spotlight 검색** (⌘ + Space) 또는 **Launchpad**에서 "터미널" 검색
2. 터미널 실행
3. 다음 명령어 입력 후 Enter:
   ```bash
   python3 --version
   ```
4. `Python 3.x.x`라고 표시되면 성공!

> **Mac 참고사항**: Mac에서는 `python` 대신 `python3` 명령어를 사용합니다.

---

## 4. Git 설치하기

### 🪟 Windows 사용자

#### 4-1. Git 다운로드
1. 웹브라우저를 열고 https://git-scm.com/download/win 접속
2. "64-bit Git for Windows Setup" 자동 다운로드 시작
3. 다운로드된 파일(Git-2.x.x-64-bit.exe) 실행

#### 4-2. Git 설치
1. 설치 화면이 나타나면 대부분 **기본 설정 그대로** "Next" 클릭
2. 중요한 옵션:
   - "Adjusting your PATH environment" 화면: **"Git from the command line and also from 3rd-party software"** 선택 (기본값)
   - 나머지는 모두 기본값으로 진행
3. "Install" 클릭
4. 설치 완료 후 "Finish" 클릭

#### 4-3. 설치 확인
1. 명령 프롬프트(CMD) 열기
2. 다음 명령어 입력:
   ```
   git --version
   ```
3. `git version 2.x.x`라고 표시되면 성공!

### 🍎 Mac 사용자

#### 4-1. Git 설치 (두 가지 방법)

**방법 1: Homebrew 사용 (권장)**
1. 터미널 열기
2. 다음 명령어 입력 (Homebrew 설치):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. 비밀번호 입력 후 진행
4. Homebrew 설치 후 Git 설치:
   ```bash
   brew install git
   ```

**방법 2: 공식 설치 파일 사용**
1. https://git-scm.com/download/mac 접속
2. 설치 파일 다운로드 및 실행
3. 설치 마법사 따라 진행

#### 4-2. 설치 확인
1. 터미널 열기
2. 다음 명령어 입력:
   ```bash
   git --version
   ```
3. `git version 2.x.x`라고 표시되면 성공!

### 🔧 Git 초기 설정

Git을 처음 사용하는 경우 사용자 정보를 설정해야 합니다:

1. 터미널 또는 명령 프롬프트 열기
2. 다음 명령어 입력 (이메일과 이름을 자신의 것으로 변경):
   ```bash
   git config --global user.name "홍길동"
   git config --global user.email "hong@example.com"
   ```

---

## 5. LM Studio 설치하기

LM Studio는 당신의 코드를 평가해줄 AI를 실행하는 프로그램입니다.

### 5-1. LM Studio 다운로드

1. 웹브라우저를 열고 https://lmstudio.ai/ 접속
2. "Download for Windows" 또는 "Download for Mac" 버튼 클릭
3. 다운로드된 파일 실행:
   - **Windows**: `LM-Studio-Setup.exe` 실행
   - **Mac**: `LM-Studio.dmg` 열고 응용 프로그램 폴더로 드래그

### 5-2. LM Studio 설치 및 실행

**Windows:**
1. 설치 마법사 따라 진행 ("Next" → "Install")
2. 설치 완료 후 LM Studio 실행

**Mac:**
1. DMG 파일을 열고 LM Studio 아이콘을 Applications 폴더로 드래그
2. Applications 폴더에서 LM Studio 실행
3. "확인되지 않은 개발자" 경고가 나오면:
   - 시스템 환경설정 → 보안 및 개인 정보 보호 → "확인 없이 열기" 클릭

### 5-3. AI 모델 다운로드

LM Studio를 처음 실행하면 AI 모델을 다운로드해야 합니다:

1. LM Studio 실행
2. 왼쪽 메뉴에서 **"Discover"** (🔍 검색 아이콘) 클릭
3. 검색창에 다음 중 하나 입력:
   - `Llama-3-8B` (초보자 권장, 약 4.7GB)
   - `Mistral-7B` (대안, 약 4.1GB)
   - `Phi-3-mini` (가벼운 모델, 약 2.3GB)
4. 모델 옆의 **"Download"** 버튼 클릭
5. 다운로드 완료까지 기다림 (인터넷 속도에 따라 10-30분 소요)

> **저장 공간 참고**: AI 모델은 크기가 큽니다. 최소 5-10GB의 여유 공간이 필요합니다.

### 5-4. LM Studio 서버 실행

CodeDojo를 사용하려면 LM Studio를 서버 모드로 실행해야 합니다:

1. LM Studio에서 왼쪽 메뉴의 **"Local Server"** (⚡ 아이콘) 클릭
2. 상단에서 다운로드한 모델 선택 (예: llama-3-8b-instruct)
3. **"Start Server"** 버튼 클릭
4. 서버가 시작되면 화면에 다음과 같이 표시됨:
   ```
   Server running on http://localhost:1234
   ```
5. 이 상태로 유지! (CodeDojo 사용 중에는 LM Studio를 종료하지 마세요)

> **중요**: CodeDojo를 사용할 때마다 LM Studio 서버를 먼저 시작해야 합니다!

---

## 6. CodeDojo 다운로드하기

이제 CodeDojo 프로젝트를 자신의 컴퓨터로 가져옵니다.

### 6-1. GitHub에서 CodeDojo 다운로드

**방법 1: Git으로 클론 (권장)**

1. 터미널 또는 명령 프롬프트 열기
2. CodeDojo를 저장할 위치로 이동:

   **Windows 예시** (Documents 폴더에 저장):
   ```
   cd C:\Users\내사용자명\Documents
   ```

   **Mac 예시** (Documents 폴더에 저장):
   ```bash
   cd ~/Documents
   ```

   > **팁**: "내사용자명" 부분은 자신의 Windows 사용자 이름으로 변경하세요.

3. CodeDojo 클론 (복사):
   ```bash
   git clone https://github.com/Abraxaspark91/codedojo.git
   ```

4. 다운로드가 완료되면 CodeDojo 폴더로 이동:
   ```bash
   cd codedojo
   ```

**방법 2: ZIP 파일로 다운로드**

1. 웹브라우저에서 https://github.com/Abraxaspark91/codedojo 접속
2. 초록색 **"Code"** 버튼 클릭
3. **"Download ZIP"** 클릭
4. 다운로드된 `codedojo-main.zip` 파일 압축 해제
5. 압축 해제된 폴더 이름을 `codedojo`로 변경
6. 터미널/명령 프롬프트에서 해당 폴더로 이동

### 6-2. 현재 위치 확인

터미널에서 현재 어디에 있는지 확인:

**Windows:**
```
cd
```

**Mac/Linux:**
```bash
pwd
```

`codedojo` 폴더 안에 있어야 합니다. 예:
- Windows: `C:\Users\내사용자명\Documents\codedojo`
- Mac: `/Users/내사용자명/Documents/codedojo`

---

## 7. CodeDojo 실행하기

이제 CodeDojo를 실행할 차례입니다!

### 7-1. 가상환경 생성

가상환경은 CodeDojo만을 위한 독립된 작업 공간을 만듭니다.

**Windows:**
```
python -m venv .venv
```

**Mac:**
```bash
python3 -m venv .venv
```

> 명령어 설명:
> - `python -m venv`: "가상환경을 만들어줘"
> - `.venv`: 가상환경 폴더 이름 (점으로 시작하면 숨김 폴더)

이 명령어를 실행하면 `.venv`라는 폴더가 생성됩니다 (1-2분 소요).

### 7-2. 가상환경 활성화

생성한 가상환경을 "켜는" 단계입니다.

**Windows (CMD):**
```
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

> **PowerShell 에러 해결**: "이 시스템에서 스크립트를 실행할 수 없습니다" 에러가 나오면:
> 1. PowerShell을 **관리자 권한으로 실행**
> 2. 다음 명령어 입력:
>    ```powershell
>    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
>    ```
> 3. "Y" 입력 후 Enter
> 4. PowerShell 닫고 다시 일반 PowerShell로 실행

**Mac:**
```bash
source .venv/bin/activate
```

가상환경이 활성화되면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다:
```
(.venv) C:\Users\name\Documents\codedojo>
```

### 7-3. 의존성 설치

CodeDojo가 작동하기 위해 필요한 라이브러리들을 설치합니다:

```bash
pip install -r requirements.txt
```

> 명령어 설명:
> - `pip`: Python 패키지 설치 도구
> - `install`: "설치해줘"
> - `-r requirements.txt`: "requirements.txt 파일에 적힌 것들을 모두"

설치 진행 상황이 표시되며, 1-3분 정도 소요됩니다.

성공적으로 완료되면 다음과 같은 메시지가 나타납니다:
```
Successfully installed gradio-x.x.x requests-x.x.x ...
```

### 7-4. LM Studio 연결 확인

CodeDojo는 기본적으로 `http://localhost:1234`에서 실행되는 LM Studio와 연결됩니다.

만약 LM Studio가 **다른 포트**를 사용한다면:

1. 프로젝트 폴더에 `.env` 파일 생성:

   **Windows (메모장 사용):**
   ```
   notepad .env
   ```

   **Mac (TextEdit 사용):**
   ```bash
   open -e .env
   ```

2. 다음 내용 입력 (포트 번호를 실제 사용하는 것으로 변경):
   ```
   LM_STUDIO_ENDPOINT=http://localhost:1234/v1/chat/completions
   ```

3. 저장 후 닫기

### 7-5. CodeDojo 실행

모든 준비가 끝났습니다! 이제 CodeDojo를 실행합니다:

**Windows:**
```
python app.py
```

**Mac:**
```bash
python3 app.py
```

정상적으로 실행되면 다음과 같은 메시지가 나타납니다:

```
Running on local URL:  http://127.0.0.1:7860
```

### 7-6. 브라우저에서 접속

1. 웹브라우저 (Chrome, Firefox, Safari 등) 열기
2. 주소창에 `http://127.0.0.1:7860` 입력
3. Enter 키 누르기
4. CodeDojo 화면이 나타남!

> **참고**:
> - `127.0.0.1`은 "내 컴퓨터"를 의미하는 특별한 주소
> - `7860`은 포트 번호 (CodeDojo가 사용하는 문)

---

## 8. CodeDojo 사용하기

### 8-1. 화면 구성

CodeDojo 화면은 크게 다음과 같이 구성되어 있습니다:

```
┌─────────────────────────────────────────┐
│ [문제 유형: SQL ▼] [난이도: Lv3 ▼]      │  ← 문제 선택
│ [문제 출제] 버튼                         │
├─────────────────────────────────────────┤
│                                          │
│ 📝 문제 설명 영역                        │
│   - 문제 내용                            │
│   - 데이터베이스 스키마                  │
│   - 샘플 데이터                          │
│                                          │
├─────────────────────────────────────────┤
│                                          │
│ 💻 코드 에디터                           │
│   (여기에 SQL 또는 PySpark 코드 작성)   │
│                                          │
├─────────────────────────────────────────┤
│ [제출] [문법 힌트] 버튼                  │
├─────────────────────────────────────────┤
│ 📊 결과 및 피드백 영역                   │
│   - 실행 결과                            │
│   - AI 평가                              │
│   - 보완점 및 해설                       │
└─────────────────────────────────────────┘
```

### 8-2. 문제 풀이 순서

**1단계: 문제 선택**
1. **문제 유형** 선택: SQL 또는 PySpark
2. **난이도** 선택: Lv1 (가장 쉬움) ~ Lv5 (가장 어려움)
3. **"문제 출제"** 버튼 클릭

**2단계: 문제 이해**
1. 문제 설명을 천천히 읽기
2. 제공된 **스키마**(데이터베이스 구조) 확인
3. **샘플 데이터** 확인

**3단계: 코드 작성**
1. 코드 에디터에 SQL 또는 PySpark 코드 작성
2. 막히면 **"문법 힌트"** 버튼 클릭 (핵심 문법 표시)

**4단계: 제출 및 피드백**
1. **"제출"** 버튼 클릭
2. AI가 자동으로 평가:
   - ✅ **실행 결과**: 코드 실행 시뮬레이션
   - 📈 **점수**: AI가 채점한 점수
   - 💬 **피드백**: 코드의 장단점 설명
   - 🔍 **보완점**: 개선할 부분 제안
   - 📚 **해설**: 모범 답안 및 개념 설명

**5단계: 오답노트**
- 틀린 문제는 자동으로 `data/wrong_notes.md`에 저장됨
- 나중에 다시 풀어보고 싶으면 해당 파일 확인

### 8-3. 사용 예시

**SQL 예제 - Lv1 난이도:**

문제: "users 테이블에서 모든 사용자의 이름을 조회하세요."

코드 에디터에 입력:
```sql
SELECT name FROM users;
```

제출 후 AI 피드백:
- "기본적인 SELECT 문법을 올바르게 사용했습니다."
- "모든 컬럼을 보려면 SELECT * 를 사용할 수도 있습니다."

**PySpark 예제 - Lv2 난이도:**

문제: "DataFrame에서 age가 30 이상인 사용자만 필터링하세요."

코드 에디터에 입력:
```python
df.filter(df['age'] >= 30)
```

제출 후 AI 피드백:
- "filter() 함수를 올바르게 사용했습니다."
- "결과를 출력하려면 .show()를 추가하세요."

### 8-4. 유용한 팁

💡 **문법을 모르겠을 때**
- "문법 힌트" 버튼 클릭
- 해당 유형의 핵심 문법과 예제 확인

💡 **틀렸을 때**
- AI 피드백을 꼼꼼히 읽기
- 보완점에서 제시한 방향으로 수정
- 다시 제출해보기

💡 **실력 향상**
- Lv1부터 차근차근 시작
- 한 난이도에서 여러 문제 풀어보기
- 오답노트를 주기적으로 복습

---

## 9. 문제 해결

### ❌ Python을 찾을 수 없다는 에러

**증상:**
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결 방법:**

1. **Python이 설치되어 있는지 확인**
   - Windows 시작 메뉴에서 "Python" 검색
   - 없으면 [Python 설치하기](#3-python-설치하기) 다시 진행

2. **PATH 환경 변수 추가** (고급)
   - 시작 → "환경 변수" 검색
   - "시스템 환경 변수 편집" 클릭
   - "환경 변수" 버튼 클릭
   - "Path" 선택 후 "편집" 클릭
   - "새로 만들기" 클릭 후 Python 설치 경로 추가:
     ```
     C:\Users\내사용자명\AppData\Local\Programs\Python\Python3xx
     C:\Users\내사용자명\AppData\Local\Programs\Python\Python3xx\Scripts
     ```
   - 확인 → 명령 프롬프트 재시작

3. **Microsoft Store에서 Python 설치** (Windows 10/11 간편 방법)
   - Microsoft Store 열기
   - "Python 3.12" 검색 및 설치
   - 자동으로 PATH에 추가됨

### ❌ 가상환경 활성화 에러 (PowerShell)

**증상:**
```
이 시스템에서 스크립트를 실행할 수 없으므로 ...
```

**해결 방법:**
1. PowerShell을 **관리자 권한**으로 실행
2. 다음 명령어 입력:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. "Y" 입력 후 Enter
4. PowerShell 닫고 다시 일반 모드로 실행

또는 **CMD 사용**:
- PowerShell 대신 명령 프롬프트(CMD) 사용
- `.venv\Scripts\activate.bat` 실행

### ❌ LM Studio 연결 에러

**증상:**
```
Failed to connect to LM Studio: Connection refused
```

**해결 방법:**

1. **LM Studio 서버가 실행 중인지 확인**
   - LM Studio 앱 열기
   - "Local Server" 클릭
   - "Start Server" 버튼이 "Stop Server"로 표시되어야 함

2. **포트 번호 확인**
   - LM Studio 서버 화면에서 주소 확인 (예: `http://localhost:1234`)
   - CodeDojo 폴더의 `.env` 파일에 올바른 주소 입력

3. **방화벽 확인**
   - Windows Defender 방화벽에서 LM Studio 허용
   - 설정 → 업데이트 및 보안 → Windows 보안 → 방화벽 및 네트워크 보호

### ❌ 포트 7860이 이미 사용 중이라는 에러

**증상:**
```
OSError: [Errno 48] Address already in use
```

**해결 방법:**

1. **다른 CodeDojo가 실행 중인지 확인**
   - 이전에 실행한 터미널/CMD 창이 열려있는지 확인
   - 있다면 `Ctrl + C`로 종료

2. **포트를 사용하는 프로세스 종료**

   **Windows:**
   ```
   netstat -ano | findstr :7860
   taskkill /PID [프로세스번호] /F
   ```

   **Mac:**
   ```bash
   lsof -ti:7860 | xargs kill -9
   ```

3. **다른 포트 사용**
   - `app.py` 실행 시 포트 지정:
     ```bash
     python app.py --port 7861
     ```

### ❌ requirements.txt 설치 에러

**증상:**
```
ERROR: Could not install packages due to an OSError
```

**해결 방법:**

1. **pip 업그레이드**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **관리자 권한으로 실행**
   - Windows: CMD를 관리자 권한으로 실행
   - Mac: `sudo pip install -r requirements.txt`

3. **한 번에 하나씩 설치**
   ```bash
   pip install gradio
   pip install requests
   pip install python-dotenv
   pip install audioop-lts
   pip install setuptools
   ```

### ❌ Mac에서 "확인되지 않은 개발자" 경고

**증상:**
LM Studio 또는 다른 앱 실행 시 보안 경고

**해결 방법:**
1. 시스템 환경설정(System Settings) 열기
2. "보안 및 개인 정보 보호(Privacy & Security)" 클릭
3. 하단에 "확인 없이 열기(Open Anyway)" 버튼 클릭
4. 비밀번호 입력

또는:
1. 앱 아이콘에서 **Control + 클릭** (또는 오른쪽 클릭)
2. "열기(Open)" 선택
3. "열기" 확인

### ❌ Git clone 에러

**증상:**
```
fatal: unable to access 'https://github.com/...': Could not resolve host
```

**해결 방법:**

1. **인터넷 연결 확인**
   - 다른 웹사이트가 열리는지 확인

2. **GitHub 접속 확인**
   - 웹브라우저에서 https://github.com 접속 시도

3. **ZIP 파일로 대체**
   - Git 대신 ZIP 파일 다운로드 방법 사용
   - [CodeDojo 다운로드하기](#6-codedojo-다운로드하기)의 "방법 2" 참조

### 💬 추가 도움이 필요하신가요?

위의 해결 방법으로도 문제가 해결되지 않으면:

1. **GitHub Issues 확인**
   - https://github.com/Abraxaspark91/codedojo/issues
   - 비슷한 문제가 이미 보고되었는지 확인

2. **새로운 Issue 생성**
   - 문제 상황을 자세히 설명
   - 에러 메시지 전체를 복사해서 첨부
   - 운영체제(Windows/Mac) 및 버전 명시

---

## 10. CodeDojo 종료하기

### 10-1. CodeDojo 앱 종료

터미널/CMD에서 `Ctrl + C` 키 누르기

### 10-2. 가상환경 비활성화

```bash
deactivate
```

프롬프트에서 `(.venv)` 표시가 사라지면 성공

### 10-3. LM Studio 종료

LM Studio 앱에서:
1. "Stop Server" 버튼 클릭
2. LM Studio 앱 종료

---

## 11. 다음에 다시 실행할 때

CodeDojo를 다시 사용하려면:

1. **LM Studio 서버 시작**
   - LM Studio 실행 → Local Server → Start Server

2. **터미널/CMD 열기**
   - CodeDojo 폴더로 이동: `cd /path/to/codedojo`

3. **가상환경 활성화**
   - Windows: `.venv\Scripts\activate.bat`
   - Mac: `source .venv/bin/activate`

4. **CodeDojo 실행**
   - Windows: `python app.py`
   - Mac: `python3 app.py`

5. **브라우저 접속**
   - http://127.0.0.1:7860

> **핵심**: 한 번 설치하면 다음부터는 3-4-5 단계만 반복하면 됩니다!

---

## 12. 자주 묻는 질문 (FAQ)

### Q1: Python과 Python3의 차이는?

**A:**
- Windows에서는 대부분 `python` 명령어 사용
- Mac/Linux에서는 대부분 `python3` 명령어 사용
- 둘 다 같은 의미이지만 운영체제에 따라 다름

### Q2: 가상환경을 꼭 사용해야 하나요?

**A:**
- 필수는 아니지만 **강력히 권장**
- 가상환경 없이 설치하면:
  - 다른 프로젝트와 충돌 가능
  - 컴퓨터 전체에 영향을 미침
  - 나중에 삭제하기 어려움

### Q3: LM Studio 대신 다른 AI를 사용할 수 있나요?

**A:**
- 현재 버전은 LM Studio 전용입니다
- 향후 버전에서 OpenAI API, Anthropic Claude 등을 지원할 예정

### Q4: 인터넷 없이 사용할 수 있나요?

**A:**
- 설치 후에는 **인터넷 없이 사용 가능**
- LM Studio가 로컬에서 실행되기 때문
- 단, 초기 설치 시에는 인터넷 필요

### Q5: 여러 대의 컴퓨터에서 사용하려면?

**A:**
- 각 컴퓨터마다 이 가이드를 따라 설치
- 또는 USB에 설치해서 가지고 다닐 수도 있음 (고급)

### Q6: CodeDojo가 느린데 어떻게 하나요?

**A:**
- **LM Studio 모델이 클 경우**: 더 작은 모델 사용 (예: Phi-3-mini)
- **RAM 부족**: 다른 프로그램 종료
- **오래된 컴퓨터**: 최소 8GB RAM 권장

### Q7: 문제를 더 추가하고 싶어요

**A:**
- `data/problems.json` 파일을 수정
- JSON 형식에 맞춰 새로운 문제 추가
- 자세한 방법은 향후 "고급 가이드"에서 설명 예정

---

## 13. 다음 단계

CodeDojo를 설치하고 사용하는 방법을 익혔다면:

✅ **초급**
- 다양한 난이도의 문제를 풀어보기
- 오답노트를 주기적으로 복습하기

✅ **중급**
- SQL 문법 체계적으로 공부하기
- PySpark 기초 학습하기
- 자신만의 문제 추가해보기

✅ **고급**
- CodeDojo 코드 수정해보기
- 새로운 기능 추가하기 (예: 데이터베이스 연동)
- 다른 사람들과 문제 공유하기

---

## 📝 마치며

축하합니다! 🎉

이 가이드를 따라 CodeDojo를 성공적으로 설치하고 실행하셨다면, 이제 당신은:
- 터미널/CMD를 사용할 수 있고
- Python 가상환경을 만들고 관리할 수 있으며
- Git으로 프로젝트를 다운로드할 수 있고
- AI를 로컬에서 실행할 수 있습니다

이것들은 모두 프로그래밍을 배우는 데 필수적인 기술입니다. 처음엔 어렵고 복잡해 보이지만, 몇 번 반복하다 보면 자연스럽게 익숙해질 것입니다.

**CodeDojo와 함께 즐거운 코딩 공부 되세요!** 💻✨

---

**문서 버전**: 1.0.0
**최종 수정일**: 2025-12-08
**작성자**: CodeDojo Team
**라이선스**: MIT License
