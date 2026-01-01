import json
import os
import random
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from dotenv import load_dotenv
import gradio as gr
import requests
import problem_bank
from problem_bank import (
    DIFFICULTY_OPTIONS,
    PROBLEM_BANK,
    Problem,
    unique_preserve_order,
    get_available_problem_files,
    reload_problem_bank,
    DEFAULT_PROBLEM_FILE,
)

NOTE_PATH = Path("data/wrong_notes.md")
NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
FAVORITES_PATH = Path("data/favorites.json")
FAVORITES_PATH.parent.mkdir(parents=True, exist_ok=True)

# .env 파일에서 환경변수 로드
load_dotenv()
LM_STUDIO_ENDPOINT = os.getenv("LM_STUDIO_ENDPOINT", "http://127.0.0.1:1234/v1/chat/completions")

CUSTOM_THEME = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
).set(
    body_background_fill="*neutral_50",
    body_background_fill_dark="*neutral_950",
)

CUSTOM_CSS = """
/* ===== 영역 구분 스타일 ===== */
.section-box {
    padding: 1.5rem;
    border-radius: 0.75rem;
    border: 1px solid var(--border-color-primary);
    background: var(--background-fill-secondary);
    margin-bottom: 1rem;
}

.problem-box {
    min-height: 200px;
    max-height: 500px;
    overflow-y: auto;
}

.feedback-box {
    min-height: 250px;
    max-height: 350px;
    overflow-y: auto;
}

.code-editor-box {
    min-height: 200px;
}

/* GitHub Dark Dimmed 배경 */
.code-editor-box .cm-editor,
.code-editor-box .cm-scroller,
.code-editor-box .cm-gutters {
    background-color: #2d333b !important;
    color: #adbac7 !important;
}

/* 기본 텍스트 */
.code-editor-box .cm-content {
    color: #adbac7 !important;
}

/* 줄 번호 */
.code-editor-box .cm-gutters {
    color: #768390 !important;
}

/* 커서 */
.code-editor-box .cm-cursor {
    border-left: 1px solid #f0f3f6 !important;
}

/* 선택 활성 라인 */
.code-editor-box .cm-activeLine {
    background-color: #39424e !important;
}

/* ===== Syntax Highlighting ===== */

/* 키워드 - 보라 */
.code-editor-box .cm-keyword {
    color: #dcbdfb !important;
}

/* 문자열 - 파스텔 블루 */
.code-editor-box .cm-string {
    color: #96d0ff !important;
}

/* 숫자/상수 - 따뜻 노랑 */
.code-editor-box .cm-number {
    color: #f9c97f !important;
}

/* 함수/메서드 이름 - 녹색 */
.code-editor-box .cm-variable,
.code-editor-box .cm-property {
    color: #8ddb8c !important;
}

/* 코멘트 - 푸른 회색 */
.code-editor-box .cm-comment {
    color: #6c7986 !important;
}


/* ===== 버튼 그룹 ===== */
.button-row {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
}

/* ===== 하단 섹션 ===== */
.bottom-panel {
    padding: 1rem;
    border-radius: 0.75rem;
    border: 1px solid var(--border-color-primary);
    background: var(--background-fill-secondary);
}

/* ===== 상태 메시지 ===== */
.status-message {
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

/* ===== 스크롤바 커스터마이징 ===== */
.problem-box::-webkit-scrollbar,
.feedback-box::-webkit-scrollbar {
    width: 6px;
}

.problem-box::-webkit-scrollbar-track,
.feedback-box::-webkit-scrollbar-track {
    background: transparent;
}

.problem-box::-webkit-scrollbar-thumb,
.feedback-box::-webkit-scrollbar-thumb {
    background: var(--border-color-primary);
    border-radius: 3px;
}

.problem-box::-webkit-scrollbar-thumb:hover,
.feedback-box::-webkit-scrollbar-thumb:hover {
    background: var(--color-accent);
}

/* ===== 모바일 반응형 ===== */
@media (max-width: 768px) {
    .section-box {
        padding: 1rem;
    }

    .problem-box,
    .feedback-box,
    .code-editor-box {
        min-height: 250px;
    }
}
"""


@dataclass
class Attempt:
    """오답노트에 저장되는 단일 채점 시도 레코드입니다.

    Attributes:
        pid: 문제 ID (problem_bank에서의 고유 식별자)
        title: 문제 제목
        difficulty: 난이도 (Lv1 입문 등)
        score: 채점 점수 (0-100)
        status: 상태 (통과/재도전)
        submitted: 제출된 코드
        feedback: LLM 피드백
        improvement: 보완 포인트
        reasoning: 해설/의도 추측
        question: 문제 내용
        code: 제출 코드
        kind: 프로그래밍 언어 (sql/python, Gradio Code 컴포넌트 지원 언어)
        timestamp: 제출 시간 (형식: "YYYY-MM-DD HH:MM (요일)")
        rechallenge_hint: 재도전 시 참고할 힌트
        nickname: 문제 별명 (사용자 지정)
        source_file: 문제 출처 파일 (예: "problems.json")
    """
    pid: str
    title: str
    difficulty: str
    score: int
    status: str
    submitted: str
    feedback: str
    improvement: str
    reasoning: str
    question: str
    code: str
    kind: str
    timestamp: str
    rechallenge_hint: str = ""
    nickname: str = ""
    source_file: str = "problems.json"  # 하위 호환성을 위한 기본값


def ensure_state(state: Optional[Dict]) -> Dict:
    if state is None:
        state = {}

    state.setdefault("in_progress", False)
    state.setdefault("last_feedback", "")
    state.setdefault("filters", normalize_filters(None, None, None))
    state.setdefault("hint_visible", False)
    return state



def ensure_note_file() -> None:
    """오답노트 파일을 초기화합니다.

    JSON Lines 형식: 각 라인이 독립적인 JSON 객체
    """
    if not NOTE_PATH.exists():
        NOTE_PATH.write_text("")  # 빈 파일로 시작 (헤더 없음)


def serialize_attempt(attempt: Attempt) -> str:
    """Attempt를 JSON Lines 형식으로 직렬화합니다.

    각 Attempt는 한 줄의 JSON으로 저장되어 강건한 파싱이 가능합니다.
    - 멀티라인 텍스트는 JSON이 자동으로 이스케이프
    - 마크다운 syntax 충돌 없음
    - 손상된 한 줄만 무시, 나머지는 안전
    """
    meta = json.dumps(
        asdict(attempt),
        ensure_ascii=False,  # 한글 유지
        separators=(',', ':')  # 공백 제거해서 한 줄 유지
    )

    # JSON이 유효한지 검증
    try:
        json.loads(meta)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 직렬화 오류: {e}\n{meta[:200]}...")

    return meta  # 순수 JSON 한 줄만 반환


def safe_read_file(path: Path) -> str:
    """다중 인코딩 시도로 안전하게 파일 읽기

    Args:
        path: 읽을 파일 경로

    Returns:
        str: 파일 내용 (UTF-8 BOM 제거됨)
    """
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']

    for encoding in encodings:
        try:
            text = path.read_text(encoding=encoding, errors='ignore')
            # UTF-8 BOM 제거 (utf-8-sig가 실패한 경우 대비)
            if text.startswith('\ufeff'):
                text = text[1:]
            return text
        except Exception:
            continue

    # 최후의 수단: 바이너리 읽기 후 디코드
    return path.read_bytes().decode('utf-8', errors='replace')


def sanitize_line(line: str) -> str:
    """JSON 파싱 전 라인 정제

    Args:
        line: 정제할 라인

    Returns:
        str: 정제된 라인
    """
    import unicodedata

    # 제어 문자 제거 (탭/개행 제외)
    line = ''.join(c for c in line if c >= ' ' or c in '\t\n')

    # NULL 바이트 제거
    line = line.replace('\x00', '')

    # 유니코드 정규화 (NFKC)
    line = unicodedata.normalize('NFKC', line)

    # 양쪽 공백 제거
    return line.strip()


def is_likely_json(line: str) -> bool:
    """라인이 JSON 객체일 가능성이 있는지 빠르게 체크

    Args:
        line: 체크할 라인

    Returns:
        bool: JSON 객체일 가능성이 있으면 True
    """
    line = line.strip()
    # JSON 객체는 { 로 시작하고 } 로 끝남
    return line.startswith('{') and line.endswith('}')


def robust_json_parse(line: str) -> Optional[Dict]:
    """여러 방법으로 JSON 파싱 시도

    Args:
        line: 파싱할 JSON 라인

    Returns:
        Optional[Dict]: 파싱된 딕셔너리 또는 None
    """
    # 1차: 기본 파싱
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        pass

    # 2차: 손상된 이스케이프 시퀀스 복구
    try:
        # 백슬래시가 과도하게 이스케이프된 경우
        fixed = line.replace('\\\\', '\\')
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    # 3차: 중괄호 매칭으로 JSON 추출
    try:
        start = line.find('{')
        end = line.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(line[start:end])
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def log_parse_error(line_idx: int, line: str, error: Exception) -> None:
    """파싱 실패 시 상세 정보 출력

    Args:
        line_idx: 라인 번호
        line: 실패한 라인 내용
        error: 발생한 예외
    """
    import sys

    # 라인 미리보기 (첫 100자)
    preview = line[:100] + ('...' if len(line) > 100 else '')

    # 에러 메시지
    error_msg = str(error)[:80]

    print(
        f"[경고] 라인 {line_idx} 파싱 실패\n"
        f"  오류: {error_msg}\n"
        f"  내용: {repr(preview)}",
        file=sys.stderr
    )


def load_attempts() -> List[Attempt]:
    """오답노트 파일에서 모든 Attempt를 로드합니다.

    JSON Lines 형식: 각 라인이 하나의 JSON 객체
    - 손상된 라인은 무시하고 나머지 계속 파싱
    - 라인 단위 오류 로깅으로 문제 진단 용이
    - 다중 인코딩 지원, 제어 문자 제거, 다단계 파싱 시도
    """
    ensure_note_file()

    # 강건한 파일 읽기 (다중 인코딩, BOM 처리)
    text = safe_read_file(NOTE_PATH)
    entries: List[Attempt] = []

    # 빈 파일 처리
    if not text.strip():
        return entries

    # 각 라인을 독립적으로 파싱
    for line_idx, line in enumerate(text.split("\n"), 1):
        # 라인 정제 (제어 문자, NULL 바이트 제거)
        line = sanitize_line(line)

        # 빈 라인 무시
        if not line:
            continue

        # JSON이 아닌 라인 건너뛰기 (마크다운 헤더, 주석 등)
        if not is_likely_json(line):
            continue

        try:
            # 강건한 JSON 파싱 (다단계 재시도)
            data = robust_json_parse(line)

            if data is None:
                # 모든 파싱 방법 실패
                log_parse_error(line_idx, line, ValueError("JSON 파싱 불가"))
                continue

            # 하위 호환성: source_file 필드가 없으면 기본값 추가
            if "source_file" not in data:
                data["source_file"] = DEFAULT_PROBLEM_FILE

            # Attempt 객체 생성
            entry = Attempt(**data)
            entries.append(entry)

        except TypeError as e:
            # Attempt 필드 부족: 해당 라인 무시, 계속 진행
            log_parse_error(line_idx, line, e)
            continue

        except Exception as e:
            # 예상 외의 오류
            log_parse_error(line_idx, line, e)
            continue

    return entries


def failed_attempts(entries: List[Attempt]) -> List[Attempt]:
    return [a for a in entries if a.score < 80]


def matches_filters(
        problem: Problem,
        difficulty: Optional[str],
        language: Optional[str],
        problem_types: Optional[List[str]]) -> bool:
    """
    문제가 필터 조건과 일치하는지 확인합니다.

    language 필터 동작:
    - "전체": 모든 문제 포함
    - "Python": Python 관련 모두 포함
    - "Python.Pyspark": Python.Pyspark만 포함
    - "Python.Pandas": Python.Pandas만 포함
    - "Python.NumPy": Python.NumPy만 포함
    - "SQL": SQL만 포함
    """
    # 언어 필터 매칭
    if not language or language == "전체":
        language_match = True
    elif '.' not in language:
        # "Python"이나 "SQL"처럼 base language만 선택한 경우
        # problem.language는 kind의 '.' 앞부분만 반환
        language_match = problem.language.lower() == language.lower()
    else:
        # "Python.Pyspark"처럼 구체적인 라이브러리까지 선택한 경우
        language_match = problem.kind.lower() == language.lower()

    difficulty_match = (not difficulty or difficulty ==
                        "전체") or problem.difficulty == difficulty
    # problem_types가 리스트로 전달됨 (체크박스 선택값)
    type_match = (not problem_types or len(problem_types) == 0) or problem.problem_type in problem_types
    return difficulty_match and language_match and type_match


def normalize_filters(
    difficulty: Optional[str], language: Optional[str], problem_types: Optional[List[str]]
) -> Dict:
    """필터를 정규화합니다. problem_types는 리스트입니다."""
    return {
        "difficulty": difficulty or "전체",
        "language": language or "전체",
        "problem_types": problem_types if problem_types else [],
    }


def pick_problem(
    difficulty: str, language: str, problem_types: List[str]
) -> Tuple[Problem | None, bool, str, Dict]:
    """체크박스로 선택된 problem_types 중에서 문제를 선택합니다. 엄격한 필터링으로 매칭 실패 시 None을 반환합니다."""
    rechallenge = False
    hint = ""
    target_filters = normalize_filters(difficulty, language, problem_types)

    # 엄격한 필터링: 요청한 조건에 정확히 맞는 문제만 선택
    full_pool = [(p, "") for p in problem_bank.PROBLEM_BANK]
    candidates = [
        (prob, attempt_hint)
        for prob, attempt_hint in full_pool
        if matches_filters(prob, difficulty, language, problem_types)
    ]

    if not candidates:
        # 매칭되는 문제가 없으면 None 반환
        return None, rechallenge, hint, target_filters

    prob, attempt_hint = random.choice(candidates)
    return prob, rechallenge, hint, target_filters


def render_question(
    problem: Problem,
    rechallenge: bool,
    rechallenge_hint: str,
    requested_filters: Dict[str, str],
    applied_filters: Optional[Dict[str, str]] = None,
) -> str:
    """문제를 마크다운 형식으로 렌더링합니다."""
    banner = "재도전" if rechallenge else "신규 문제"
    hint_line = f"\n> 🔁 재도전 힌트: {rechallenge_hint}\n" if rechallenge_hint else ""

    # 기본 정보
    # 라이브러리 정보가 있으면 함께 표시
    library_info = f" ({problem.library})" if problem.library else ""
    result = (
        f"### [{banner}] {problem.title}\n"
        f"- 난이도: {problem.difficulty}\n"
        f"- 유형: {problem.language}{library_info}\n"
        f"{hint_line}\n"
        f"---\n\n"
        f"**📝 문제**\n\n"
        f"{problem.body}\n\n"
    )

    # 스키마 추가 (있을 경우)
    if problem.schema:
        result += f"**📊 스키마**\n```\n{problem.schema}\n```\n\n"

    # 샘플 데이터 추가 (있을 경우)
    if problem.sample_rows:
        result += "**📋 샘플 데이터**\n```\n"
        for row in problem.sample_rows:
            result += f"{row}\n"
        result += "```\n"

    return result


def ensure_favorites_file() -> None:
    if not FAVORITES_PATH.exists():
        FAVORITES_PATH.write_text("[]", encoding="utf-8")


def load_favorites() -> List[Dict]:
    ensure_favorites_file()
    try:
        data = json.loads(FAVORITES_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return []


def save_favorites(favorites: List[Dict]) -> None:
    """즐겨찾기를 저장합니다. source_file + pid 조합으로 중복 제거."""
    deduped = {}
    for fav in favorites:
        pid = fav.get("pid")
        source_file = fav.get("source_file", DEFAULT_PROBLEM_FILE)
        if pid:
            # source_file + pid 조합을 키로 사용하여 중복 제거
            key = f"{source_file}:{pid}"
            deduped[key] = {
                "pid": pid,
                "source_file": source_file,
                "title": fav.get("title", ""),
                "difficulty": fav.get("difficulty", ""),
                "kind": fav.get("kind", ""),
                "timestamp": fav.get("timestamp", format_timestamp_with_weekday()),
            }
    FAVORITES_PATH.write_text(
        json.dumps(
            list(
                deduped.values()),
            ensure_ascii=False,
            indent=2),
        encoding="utf-8")


def favorite_button_label(pid: str, source_file: str = DEFAULT_PROBLEM_FILE) -> str:
    """즐겨찾기 버튼 레이블을 반환합니다. source_file + pid로 확인."""
    favorites = load_favorites()
    is_favorite = any(
        fav.get("pid") == pid and fav.get("source_file", DEFAULT_PROBLEM_FILE) == source_file
        for fav in favorites
    )
    return "⭐ 즐겨찾기 해제" if is_favorite else "☆ 즐겨찾기 추가"


def _format_dropdown_choices(
    items: List[Any],
    label_fn: Callable[[Any], str],
    value_fn: Callable[[Any], str]
) -> Tuple[List[str], List[str]]:
    """드롭다운 선택지를 생성하는 헬퍼 함수.

    Args:
        items: 데이터 항목 리스트
        label_fn: 각 항목을 레이블 문자열로 변환하는 함수
        value_fn: 각 항목에서 값을 추출하는 함수

    Returns:
        Tuple[List[str], List[str]]: (labels, values)
    """
    labels = [label_fn(item) for item in items]
    values = [value_fn(item) for item in items]
    return labels, values


def refresh_favorite_choices() -> Tuple[List[str], List[str]]:
    """즐겨찾기 드롭다운 선택지를 반환합니다. 값은 'source_file:pid' 형식입니다."""
    favorites = load_favorites()
    return _format_dropdown_choices(
        favorites,
        lambda fav: f"{fav.get('title', '')} | {fav.get('source_file', DEFAULT_PROBLEM_FILE)} | {fav.get('difficulty', '')} | {fav.get('kind', '')}",
        lambda fav: f"{fav.get('source_file', DEFAULT_PROBLEM_FILE)}:{fav['pid']}"
    )


def call_llm(system_prompt: str, user_prompt: str,
             endpoint: str = LM_STUDIO_ENDPOINT) -> str:
    payload = {
        "model": "lm-studio",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "temperature": 0.2,
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=180)
        response.raise_for_status()
        content = response.json()
        result = content["choices"][0]["message"]["content"]

        # 일부 모델이 생성하는 <think>...</think> 태그 제거
        # (Gradio Markdown 렌더링 방해 방지)
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
        result = result.strip()

        return result
    except (requests.RequestException, KeyError, ValueError, IndexError) as exc:
        return (
            "LLM 서버에 연결하지 못했습니다.\n"
            f"로컬 엔드포인트({endpoint})를 확인하세요.\n"
            f"네트워크를 확인하거나 나중에 다시 시도하세요. ({exc})"
        )




def build_feedback(
    problem: Problem, code: str, endpoint: str
) -> str:
    """LLM을 사용하여 코드에 대한 피드백을 생성합니다."""
    system_prompt = (
        "당신은 SQL, Python, Pseudocode, Technical Decomp문제의 채점을 돕는 조교입니다. "
        "제출된 코드를 분석하여 피드백을 제공하세요. "
        "정답 여부, 놓친 부분, 작성자의 의도 추정 및 약점분석, 효율/논리 개선안을 포함합니다.")
    user_prompt = (
        f"문제: {problem.body}\n"
        f"스키마: {problem.schema}\n"
        f"코드:```{code}\n```\n"
        "다음 사항을 포함하여 피드백을 제공하세요:\n"
        "- 1) 코드 분석 및 평가\n"
        "- 2) 보완이 필요한 부분\n"
        "- 3) 작성자의 의도 추측 및 약점분석\n"
        "- 4) 더 효율적이거나 간결한 방법")
    llm_reply = call_llm(system_prompt, user_prompt, endpoint)
    return llm_reply


# append_attempt function removed - manual note saving implemented below


def generate_hint_summary(problem: Problem, code: str, feedback: str, endpoint: str) -> str:
    """LLM을 사용하여 틀린 이유를 50자 이내로 요약합니다."""
    system_prompt = (
        "당신은 학습 도우미입니다. 학생이 문제를 틀린 이유를 50자 이내로 간결하게 요약하세요."
    )
    user_prompt = (
        f"문제: {problem.body}\n"
        f"제출 코드: {code}\n"
        f"피드백: {feedback}\n\n"
        "위 내용을 바탕으로 이 문제를 틀린 핵심 이유를 50자 이내로 요약하세요."
    )
    summary = call_llm(system_prompt, user_prompt, endpoint)
    # 50자로 자르기
    return summary[:50] if len(summary) > 50 else summary


def format_timestamp_with_weekday() -> str:
    """현재 시간을 'YYYY-MM-DD HH:MM (요일)' 형식으로 반환합니다."""
    now = datetime.now()
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday = weekdays[now.weekday()]
    return now.strftime(f"%Y-%m-%d %H:%M ({weekday})")


def save_to_wrong_notes(
    problem: Problem,
    code: str,
    feedback: str,
    nickname: str,
    rechallenge_hint: str,
    source_file: str = DEFAULT_PROBLEM_FILE
) -> str:
    """수동으로 오답노트에 저장합니다."""
    ensure_note_file()

    # Attempt 객체 생성 (수동 저장이므로 score는 0, status는 "재도전")
    attempt = Attempt(
        pid=problem.pid,
        title=problem.title,
        difficulty=problem.difficulty,
        score=0,  # 수동 저장이므로 점수 없음
        status="재도전",
        submitted=code,
        feedback=feedback,
        improvement="수동으로 오답노트에 추가됨",
        reasoning="수동 추가",
        question=problem.body,
        code=code,
        kind=problem.kind,
        timestamp=format_timestamp_with_weekday(),
        rechallenge_hint=rechallenge_hint,
        nickname=nickname,
        source_file=source_file,
    )

    try:
        serialized = serialize_attempt(attempt)
        # JSON Lines: append 모드로 새 라인 추가
        # 파일이 비어있지 않으면 앞에 개행 추가 (안전하게 줄바꿈 보장)
        prefix = '\n' if NOTE_PATH.exists() and NOTE_PATH.stat().st_size > 0 else ''
        with open(NOTE_PATH, 'a', encoding='utf-8') as f:
            f.write(f'{prefix}{serialized}\n')
        return f"✅ 오답노트에 추가되었습니다! ({format_timestamp_with_weekday()})"
    except ValueError as e:
        print(f"[오류] Attempt 저장 실패: {e}", file=__import__('sys').stderr)
        return f"❌ 저장 실패: {str(e)}"


def refresh_note_choices() -> Tuple[List[str], List[str]]:
    entries = failed_attempts(load_attempts())
    return _format_dropdown_choices(
        entries,
        lambda a: f"{a.title} | {a.nickname if a.nickname else '-'} | {a.difficulty} | {a.kind} | {a.timestamp}",
        lambda a: a.pid
    )


def refresh_note_pid_choices() -> Tuple[List[str], List[str]]:
    """고유한 source_file + PID 목록을 반환합니다 (중복 제거).

    Returns:
        Tuple[List[str], List[str]]: (labels, values)
            - labels: "title | source_file | difficulty | kind" 형식
            - values: "source_file:pid" 문자열
    """
    entries = failed_attempts(load_attempts())
    # source_file + pid 조합별로 첫 번째 항목만 유지 (중복 제거)
    seen_keys = set()
    unique_entries = []
    for a in entries:
        key = f"{a.source_file}:{a.pid}"
        if key not in seen_keys:
            seen_keys.add(key)
            unique_entries.append(a)

    return _format_dropdown_choices(
        unique_entries,
        lambda a: f"{a.title} | {a.source_file} | {a.difficulty} | {a.kind}",
        lambda a: f"{a.source_file}:{a.pid}"
    )


def refresh_note_attempt_choices(selected_key: str) -> Tuple[List[str], List[str]]:
    """특정 source_file + PID의 모든 시도 목록을 반환합니다.

    Args:
        selected_key: 선택된 키 ("source_file:pid" 형식)

    Returns:
        Tuple[List[str], List[str]]: (labels, values)
            - labels: "nickname | timestamp" 형식
            - values: "source_file:pid:nickname:timestamp" 복합 키
    """
    if not selected_key:
        return [], []

    # source_file:pid 파싱
    parts = selected_key.split(":", 1)
    if len(parts) == 2:
        source_file, pid = parts
    else:
        source_file, pid = DEFAULT_PROBLEM_FILE, selected_key

    entries = failed_attempts(load_attempts())
    pid_entries = [a for a in entries if a.pid == pid and a.source_file == source_file]

    return _format_dropdown_choices(
        pid_entries,
        lambda a: f"{a.nickname if a.nickname else '(별명없음)'} | {a.timestamp}",
        lambda a: f"{a.source_file}:{a.pid}:{a.nickname}:{a.timestamp}"
    )


def load_from_notes(
        selected_key: str) -> Tuple[str, Dict, gr.update, str, str]:
    """오답노트에서 문제를 로드합니다.

    Args:
        selected_key: 복합 키 (source_file:pid:nickname:timestamp)

    Returns:
        Tuple[str, Dict, gr.update, str, str]: (question, state, code_update, fav_button, status)
    """
    if not selected_key:
        return "문제를 선택하세요.", {}, gr.update(), "☆ 즐겨찾기 추가", ""

    entries = failed_attempts(load_attempts())

    # 복합 키 파싱: source_file:pid:nickname:timestamp
    # maxsplit=3으로 timestamp에 ":"가 있어도 처리
    parts = selected_key.split(":", 3)

    if len(parts) == 4:
        source_file, pid, nickname, timestamp = parts
    elif len(parts) == 3:
        # 하위 호환성: pid:nickname:timestamp (source_file 없음)
        source_file = DEFAULT_PROBLEM_FILE
        pid, nickname, timestamp = parts
    else:
        return "선택한 문제가 없습니다.", {}, gr.update(), "☆ 즐겨찾기 추가", ""

    # 해당 source_file로 PROBLEM_BANK 재로드
    reload_problem_bank(source_file)

    # 모든 조건으로 정확히 매칭
    for entry in entries:
        if (entry.pid == pid and
            entry.nickname == nickname and
            entry.timestamp == timestamp and
            entry.source_file == source_file):
            problem = next(
                (p for p in problem_bank.PROBLEM_BANK if p.pid == entry.pid), None)
            if problem:
                filters = normalize_filters(None, None, None)
                question = render_question(
                    problem, True, entry.rechallenge_hint, filters)
                return (
                    question,
                    {
                        "problem": problem,
                        "rechallenge": True,
                        "hint": entry.rechallenge_hint,
                        "filters": filters,
                        "in_progress": False,
                        "source_file": source_file,  # source_file 저장
                    },
                    gr.update(value="", language=problem.safe_language),
                    favorite_button_label(problem.pid, source_file),
                    "",
                )

    return "선택한 문제가 없습니다.", {}, gr.update(), "☆ 즐겨찾기 추가", ""


def load_favorite_problem(pid: str, source_file: str = DEFAULT_PROBLEM_FILE) -> Tuple[str, Dict, gr.update, str, str, gr.update]:
    """즐겨찾기에서 문제를 로드합니다. source_file에서 PROBLEM_BANK를 재로드합니다."""
    # 해당 소스 파일로 PROBLEM_BANK 재로드
    reload_problem_bank(source_file)

    problem = next((p for p in problem_bank.PROBLEM_BANK if p.pid == pid), None)
    if problem:
        filters = normalize_filters(None, None, None)
        question = render_question(problem, False, "", filters)
        state = ensure_state({
            "problem": problem,
            "rechallenge": False,
            "hint": "",
            "filters": filters,
            "in_progress": False,
            "source_file": source_file,  # source_file 저장
        })
        return (
            question,
            state,
            gr.update(value="", language=problem.safe_language),
            favorite_button_label(problem.pid, source_file),
            "",
            gr.update(value="💡 힌트 보기"),
        )
    return "선택한 즐겨찾기 문제가 없습니다.", {}, gr.update(), "☆ 즐겨찾기 추가", "", gr.update(value="💡 힌트 보기")


def on_new_problem(problem_file: str,
                   difficulty: str,
                   language: str,
                   problem_types: List[str]) -> Tuple[str,
                                                      Dict,
                                                      gr.update,
                                                      str,
                                                      str,
                                                      gr.update,
                                                      gr.update,
                                                      str,
                                                      str]:
    """새 문제를 출제합니다. problem_types는 체크박스로 선택된 리스트입니다."""
    # 선택된 문제 파일로 PROBLEM_BANK 재로드 (필요시)
    reload_problem_bank(problem_file)

    filters = normalize_filters(difficulty, language, problem_types)
    problem, rechallenge, hint, applied_filters = pick_problem(
        difficulty, language, problem_types)

    # 엄격한 필터링으로 매칭되는 문제가 없는 경우
    if problem is None:
        # 필터 조건을 명확히 표시
        filter_desc = []
        if difficulty and difficulty != "전체":
            filter_desc.append(f"난이도: {difficulty}")
        if language and language != "전체":
            filter_desc.append(f"유형: {language}")
        if problem_types:
            filter_desc.append(f"문제 형태: {', '.join(problem_types)}")

        filter_msg = " / ".join(filter_desc) if filter_desc else "선택한 조건"
        error_msg = f"⚠️ 해당하는 문제가 없습니다\n\n**{filter_msg}**에 맞는 문제가 `{problem_file}`에 존재하지 않습니다.\n\n다른 조건을 선택해주세요."

        # Gradio Error를 raise하여 사용자에게 오류 메시지 표시
        raise gr.Error(error_msg)

    question = render_question(
        problem,
        rechallenge,
        hint,
        filters,
        applied_filters)
    state = ensure_state({})
    state.update(
        {
            "problem": problem,
            "rechallenge": rechallenge,
            "hint": hint,
            "filters": filters,
            "in_progress": False,
            "last_feedback": "",
            "source_file": problem_file,  # 현재 문제 파일 저장
        }
    )
    # 오답노트 목록 자동 업데이트 (PID 드롭다운만)
    pid_labels, pid_values = refresh_note_pid_choices()
    pid_choices = list(zip(pid_labels, pid_values)) if pid_labels else []

    return (
        question,
        state,
        gr.update(value="", language=problem.safe_language),
        favorite_button_label(problem.pid, problem_file),
        "",  # exec_result 초기화
        gr.update(choices=pid_choices, value=None),  # note_pid_dropdown 업데이트
        gr.update(value="💡 힌트 보기"),  # hint_btn 초기화
        "",  # add_notes_status 초기화
        "",  # nickname_input 초기화
    )


def on_submit(state: Dict, code: str, progress=gr.Progress()
              ) -> Tuple[str, gr.update, gr.update]:
    """코드를 제출하고 LLM 피드백을 받습니다. (자동 저장 없음)"""
    state = ensure_state(state)
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다.", gr.update(), gr.update(value="💡 힌트 보기")

    if state.get("in_progress"):
        return "피드백 생성이 진행 중입니다. 잠시만 기다려주세요.", gr.update(), gr.update()

    state["in_progress"] = True
    problem: Problem = state["problem"]

    progress(0.5, desc="LLM 피드백 생성 중")
    feedback = build_feedback(problem, code, LM_STUDIO_ENDPOINT)

    # 힌트 자동 숨김
    state.update({
        "in_progress": False,
        "last_feedback": feedback,
        "last_code": code,
        "hint_visible": False
    })

    # LLM 피드백만 반환
    result = f"### 💬 LLM 피드백\n{feedback}"

    return result, gr.update(), gr.update(value="💡 힌트 보기")


def toggle_hint(state: Dict) -> Tuple[str, gr.update, Dict]:
    """힌트 표시/숨김을 토글합니다."""
    state = ensure_state(state)

    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다.", gr.update(value="💡 힌트 보기"), state

    # 힌트 표시 상태 토글
    state["hint_visible"] = not state.get("hint_visible", False)

    problem: Problem = state["problem"]

    # LLM 응답이 있는지 확인
    llm_feedback = state.get("last_feedback", "")

    if state["hint_visible"]:
        # 힌트 표시
        hint_text = f"### 💡 문법 힌트\n{problem.hint}"
        button_label = "💡 힌트 숨기기"

        # LLM 응답이 있으면 함께 표시 (LLM 응답 유지 + 힌트 추가)
        if llm_feedback:
            result = f"### 💬 LLM 피드백\n{llm_feedback}\n\n{hint_text}"
        else:
            result = hint_text
    else:
        # 힌트 숨김
        button_label = "💡 힌트 보기"

        # LLM 응답이 있으면 유지
        if llm_feedback:
            result = f"### 💬 LLM 피드백\n{llm_feedback}"
        else:
            result = ""

    return result, gr.update(value=button_label), state


def toggle_favorite(state: Dict) -> Tuple[gr.update, str, gr.update]:
    if not state or "problem" not in state:
        labels, values = refresh_favorite_choices()
        return gr.update(), "문제가 선택되지 않았습니다.", gr.update(
            choices=list(zip(labels, values)), value=None)

    problem: Problem = state["problem"]
    source_file = state.get("source_file", DEFAULT_PROBLEM_FILE)
    favorites = load_favorites()

    # source_file + pid 조합으로 존재 여부 확인
    exists = any(
        fav.get("pid") == problem.pid and fav.get("source_file", DEFAULT_PROBLEM_FILE) == source_file
        for fav in favorites
    )

    if exists:
        # source_file + pid 조합으로 제거
        favorites = [
            fav for fav in favorites
            if not (fav.get("pid") == problem.pid and fav.get("source_file", DEFAULT_PROBLEM_FILE) == source_file)
        ]
        message = "즐겨찾기에서 제거했습니다."
        new_value = None
    else:
        favorites.append(
            {
                "pid": problem.pid,
                "source_file": source_file,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "kind": problem.kind,
            }
        )
        message = "즐겨찾기에 추가했습니다."
        new_value = problem.pid

    save_favorites(favorites)
    labels, values = refresh_favorite_choices()
    return (
        gr.update(value=favorite_button_label(problem.pid, source_file)),
        message,
        gr.update(choices=list(zip(labels, values)), value=new_value),
    )


def build_interface() -> gr.Blocks:
    # 사용 가능한 문제 파일 목록
    available_problem_files = get_available_problem_files()

    # kind 값을 정렬하여 계층적으로 표시
    # 결과: ["전체", "Python", "Python.Pyspark", "SQL"]
    language_options = ["전체"] + \
        sorted(unique_preserve_order([p.kind for p in problem_bank.PROBLEM_BANK]))
    # 문제 유형 옵션 (체크박스용)
    problem_type_options = ["코딩", "개념문제", "빈칸채우기"]

    demo = gr.Blocks(
        title="SQL & Python 코딩 연습"
    )

    with demo:
        # 탭별 독립적인 state 생성
        new_state = gr.State({})    # 신규 문제 탭 전용
        note_state = gr.State({})   # 오답노트 탭 전용
        fav_state = gr.State({})    # 즐겨찾기 탭 전용

        # ===== 헤더 =====
        with gr.Group():
            with gr.Row(variant='panel'):
                gr.Markdown("# <center>🐉🐉🐉🐉🐉CODE🥋DOJO🐉🐉🐉🐉🐉</center>")

        # ===== 탭 구조 =====
        with gr.Tabs():
            # ========== 탭 1: 신규 문제 ==========
            with gr.Tab("🆕 신규 문제"):
                # 필터 섹션
                with gr.Group():
                    gr.Markdown("### 📋 출제 옵션")
                    with gr.Row():
                        problem_file = gr.Dropdown(
                            choices=available_problem_files,
                            value=available_problem_files[0] if available_problem_files else DEFAULT_PROBLEM_FILE,
                            label="📁 문제은행 선택",
                            scale=1
                        )
                        difficulty = gr.Dropdown(
                            DIFFICULTY_OPTIONS,
                            value=DIFFICULTY_OPTIONS[0],
                            label="📊 난이도",
                            scale=1
                        )
                        language = gr.Dropdown(
                            language_options,
                            value=language_options[0],
                            label="💻 유형",
                            scale=1
                        )
                        problem_types = gr.CheckboxGroup(
                            choices=problem_type_options,
                            value=problem_type_options,  # 기본적으로 모두 선택
                            label="🏷️ 문제 유형 (체크된 유형만 출제)",
                            scale=1
                        )

                # 메인 콘텐츠 영역
                with gr.Row():
                    # 왼쪽: 문제
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 📋 문제")
                            question_md = gr.Markdown(
                                "새 문제 버튼을 눌러 시작하세요.",
                                container=True,
                                elem_classes="problem-box"
                            )
                            with gr.Row():
                                new_btn = gr.Button("🔄 새 문제 출제", variant="primary", size="md", scale=1)
                                favorite_btn = gr.Button("⭐ 즐겨찾기 추가", size="md", scale=1)
                            new_favorite_status_md = gr.Markdown("")

                    # 오른쪽: 코드 에디터
                    with gr.Column(scale=8):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💻 답변 작성칸")
                            code_box = gr.Code(
                                value="",
                                language="python",
                                show_label=False,
                                elem_classes="code-editor-box",
                                lines=15,
                                max_lines=50,
                                container=True
                            )
                            with gr.Row():
                                submit_btn = gr.Button(
                                    "✅ 제출하기",
                                    variant="primary",
                                    size="md",
                                    scale=8
                                )
                                hint_btn = gr.Button("💡 힌트 보기", size="md", scale=1)

                # 피드백 영역
                with gr.Row():
                    # 왼쪽 : 오답노트 추가 섹션
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="bottom-panel"):
                            gr.Markdown("### 📝 오답노트에 추가")
                            with gr.Row():
                                nickname_input = gr.Textbox(
                                    label="문제 별명 (선택사항)",
                                    placeholder="예: 복잡한 조인 문제",
                                    scale=1
                                    )
                            with gr.Row():
                                add_to_notes_btn = gr.Button("➕ 오답노트에 추가", variant="secondary", size="lg", scale=1)
                            add_notes_status = gr.Markdown("")
                    
                    # 오른쪽: LLM 피드백
                    with gr.Column(scale=8):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💬 LLM 피드백")
                            exec_result = gr.Markdown(
                                value="",
                                elem_classes="feedback-box",
                                container=True
                            )



            # ========== 탭 2: 오답노트 ==========
            with gr.Tab("📝 오답노트"):
                # 오답노트 목록
                with gr.Group():
                    gr.Markdown("### 📝 오답노트 재도전")
                    # 2단계 드롭다운: 1) PID 선택 → 2) 시도 선택
                    with gr.Row():
                        # 드롭다운 1: PID 선택
                        pid_labels, pid_values = refresh_note_pid_choices()
                        pid_choices = list(zip(pid_labels, pid_values)) if pid_labels else []
                        note_pid_dropdown = gr.Dropdown(
                            choices=pid_choices,
                            label="문제 선택",
                            scale=1
                        )
                        # 드롭다운 2: 시도 선택 (드롭다운 1 선택 후 활성화)
                        note_attempt_dropdown = gr.Dropdown(
                            choices=[],
                            label="시도 선택",
                            scale=2,
                            interactive=True
                        )
                    with gr.Row():
                        refresh_btn = gr.Button("🔄 새로고침", size="sm", scale=1)
                        load_note_btn = gr.Button("🎯 문제 불러오기", size="sm", scale=1)

                # 메인 콘텐츠 영역
                with gr.Row():
                    # 왼쪽: 문제
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 📋 문제")
                            note_question_md = gr.Markdown(
                                "오답노트에서 문제를 선택하세요.",
                                container=True,
                                elem_classes="problem-box"
                            )
                            with gr.Row():
                                note_favorite_btn = gr.Button("⭐ 즐겨찾기 추가", size="md", scale=1)
                            note_favorite_status_md = gr.Markdown("")

                    # 오른쪽: 코드 에디터
                    with gr.Column(scale=8):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💻 답변 작성칸")
                            note_code_box = gr.Code(
                                value="",
                                language="python",
                                show_label=False,
                                elem_classes="code-editor-box",
                                lines=15,
                                max_lines=50,
                                container=True
                            )
                            with gr.Row():
                                note_submit_btn = gr.Button(
                                    "✅ 제출하기",
                                    variant="primary",
                                    size="md",
                                    scale=8
                                )
                                note_hint_btn = gr.Button("💡 힌트 보기", size="md", scale=1)
                
                # 피드백 영역
                with gr.Group(elem_classes="section-box"):
                    gr.Markdown("### 💬 LLM 피드백")
                    note_exec_result = gr.Markdown(
                        value="",
                        elem_classes="feedback-box",
                        container=True
                    )
                    
            # ========== 탭 3: 즐겨찾기 ==========
            with gr.Tab("⭐ 즐겨찾기"):
                # 즐겨찾기 섹션
                with gr.Group(elem_classes="bottom-panel"):
                    gr.Markdown("### ⭐ 즐겨찾기")
                    fav_labels, fav_values = refresh_favorite_choices()
                    fav_choices = list(zip(fav_labels, fav_values)) if fav_labels else []
                    favorite_choices = gr.Dropdown(
                        choices=fav_choices,
                        label="즐겨찾기 목록",
                        scale=1
                    )
                    with gr.Row():
                        fav_refresh_btn = gr.Button("🔄 새로고침", size="sm", scale=1)
                        load_fav_btn = gr.Button("📖 문제 열기", size="sm", scale=1)
                    fav_status_md = gr.Markdown("")

                # 메인 콘텐츠 영역
                with gr.Row():
                    # 왼쪽: 문제
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 📋 문제")
                            fav_question_md = gr.Markdown(
                                "즐겨찾기 목록에서 문제를 선택하세요.",
                                container=True,
                                elem_classes="problem-box"
                            )
                            with gr.Row():
                                fav_favorite_btn = gr.Button("⭐ 즐겨찾기 추가", size="md", scale=1)
                            fav_favorite_status_md = gr.Markdown("", elem_classes="status-message")

                    # 오른쪽: 코드 에디터
                    with gr.Column(scale=8):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💻 답변 작성칸")
                            fav_code_box = gr.Code(
                                value="",
                                language="python",
                                show_label=False,
                                elem_classes="code-editor-box",
                                lines=15,
                                max_lines=50,
                                container=True
                            )
                            with gr.Row():
                                fav_submit_btn = gr.Button(
                                    "✅ 제출하기",
                                    variant="primary",
                                    size="md",
                                    scale=8
                                )
                                fav_hint_btn = gr.Button("💡 힌트 보기", size="md", scale=1)

                # 피드백 영역
                with gr.Group(elem_classes="section-box"):
                    gr.Markdown("### 💬 LLM 피드백")
                    fav_exec_result = gr.Markdown(
                        value="",
                        elem_classes="feedback-box",
                        container=True
                    )


        # ===== 이벤트 핸들러 - 신규 문제 탭 =====

        # 문제 파일 선택 시 난이도/언어 드롭다운 옵션 업데이트
        def on_problem_file_change(selected_file):
            """문제 파일 변경 시 난이도/언어 옵션 업데이트"""
            _, new_difficulty_options, new_language_options = reload_problem_bank(selected_file)
            return (
                gr.update(choices=new_difficulty_options, value=new_difficulty_options[0] if new_difficulty_options else None),
                gr.update(choices=new_language_options, value=new_language_options[0] if new_language_options else "전체"),
            )

        problem_file.change(
            on_problem_file_change,
            inputs=[problem_file],
            outputs=[difficulty, language],
        )

        new_btn.click(
            on_new_problem,
            inputs=[problem_file, difficulty, language, problem_types],
            outputs=[question_md, new_state, code_box, favorite_btn, exec_result, note_pid_dropdown, hint_btn, add_notes_status, nickname_input],
        )

        submit_btn.click(
            on_submit,
            inputs=[new_state, code_box],
            outputs=[exec_result, note_pid_dropdown, hint_btn],
            show_progress="minimal",
        )

        hint_btn.click(
            toggle_hint,
            inputs=new_state,
            outputs=[exec_result, hint_btn, new_state],
        )

        # ===== 헬퍼 함수: 즐겨찾기 버튼 업데이트 =====
        def _get_favorite_button_update(state_dict):
            """state에서 즐겨찾기 버튼 업데이트를 계산합니다.

            Args:
                state_dict: 탭의 state 딕셔너리

            Returns:
                gr.update: 버튼 업데이트 객체
            """
            if state_dict and "problem" in state_dict:
                source_file = state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                return gr.update(value=favorite_button_label(state_dict["problem"].pid, source_file))
            return gr.update()  # state 없으면 변경 안 함

        # 신규 문제 탭의 즐겨찾기 버튼 (버튼만 동기화, 메시지는 현재 탭만)
        def toggle_favorite_new_tab(new_state_dict, note_state_dict, fav_state_dict):
            # 현재 탭(신규 출제)의 문제에 대해 즐겨찾기 토글
            btn_update, message, choices_update = toggle_favorite(new_state_dict)
            # 다른 탭의 버튼 업데이트 계산
            note_btn = _get_favorite_button_update(note_state_dict)
            fav_btn = _get_favorite_button_update(fav_state_dict)
            # 메시지는 현재 탭(신규 출제)에만 표시
            return btn_update, message, choices_update, note_btn, "", fav_btn, ""

        favorite_btn.click(
            toggle_favorite_new_tab,
            inputs=[new_state, note_state, fav_state],
            outputs=[favorite_btn, new_favorite_status_md, favorite_choices, note_favorite_btn, note_favorite_status_md, fav_favorite_btn, fav_favorite_status_md],
        )

        # ===== 이벤트 핸들러 - 즐겨찾기 탭 =====
        def refresh_favorites(new_state_dict, note_state_dict):
            labels, values = refresh_favorite_choices()

            # 다른 탭의 버튼 레이블 계산
            if new_state_dict and "problem" in new_state_dict:
                source_file = new_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                new_btn = favorite_button_label(new_state_dict["problem"].pid, source_file)
            else:
                new_btn = "☆ 즐겨찾기 추가"

            if note_state_dict and "problem" in note_state_dict:
                source_file = note_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                note_btn = favorite_button_label(note_state_dict["problem"].pid, source_file)
            else:
                note_btn = "☆ 즐겨찾기 추가"

            return (
                gr.update(choices=list(zip(labels, values)), value=None),
                {},
                "즐겨찾기 목록에서 문제를 선택하세요.",
                gr.update(value=""),
                "",
                gr.update(value="💡 힌트 보기"),
                "☆ 즐겨찾기 추가",  # fav_favorite_btn (현재 탭이므로 초기화)
                "",
                note_btn,  # note_favorite_btn
                new_btn,   # favorite_btn
            )

        fav_refresh_btn.click(
            refresh_favorites,
            inputs=[new_state, note_state],
            outputs=[favorite_choices, fav_state, fav_question_md, fav_code_box, fav_exec_result, fav_hint_btn, fav_favorite_btn, fav_favorite_status_md, note_favorite_btn, favorite_btn]
        )

        def load_favorite_selection(composite_key, new_state_dict, note_state_dict, fav_state_dict):
            """즐겨찾기에서 문제를 불러옵니다. composite_key는 'source_file:pid' 형식입니다."""
            if not composite_key:
                return (
                    gr.update(),
                    {},
                    gr.update(),
                    "",
                    gr.update(value="💡 힌트 보기"),
                    "☆ 즐겨찾기 추가",
                    "",
                    "☆ 즐겨찾기 추가",
                    "☆ 즐겨찾기 추가",
                )

            # 복합 키 파싱: source_file:pid
            parts = composite_key.split(":", 1)
            if len(parts) == 2:
                source_file, pid = parts
            else:
                source_file, pid = DEFAULT_PROBLEM_FILE, composite_key

            question, state_val, code_update, btn_label, status_text, hint_update = load_favorite_problem(pid, source_file)

            # 각 탭의 버튼 레이블을 개별적으로 계산
            fav_btn = btn_label  # 현재 불러온 문제

            if new_state_dict and "problem" in new_state_dict:
                new_source = new_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                new_btn = favorite_button_label(new_state_dict["problem"].pid, new_source)
            else:
                new_btn = "☆ 즐겨찾기 추가"

            if note_state_dict and "problem" in note_state_dict:
                note_source = note_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                note_btn = favorite_button_label(note_state_dict["problem"].pid, note_source)
            else:
                note_btn = "☆ 즐겨찾기 추가"

            return question, state_val, code_update, status_text, hint_update, fav_btn, "", note_btn, new_btn

        load_fav_btn.click(
            load_favorite_selection,
            inputs=[favorite_choices, new_state, note_state, fav_state],
            outputs=[fav_question_md, fav_state, fav_code_box, fav_status_md, fav_hint_btn, fav_favorite_btn, fav_favorite_status_md, note_favorite_btn, favorite_btn],
        )


        # 즐겨찾기 탭의 제출/힌트 버튼
        fav_submit_btn.click(
            on_submit,
            inputs=[fav_state, fav_code_box],
            outputs=[fav_exec_result, note_pid_dropdown, fav_hint_btn],
            show_progress="minimal",
        )

        fav_hint_btn.click(
            toggle_hint,
            inputs=fav_state,
            outputs=[fav_exec_result, fav_hint_btn, fav_state],
        )

        # 즐겨찾기 탭의 문제 영역 즐겨찾기 버튼 (버튼만 동기화, 메시지는 현재 탭만)
        def toggle_favorite_fav_tab(fav_state_dict, new_state_dict, note_state_dict):
            # 현재 탭(즐겨찾기)의 문제에 대해 즐겨찾기 토글
            btn_update, message, choices_update = toggle_favorite(fav_state_dict)
            # 다른 탭의 버튼 업데이트 계산
            new_btn = _get_favorite_button_update(new_state_dict)
            note_btn = _get_favorite_button_update(note_state_dict)
            # 메시지는 현재 탭(즐겨찾기)에만 표시
            return btn_update, message, choices_update, new_btn, "", note_btn, ""

        fav_favorite_btn.click(
            toggle_favorite_fav_tab,
            inputs=[fav_state, new_state, note_state],
            outputs=[fav_favorite_btn, fav_favorite_status_md, favorite_choices, favorite_btn, new_favorite_status_md, note_favorite_btn, note_favorite_status_md],
        )

        # 오답노트 추가 이벤트
        def on_add_to_notes(state_dict, nickname, progress=gr.Progress()):
            """오답노트에 수동으로 추가합니다."""
            progress(0.1, desc="오답노트 저장 시작...")

            if not state_dict or "problem" not in state_dict:
                return "⚠️ 먼저 문제를 출제하고 코드를 제출하세요.", gr.update()

            if "last_code" not in state_dict or "last_feedback" not in state_dict:
                return "⚠️ 먼저 코드를 제출하여 피드백을 받으세요.", gr.update()

            problem = state_dict["problem"]
            source_file = state_dict.get("source_file", DEFAULT_PROBLEM_FILE)

            # 중복 저장 체크: 같은 source_file + pid + nickname 조합으로 이미 저장되었는지 확인
            existing_attempts = load_attempts()
            if any(
                attempt.pid == problem.pid
                and attempt.nickname == nickname
                and attempt.source_file == source_file
                for attempt in existing_attempts
            ):
                return "⚠️ 같은 별명으로 이미 저장된 문제입니다.", gr.update()

            code = state_dict["last_code"]
            feedback = state_dict["last_feedback"]

            progress(0.5, desc="LLM으로 힌트 요약 중...")
            hint_summary = generate_hint_summary(problem, code, feedback, LM_STUDIO_ENDPOINT)

            progress(0.8, desc="오답노트에 저장 중...")
            result = save_to_wrong_notes(problem, code, feedback, nickname, hint_summary, source_file)

            progress(0.9, desc="오답노트 목록 갱신 중...")
            # 오답노트 목록 갱신 (PID 드롭다운만)
            pid_labels, pid_values = refresh_note_pid_choices()
            pid_choices_updated = list(zip(pid_labels, pid_values)) if pid_labels else []

            return result, gr.update(choices=pid_choices_updated, value=None)

        add_to_notes_btn.click(
            on_add_to_notes,
            inputs=[new_state, nickname_input],
            outputs=[add_notes_status, note_pid_dropdown],
            show_progress="minimal",
        )

        # ===== 이벤트 핸들러 - 오답노트 탭 =====
        def update_attempt_dropdown(selected_pid):
            """드롭다운 1에서 PID 선택 시 드롭다운 2 업데이트"""
            if not selected_pid:
                return gr.update(choices=[], value=None)

            labels, values = refresh_note_attempt_choices(selected_pid)
            choices = list(zip(labels, values)) if labels else []
            return gr.update(choices=choices, value=None)

        # 드롭다운 1 선택 시 드롭다운 2 업데이트
        note_pid_dropdown.change(
            update_attempt_dropdown,
            inputs=[note_pid_dropdown],
            outputs=[note_attempt_dropdown]
        )

        def refresh_notes(new_state_dict, fav_state_dict):
            # PID 드롭다운 갱신
            pid_labels, pid_values = refresh_note_pid_choices()
            pid_choices = list(zip(pid_labels, pid_values)) if pid_labels else []

            # 다른 탭의 버튼 레이블 계산
            if new_state_dict and "problem" in new_state_dict:
                new_source = new_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                new_btn = favorite_button_label(new_state_dict["problem"].pid, new_source)
            else:
                new_btn = "☆ 즐겨찾기 추가"

            if fav_state_dict and "problem" in fav_state_dict:
                fav_source = fav_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                fav_btn = favorite_button_label(fav_state_dict["problem"].pid, fav_source)
            else:
                fav_btn = "☆ 즐겨찾기 추가"

            return (
                gr.update(choices=pid_choices, value=None),  # note_pid_dropdown
                gr.update(choices=[], value=None),  # note_attempt_dropdown 초기화
                {},  # note_state
                "오답노트에서 문제를 선택하세요.",  # note_question_md
                gr.update(value=""),  # note_code_box
                "",  # note_exec_result
                gr.update(value="💡 힌트 보기"),  # note_hint_btn
                "☆ 즐겨찾기 추가",  # note_favorite_btn (현재 탭이므로 초기화)
                "",  # note_favorite_status_md
                fav_btn,  # fav_favorite_btn
                new_btn,  # favorite_btn
            )

        refresh_btn.click(
            refresh_notes,
            inputs=[new_state, fav_state],
            outputs=[note_pid_dropdown, note_attempt_dropdown, note_state, note_question_md, note_code_box, note_exec_result, note_hint_btn, note_favorite_btn, note_favorite_status_md, fav_favorite_btn, favorite_btn]
        )

        def load_note_to_tab(composite_key, new_state_dict, note_state_dict, fav_state_dict):
            """오답노트 탭용: 문제 불러오기 (복합 키 사용)"""
            if not composite_key:
                return gr.update(), {}, gr.update(), "", gr.update(value="💡 힌트 보기"), "☆ 즐겨찾기 추가", "", "☆ 즐겨찾기 추가", "☆ 즐겨찾기 추가"

            # load_from_notes() 함수 사용
            question, note_state_val, code_update, note_btn, status = load_from_notes(composite_key)

            # 다른 탭의 버튼 레이블 계산
            if new_state_dict and "problem" in new_state_dict:
                new_source = new_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                new_btn = favorite_button_label(new_state_dict["problem"].pid, new_source)
            else:
                new_btn = "☆ 즐겨찾기 추가"

            if fav_state_dict and "problem" in fav_state_dict:
                fav_source = fav_state_dict.get("source_file", DEFAULT_PROBLEM_FILE)
                fav_btn = favorite_button_label(fav_state_dict["problem"].pid, fav_source)
            else:
                fav_btn = "☆ 즐겨찾기 추가"

            return (
                question,  # note_question_md
                note_state_val,  # note_state
                code_update,  # note_code_box
                status,  # note_exec_result
                gr.update(value="💡 힌트 보기"),  # note_hint_btn
                note_btn,  # note_favorite_btn
                "",  # note_favorite_status_md
                fav_btn,  # fav_favorite_btn
                new_btn,  # favorite_btn
            )

        load_note_btn.click(
            load_note_to_tab,
            inputs=[note_attempt_dropdown, new_state, note_state, fav_state],
            outputs=[note_question_md, note_state, note_code_box, note_exec_result, note_hint_btn, note_favorite_btn, note_favorite_status_md, fav_favorite_btn, favorite_btn],
        )

        note_submit_btn.click(
            on_submit,
            inputs=[note_state, note_code_box],
            outputs=[note_exec_result, note_pid_dropdown, note_hint_btn],
            show_progress="minimal",
        )

        note_hint_btn.click(
            toggle_hint,
            inputs=note_state,
            outputs=[note_exec_result, note_hint_btn, note_state],
        )

        # 오답노트 탭의 즐겨찾기 버튼 (버튼만 동기화, 메시지는 현재 탭만)
        def toggle_favorite_note_tab(note_state_dict, new_state_dict, fav_state_dict):
            # 현재 탭(오답노트)의 문제에 대해 즐겨찾기 토글
            btn_update, message, choices_update = toggle_favorite(note_state_dict)
            # 다른 탭의 버튼 업데이트 계산
            new_btn = _get_favorite_button_update(new_state_dict)
            fav_btn = _get_favorite_button_update(fav_state_dict)
            # 메시지는 현재 탭(오답노트)에만 표시
            return btn_update, message, choices_update, new_btn, "", fav_btn, ""

        note_favorite_btn.click(
            toggle_favorite_note_tab,
            inputs=[note_state, new_state, fav_state],
            outputs=[note_favorite_btn, note_favorite_status_md, favorite_choices, favorite_btn, new_favorite_status_md, fav_favorite_btn, fav_favorite_status_md],
        )

    return demo


app = build_interface()

if __name__ == "__main__":
    app.launch(theme=CUSTOM_THEME, css=CUSTOM_CSS)
