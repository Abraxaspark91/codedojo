import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import gradio as gr
import requests
from problem_bank import DIFFICULTY_OPTIONS, PROBLEM_BANK, Problem

NOTE_PATH = Path("data/wrong_notes.md")
NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
FAVORITES_PATH = Path("data/favorites.json")
FAVORITES_PATH.parent.mkdir(parents=True, exist_ok=True)

_env_path = Path(".env")
_env_text = _env_path.read_text(encoding="utf-8") if _env_path.exists() else ""
LM_STUDIO_ENDPOINT = (
    _env_text.split("LM_STUDIO_ENDPOINT=", maxsplit=1)[-1].splitlines()[0].strip()
    if "LM_STUDIO_ENDPOINT=" in _env_text
    else "http://127.0.0.1:1234/v1/chat/completions"
)

CUSTOM_THEME = gr.themes.Soft(
    primary_hue="emerald",
    neutral_hue="slate",
).set(
    body_background_fill="*neutral_950",
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
    min-height: 300px;
    max-height: 400px;
    overflow-y: auto;
}

.feedback-box {
    min-height: 250px;
    max-height: 350px;
    overflow-y: auto;
}

.code-editor-box {
    min-height: 500px;
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
        feedback: LLM 또는 휴리스틱 피드백
        improvement: 보완 포인트
        reasoning: 해설/의도 추측
        question: 문제 내용
        code: 제출 코드
        kind: 프로그래밍 언어 (sql/python, Gradio Code 컴포넌트 지원 언어)
        timestamp: 제출 시간 (형식: "YYYY-MM-DD HH:MM (요일)")
        rechallenge_hint: 재도전 시 참고할 힌트
        nickname: 문제 별명 (사용자 지정)
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


def ensure_state(state: Optional[Dict]) -> Dict:
    if state is None:
        state = {}

    state.setdefault("in_progress", False)
    state.setdefault("last_run_detail", "")
    state.setdefault("last_feedback", "")
    state.setdefault("last_improvement", "")
    state.setdefault("filters", normalize_filters(None, None, None))
    return state


def unique_preserve_order(items: List[str]) -> List[str]:
    seen = []
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.append(item)
        ordered.append(item)
    return ordered




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


def load_attempts() -> List[Attempt]:
    """오답노트 파일에서 모든 Attempt를 로드합니다.

    JSON Lines 형식: 각 라인이 하나의 JSON 객체
    - 손상된 라인은 무시하고 나머지 계속 파싱
    - 라인 단위 오류 로깅으로 문제 진단 용이
    """
    ensure_note_file()
    text = NOTE_PATH.read_text(encoding="utf-8")
    entries: List[Attempt] = []

    # 빈 파일 처리
    if not text.strip():
        return entries

    # 각 라인을 독립적으로 파싱
    for line_idx, line in enumerate(text.split("\n"), 1):
        line = line.strip()

        # 빈 라인 무시
        if not line:
            continue

        try:
            # JSON 파싱
            data = json.loads(line)

            # Attempt 객체 생성
            entry = Attempt(**data)
            entries.append(entry)

        except json.JSONDecodeError as e:
            # JSON 파싱 오류: 해당 라인 무시, 계속 진행
            print(
                f"[경고] 라인 {line_idx}의 JSON 파싱 실패: {str(e)[:80]}",
                file=__import__('sys').stderr)
            continue

        except TypeError as e:
            # Attempt 필드 부족: 해당 라인 무시, 계속 진행
            print(
                f"[경고] 라인 {line_idx}의 Attempt 생성 실패: {str(e)[:80]}",
                file=__import__('sys').stderr)
            continue

        except Exception as e:
            # 예상 외의 오류
            print(
                f"[경고] 라인 {line_idx}의 처리 오류: {str(e)[:80]}",
                file=__import__('sys').stderr)
            continue

    return entries


def failed_attempts(entries: List[Attempt]) -> List[Attempt]:
    return [a for a in entries if a.score < 80]


def matches_filters(
        problem: Problem,
        difficulty: Optional[str],
        language: Optional[str],
        problem_types: Optional[List[str]]) -> bool:
    """문제가 필터 조건과 일치하는지 확인합니다."""
    language_match = (not language or language ==
                      "전체") or problem.kind.lower() == language.lower()
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
) -> Tuple[Problem, bool, str, Dict]:
    """체크박스로 선택된 problem_types 중에서 문제를 선택합니다."""
    entries = load_attempts()
    failed = failed_attempts(entries)
    rechallenge = False
    hint = ""
    target_filters = normalize_filters(difficulty, language, problem_types)

    # 필터 우선순위 (problem_types는 리스트로 유지)
    filter_priority = [
        (difficulty, language, problem_types),
        (difficulty, language, []),
        (difficulty, None, problem_types),
        (difficulty, None, []),
        (None, language, problem_types),
        (None, language, []),
        (None, None, problem_types),
        (None, None, []),
    ]

    def choose_candidate(
            pool: List[Tuple[Problem, str]]) -> Tuple[Problem, Dict]:
        for diff_opt, lang_opt, types_opt in filter_priority:
            candidates = [
                (prob, attempt_hint)
                for prob, attempt_hint in pool
                if matches_filters(prob, diff_opt, lang_opt, types_opt)
            ]
            if candidates:
                prob, attempt_hint = random.choice(candidates)
                return prob, normalize_filters(diff_opt, lang_opt, types_opt) | {
                    "hint": attempt_hint}
        prob, attempt_hint = random.choice(pool)
        return prob, normalize_filters(None, None, []) | {
            "hint": attempt_hint}

    failed_pool: List[Tuple[Problem, str]] = []
    for entry in failed:
        problem = next((p for p in PROBLEM_BANK if p.pid == entry.pid), None)
        if problem:
            failed_pool.append((problem, entry.rechallenge_hint))

    applied_filters = target_filters
    if failed_pool and random.random() < 0.3:
        rechallenge = True
        problem, applied_filters = choose_candidate(failed_pool)
        hint = applied_filters.pop("hint", "지난 시도에서 놓친 부분을 점검해 보세요.")
        return problem, rechallenge, hint, applied_filters

    full_pool = [(p, "") for p in PROBLEM_BANK]
    problem, applied_filters = choose_candidate(full_pool)
    hint = applied_filters.pop("hint", "")
    return problem, rechallenge, hint, applied_filters


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
    result = (
        f"### [{banner}] {problem.title}\n"
        f"- 난이도: {problem.difficulty}\n"
        f"- 언어: {problem.kind}\n"
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
    deduped = {}
    for fav in favorites:
        pid = fav.get("pid")
        if pid:
            deduped[pid] = {
                "pid": pid,
                "title": fav.get("title", ""),
                "difficulty": fav.get("difficulty", ""),
                "kind": fav.get("kind", ""),
            }
    FAVORITES_PATH.write_text(
        json.dumps(
            list(
                deduped.values()),
            ensure_ascii=False,
            indent=2),
        encoding="utf-8")


def favorite_button_label(pid: str) -> str:
    favorites = load_favorites()
    return "⭐ 즐겨찾기 해제" if any(
        fav.get("pid") == pid for fav in favorites) else "☆ 즐겨찾기 추가"


def refresh_favorite_choices() -> Tuple[List[str], List[str]]:
    favorites = load_favorites()
    labels = [
        f"{fav['pid']} | {fav.get('difficulty','')} | {fav.get('kind','')} | {fav.get('title','')}"
        for fav in favorites
    ]
    values = [fav["pid"] for fav in favorites]
    return labels, values


def favorite_status_text(pid: str) -> str:
    return ("⭐ 즐겨찾기에 저장된 문제입니다." if favorite_button_label(
        pid).startswith("⭐") else "☆ 즐겨찾기에 추가할 수 있습니다.")


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
        response = requests.post(endpoint, json=payload, timeout=120)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, ValueError, IndexError) as exc:
        return (
            "LLM 서버에 연결하지 못했습니다.\n"
            f"로컬 엔드포인트({endpoint})를 확인하세요.\n"
            f"대신 휴리스틱 피드백을 제공합니다. ({exc})"
        )




def build_feedback(
    problem: Problem, code: str, endpoint: str
) -> str:
    """LLM을 사용하여 코드에 대한 피드백을 생성합니다."""
    system_prompt = (
        "당신은 SQL, Python, Pseudocode, Technical Decomp문제의 채점을 돕는 조교입니다. "
        "제출된 코드를 분석하여 피드백을 제공하세요. "
        "정답 여부, 놓친 부분, 효율/논리 개선, 작성자의 의도 추정을 포함합니다.")
    user_prompt = (
        f"문제: {problem.body}\n"
        f"스키마: {problem.schema}\n"
        f"코드:```{problem.kind}\n{code}\n```\n"
        "다음 사항을 포함하여 피드백을 제공하세요:\n"
        "- 1) 코드 분석 및 평가\n"
        "- 2) 보완이 필요한 부분\n"
        "- 3) 더 효율적이거나 간결한 방법\n"
        "- 4) 작성자의 의도 추측")
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
    rechallenge_hint: str
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
    )

    try:
        serialized = serialize_attempt(attempt)
        # JSON Lines: 기존 내용에 새 라인을 추가
        current_content = NOTE_PATH.read_text(encoding="utf-8")
        # 마지막 줄이 개행으로 끝나지 않으면 추가
        if current_content and not current_content.endswith("\n"):
            current_content += "\n"
        NOTE_PATH.write_text(
            current_content + serialized + "\n",
            encoding="utf-8"
        )
        return f"✅ 오답노트에 추가되었습니다! ({format_timestamp_with_weekday()})"
    except ValueError as e:
        print(f"[오류] Attempt 저장 실패: {e}", file=__import__('sys').stderr)
        return f"❌ 저장 실패: {str(e)}"


def refresh_note_choices() -> Tuple[List[str], List[str]]:
    entries = failed_attempts(load_attempts())
    labels = [f"{a.pid} | {a.score}점 | {a.title}" for a in entries]
    values = [a.pid for a in entries]
    return labels, values


def load_from_notes(
        selected_pid: str) -> Tuple[str, Dict, gr.update, str, str]:
    entries = failed_attempts(load_attempts())
    for entry in entries:
        if entry.pid == selected_pid:
            problem = next(
                (p for p in PROBLEM_BANK if p.pid == entry.pid), None)
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
                    },
                    gr.update(value="", language=problem.kind),
                    favorite_button_label(problem.pid),
                    favorite_status_text(problem.pid),
                )
    return "선택한 문제가 없습니다.", {}, gr.update(), "☆ 즐겨찾기 추가", "재도전 문제를 선택하세요."


def load_favorite_problem(pid: str) -> Tuple[str, Dict, gr.update, str, str]:
    problem = next((p for p in PROBLEM_BANK if p.pid == pid), None)
    if problem:
        filters = normalize_filters(None, None, None)
        question = render_question(problem, False, "", filters)
        return (
            question,
            {
                "problem": problem,
                "rechallenge": False,
                "hint": "",
                "filters": filters,
                "in_progress": False,
            },
            gr.update(value="", language=problem.kind),
            favorite_button_label(problem.pid),
            favorite_status_text(problem.pid),
        )
    return "선택한 즐겨찾기 문제가 없습니다.", {}, gr.update(), "☆ 즐겨찾기 추가", "즐겨찾기 문제를 선택하세요."


def on_new_problem(difficulty: str,
                   language: str,
                   problem_types: List[str]) -> Tuple[str,
                                                      Dict,
                                                      gr.update,
                                                      str,
                                                      str,
                                                      str,
                                                      gr.update]:
    """새 문제를 출제합니다. problem_types는 체크박스로 선택된 리스트입니다."""
    filters = normalize_filters(difficulty, language, problem_types)
    problem, rechallenge, hint, applied_filters = pick_problem(
        difficulty, language, problem_types)
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
            "last_run_detail": "",
            "last_feedback": "",
            "last_improvement": "",
        }
    )
    # 오답노트 목록 자동 업데이트
    labels, values = refresh_note_choices()
    note_choices = list(zip(labels, values)) if labels else []

    return (
        question,
        state,
        gr.update(value="", language=problem.kind),
        favorite_button_label(problem.pid),
        favorite_status_text(problem.pid),
        "",  # exec_result 초기화
        gr.update(choices=note_choices, value=None),  # note_choices 업데이트
    )


def on_submit(state: Dict, code: str, progress=gr.Progress()
              ) -> Tuple[str, gr.update]:
    """코드를 제출하고 LLM 피드백을 받습니다. (자동 저장 없음)"""
    state = ensure_state(state)
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다.", gr.update()

    if state.get("in_progress"):
        return "피드백 생성이 진행 중입니다. 잠시만 기다려주세요.", gr.update()

    state["in_progress"] = True
    problem: Problem = state["problem"]

    progress(0.5, desc="LLM 피드백 생성 중")
    feedback = build_feedback(problem, code, LM_STUDIO_ENDPOINT)

    state.update({"in_progress": False, "last_feedback": feedback, "last_code": code})

    # LLM 피드백만 반환
    result = f"### 💬 LLM 피드백\n{feedback}"

    return result, gr.update()


def show_hint(state: Dict) -> str:
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다."
    problem: Problem = state["problem"]
    return f"문법 힌트: {problem.hint}"


def toggle_favorite(state: Dict) -> Tuple[gr.update, str, gr.update]:
    if not state or "problem" not in state:
        labels, values = refresh_favorite_choices()
        return gr.update(), "문제가 선택되지 않았습니다.", gr.update(
            choices=list(zip(labels, values)), value=None)

    problem: Problem = state["problem"]
    favorites = load_favorites()
    exists = any(fav.get("pid") == problem.pid for fav in favorites)

    if exists:
        favorites = [fav for fav in favorites if fav.get("pid") != problem.pid]
        message = "즐겨찾기에서 제거했습니다."
        new_value = None
    else:
        favorites.append(
            {
                "pid": problem.pid,
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
        gr.update(value=favorite_button_label(problem.pid)),
        message,
        gr.update(choices=list(zip(labels, values)), value=new_value),
    )


def build_interface() -> gr.Blocks:
    language_options = ["전체"] + \
        unique_preserve_order([p.kind for p in PROBLEM_BANK])
    # 문제 유형 옵션 (체크박스용)
    problem_type_options = ["코딩", "개념문제", "빈칸채우기"]

    # Create Blocks with dark theme by default
    js_code = """
    function() {
        // Set dark mode by default
        if (document.querySelector('.dark') === null) {
            document.body.classList.add('dark');
        }
    }
    """

    try:
        demo = gr.Blocks(
            title="SQL & Python 코딩 연습",
            theme=CUSTOM_THEME,
            css=CUSTOM_CSS,
            js=js_code
        )
    except TypeError:
        demo = gr.Blocks(title="SQL & Python 코딩 연습")

    with demo:
        state = gr.State({})

        # ===== 헤더 =====
        with gr.Group():
            with gr.Row():
                gr.Markdown("# 🎯 SQL & Python 코딩 연습 스테이션", container=True)

        # ===== 탭 구조 =====
        with gr.Tabs():
            # ========== 탭 1: 신규 문제 ==========
            with gr.Tab("🆕 신규 문제"):
                # 필터 섹션
                with gr.Group():
                    gr.Markdown("### 📋 출제 옵션")
                    with gr.Row():
                        difficulty = gr.Dropdown(
                            DIFFICULTY_OPTIONS,
                            value=DIFFICULTY_OPTIONS[0],
                            label="📊 난이도",
                            scale=1
                        )
                        language = gr.Dropdown(
                            language_options,
                            value=language_options[0],
                            label="💻 언어",
                            scale=1
                        )
                    with gr.Row():
                        problem_types = gr.CheckboxGroup(
                            choices=problem_type_options,
                            value=problem_type_options,  # 기본적으로 모두 선택
                            label="🏷️ 문제 유형 (체크된 유형만 출제)",
                            scale=1
                        )
                    with gr.Row():
                        new_btn = gr.Button("🔄 새 문제 출제", variant="primary", size="md", scale=1)

                # 메인 콘텐츠 영역
                with gr.Row():
                    # 왼쪽: 문제
                    with gr.Column(scale=2):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 📋 문제")
                            question_md = gr.Markdown(
                                "새 문제 버튼을 눌러 시작하세요.",
                                container=True,
                                elem_classes="problem-box"
                            )

                    # 오른쪽: 코드 에디터
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💻 답변 작성칸")
                            code_box = gr.Code(
                                value="",
                                language="python",
                                show_label=False,
                                elem_classes="code-editor-box",
                                lines=20,
                                container=True
                            )
                            with gr.Row(elem_classes="button-row"):
                                submit_btn = gr.Button(
                                    "✅ 제출하기",
                                    variant="primary",
                                    size="lg",
                                    scale=3
                                )
                                hint_btn = gr.Button("💡 힌트 보기", size="lg", scale=1)

                # 피드백 영역
                with gr.Group(elem_classes="section-box"):
                    gr.Markdown("### 💬 LLM 피드백")
                    exec_result = gr.Markdown(
                        value="",
                        elem_classes="feedback-box",
                        container=True
                    )

                # 오답노트 추가 섹션
                with gr.Group(elem_classes="bottom-panel"):
                    gr.Markdown("### 📝 오답노트에 추가")
                    nickname_input = gr.Textbox(
                        label="문제 별명 (선택사항)",
                        placeholder="예: 복잡한 조인 문제",
                        scale=1
                    )
                    with gr.Row():
                        add_to_notes_btn = gr.Button("➕ 오답노트에 추가", variant="secondary", size="md", scale=1)
                    add_notes_status = gr.Markdown("", scale=1)

                # 즐겨찾기 섹션
                with gr.Group(elem_classes="bottom-panel"):
                    gr.Markdown("### ⭐ 즐겨찾기")
                    with gr.Row():
                        favorite_btn = gr.Button("⭐ 즐겨찾기 추가", size="sm", scale=1)
                        favorite_status_md = gr.Markdown("", scale=2)
                    fav_labels, fav_values = refresh_favorite_choices()
                    fav_choices = list(zip(fav_labels, fav_values)) if fav_labels else []
                    favorite_choices = gr.Dropdown(
                        choices=fav_choices,
                        label="즐겨찾기 목록",
                        scale=1
                    )
                    with gr.Row():
                        fav_refresh_btn = gr.Button("🔄 새로고침", size="sm", scale=1)
                        load_fav_btn = gr.Button("📖 열기", size="sm", scale=1)

            # ========== 탭 2: 오답노트 ==========
            with gr.Tab("📝 오답노트"):
                # 오답노트 목록
                with gr.Group():
                    gr.Markdown("### 📝 오답노트 재도전")
                    note_labels, note_values = refresh_note_choices()
                    note_choice = list(zip(note_labels, note_values)) if note_labels else []
                    note_choices = gr.Dropdown(
                        choices=note_choice,
                        label="문제 선택",
                        scale=1
                    )
                    with gr.Row():
                        refresh_btn = gr.Button("🔄 새로고침", size="sm", scale=1)
                        load_note_btn = gr.Button("🎯 문제 불러오기", size="sm", scale=1)

                # 메인 콘텐츠 영역
                with gr.Row():
                    # 왼쪽: 문제
                    with gr.Column(scale=2):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 📋 문제")
                            note_question_md = gr.Markdown(
                                "오답노트에서 문제를 선택하세요.",
                                container=True,
                                elem_classes="problem-box"
                            )

                    # 오른쪽: 코드 에디터
                    with gr.Column(scale=3):
                        with gr.Group(elem_classes="section-box"):
                            gr.Markdown("### 💻 답변 작성칸")
                            note_code_box = gr.Code(
                                value="",
                                language="python",
                                show_label=False,
                                elem_classes="code-editor-box",
                                lines=20,
                                container=True
                            )
                            with gr.Row(elem_classes="button-row"):
                                note_submit_btn = gr.Button(
                                    "✅ 제출하기",
                                    variant="primary",
                                    size="lg",
                                    scale=3
                                )
                                note_hint_btn = gr.Button("💡 힌트 보기", size="lg", scale=1)

                # 피드백 영역
                with gr.Group(elem_classes="section-box"):
                    gr.Markdown("### 💬 LLM 피드백")
                    note_exec_result = gr.Markdown(
                        value="",
                        elem_classes="feedback-box",
                        container=True
                    )

        # ===== 이벤트 핸들러 - 신규 문제 탭 =====
        new_btn.click(
            on_new_problem,
            inputs=[difficulty, language, problem_types],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result, note_choices],
        )

        difficulty.change(
            on_new_problem,
            inputs=[difficulty, language, problem_types],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result, note_choices],
        )

        language.change(
            on_new_problem,
            inputs=[difficulty, language, problem_types],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result, note_choices],
        )

        problem_types.change(
            on_new_problem,
            inputs=[difficulty, language, problem_types],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result, note_choices],
        )

        submit_btn.click(
            on_submit,
            inputs=[state, code_box],
            outputs=[exec_result, note_choices],
            show_progress="minimal",
        )

        hint_btn.click(show_hint, inputs=state, outputs=exec_result)

        favorite_btn.click(
            toggle_favorite,
            inputs=state,
            outputs=[favorite_btn, favorite_status_md, favorite_choices],
        )

        def refresh_favorites():
            labels, values = refresh_favorite_choices()
            return gr.update(choices=list(zip(labels, values)), value=None)

        fav_refresh_btn.click(refresh_favorites, outputs=favorite_choices)

        def load_favorite_selection(pid):
            if not pid:
                return gr.update(), {}, gr.update(), "☆ 즐겨찾기 추가", ""
            return load_favorite_problem(pid)

        load_fav_btn.click(
            load_favorite_selection,
            inputs=favorite_choices,
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md],
        )

        # 오답노트 추가 이벤트
        def on_add_to_notes(state_dict, nickname, progress=gr.Progress()):
            """오답노트에 수동으로 추가합니다."""
            if not state_dict or "problem" not in state_dict:
                return "⚠️ 먼저 문제를 출제하고 코드를 제출하세요.", gr.update()

            if "last_code" not in state_dict or "last_feedback" not in state_dict:
                return "⚠️ 먼저 코드를 제출하여 피드백을 받으세요.", gr.update()

            problem = state_dict["problem"]
            code = state_dict["last_code"]
            feedback = state_dict["last_feedback"]

            progress(0.5, desc="LLM으로 힌트 요약 중...")
            hint_summary = generate_hint_summary(problem, code, feedback, LM_STUDIO_ENDPOINT)

            progress(0.8, desc="오답노트에 저장 중...")
            result = save_to_wrong_notes(problem, code, feedback, nickname, hint_summary)

            # 오답노트 목록 갱신
            labels, values = refresh_note_choices()
            note_choices_updated = list(zip(labels, values)) if labels else []

            return result, gr.update(choices=note_choices_updated, value=None)

        add_to_notes_btn.click(
            on_add_to_notes,
            inputs=[state, nickname_input],
            outputs=[add_notes_status, note_choices],
            show_progress="minimal",
        )

        # ===== 이벤트 핸들러 - 오답노트 탭 =====
        def refresh_notes():
            labels, values = refresh_note_choices()
            choices = list(zip(labels, values))
            return gr.update(choices=choices, value=None), ""

        refresh_btn.click(refresh_notes, outputs=[note_choices, note_exec_result])

        def load_note_to_tab(pid):
            """오답노트 탭용: 문제 불러오기"""
            if not pid:
                return gr.update(), {}, gr.update(), ""

            entries = failed_attempts(load_attempts())
            for entry in entries:
                if entry.pid == pid:
                    problem = next((p for p in PROBLEM_BANK if p.pid == entry.pid), None)
                    if problem:
                        filters = normalize_filters(None, None, None)
                        question = render_question(problem, True, entry.rechallenge_hint, filters)
                        return (
                            question,
                            {"problem": problem, "rechallenge": True, "hint": entry.rechallenge_hint, "filters": filters, "in_progress": False},
                            gr.update(value="", language=problem.kind),
                            ""
                        )
            return "선택한 문제가 없습니다.", {}, gr.update(), ""

        load_note_btn.click(
            load_note_to_tab,
            inputs=note_choices,
            outputs=[note_question_md, state, note_code_box, note_exec_result],
        )

        note_submit_btn.click(
            on_submit,
            inputs=[state, note_code_box],
            outputs=[note_exec_result, note_choices],
            show_progress="minimal",
        )

        note_hint_btn.click(show_hint, inputs=state, outputs=note_exec_result)

    return demo


app = build_interface()

if __name__ == "__main__":
    app.launch()
