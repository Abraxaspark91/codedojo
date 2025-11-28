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

CUSTOM_THEME = gr.themes.Default(primary_hue="emerald", neutral_hue="slate")
CUSTOM_CSS = """
body[data-user-theme="dark"] {
    background: #0f172a;
    color: #e2e8f0;
}

body[data-user-theme="light"] {
    background: #ffffff;
    color: #0f172a;
}

:root[data-user-theme="dark"] {
    color-scheme: dark;
    --shadow-drop: 0 10px 30px rgba(15, 23, 42, 0.5);
    --background-fill-primary: #0f172a;
    --background-fill-secondary: #1e293b;
    --background-fill-tertiary: #111827;
    --color-text: #e2e8f0;
}

[data-user-theme="dark"] .gradio-container,
[data-user-theme="dark"] .gr-box,
[data-user-theme="dark"] .gr-panel,
[data-user-theme="dark"] textarea,
[data-user-theme="dark"] pre,
[data-user-theme="dark"] code,
[data-user-theme="dark"] .prose {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
}

[data-user-theme="dark"] .gr-button-primary {
    background: #22c55e !important;
    color: #0f172a !important;
}

[data-user-theme="dark"] .gr-button-secondary,
[data-user-theme="dark"] .gr-button-lg,
[data-user-theme="dark"] .gr-button-sm {
    background: #1e293b !important;
    color: #e2e8f0 !important;
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
        kind: 프로그래밍 언어 (sql/python)
        timestamp: ISO 형식의 제출 시간
        rechallenge_hint: 재도전 시 참고할 힌트
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


def infer_problem_type(problem: Problem) -> str:
    lower_expected = [kw.lower() for kw in problem.expected]
    if any(key in lower_expected for key in ["join", "union", "merge"]):
        return "조인/조합"
    if any(key in lower_expected for key in ["group by", "sum", "avg", "count", "having"]):
        return "집계"
    if any(key in lower_expected for key in ["over", "rank", "dense_rank", "window"]):
        return "윈도우"
    return "기본"


def ensure_note_file() -> None:
    if not NOTE_PATH.exists():
        NOTE_PATH.write_text("# 오답노트 기록\n\n")


def serialize_attempt(attempt: Attempt) -> str:
    """Attempt를 마크다운 형식으로 변환합니다.
    
    JSON을 명시적으로 이스케이프하고 검증하여 저장합니다.
    """
    # JSON 직렬화 시 모든 문자를 명시적으로 처리
    meta = json.dumps(
        asdict(attempt), 
        ensure_ascii=False,  # 한글 유지
        indent=2,
        separators=(',', ': ')  # 표준 JSON 포맷
    )
    
    # JSON이 유효한지 검증
    try:
        json.loads(meta)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 직렬화 오류: {e}\n{meta[:200]}...")
    
    return (
        f"\n## 문제 ID: {attempt.pid}\n"
        f"```meta\n{meta}\n```\n"
        f"### 문제\n{attempt.question}\n\n"
        f"### 제출 코드\n```{attempt.kind}\n{attempt.code}\n```\n\n"
        f"### 피드백\n{attempt.feedback}\n\n"
        f"### 보완점\n{attempt.improvement}\n\n"
        f"### 해설\n{attempt.reasoning}\n\n"
        "---\n"
    )


def load_attempts() -> List[Attempt]:
    """오답노트 파일에서 모든 Attempt를 로드합니다.
    
    파싱 실패한 항목은 무시하고 로그를 남깁니다.
    """
    ensure_note_file()
    text = NOTE_PATH.read_text(encoding="utf-8")
    entries: List[Attempt] = []
    
    # ```meta 블록을 분리
    blocks = text.split("```meta")
    
    for block_idx, block in enumerate(blocks):
        # ``` 마크가 없으면 스킵 (첫 번째 헤더 블록)
        if "```" not in block:
            continue
        
        # ``` 사이의 JSON 추출
        meta_str = block.split("```", 1)[0].strip()
        
        if not meta_str:
            continue
        
        try:
            # JSON 파싱
            data = json.loads(meta_str)
            
            # Attempt 객체 생성
            entry = Attempt(**data)
            entries.append(entry)
            
        except json.JSONDecodeError as e:
            # JSON 파싱 오류: 해당 블록 무시, 계속 진행
            print(f"[경고] 블록 {block_idx}의 JSON 파싱 실패: {str(e)[:100]}", file=__import__('sys').stderr)
            continue
            
        except TypeError as e:
            # Attempt 필드 부족: 해당 블록 무시, 계속 진행
            print(f"[경고] 블록 {block_idx}의 Attempt 생성 실패: {str(e)[:100]}", file=__import__('sys').stderr)
            continue
            
        except Exception as e:
            # 예상 외의 오류
            print(f"[경고] 블록 {block_idx}의 처리 오류: {str(e)[:100]}", file=__import__('sys').stderr)
            continue
    
    return entries


def failed_attempts(entries: List[Attempt]) -> List[Attempt]:
    return [a for a in entries if a.score < 80]


def matches_filters(problem: Problem, difficulty: Optional[str], language: Optional[str], problem_type: Optional[str]) -> bool:
    language_match = (not language or language == "전체") or problem.kind.lower() == language.lower()
    difficulty_match = (not difficulty or difficulty == "전체") or problem.difficulty == difficulty
    inferred_type = infer_problem_type(problem)
    type_match = (not problem_type or problem_type == "전체") or inferred_type == problem_type
    return difficulty_match and language_match and type_match


def normalize_filters(
    difficulty: Optional[str], language: Optional[str], problem_type: Optional[str]
) -> Dict[str, str]:
    return {
        "difficulty": difficulty or "전체",
        "language": language or "전체",
        "problem_type": problem_type or "전체",
    }


def pick_problem(
    difficulty: str, language: str, problem_type: str
) -> Tuple[Problem, bool, str, Dict[str, str]]:
    entries = load_attempts()
    failed = failed_attempts(entries)
    rechallenge = False
    hint = ""
    target_filters = normalize_filters(difficulty, language, problem_type)
    filter_priority = [
        (difficulty, language, problem_type),
        (difficulty, language, None),
        (difficulty, None, problem_type),
        (difficulty, None, None),
        (None, language, problem_type),
        (None, language, None),
        (None, None, problem_type),
        (None, None, None),
    ]

    def choose_candidate(pool: List[Tuple[Problem, str]]) -> Tuple[Problem, Dict[str, str]]:
        for diff_opt, lang_opt, type_opt in filter_priority:
            candidates = [
                (prob, attempt_hint)
                for prob, attempt_hint in pool
                if matches_filters(prob, diff_opt, lang_opt, type_opt)
            ]
            if candidates:
                prob, attempt_hint = random.choice(candidates)
                return prob, normalize_filters(diff_opt, lang_opt, type_opt) | {"hint": attempt_hint}
        prob, attempt_hint = random.choice(pool)
        return prob, normalize_filters(None, None, None) | {"hint": attempt_hint}

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
    banner = "재도전" if rechallenge else "신규 문제"
    hint_line = f"\n> 🔁 재도전 힌트: {rechallenge_hint}\n" if rechallenge_hint else ""
    selection_line = (
        f"- 선택 필터: 난이도 {requested_filters.get('difficulty', '전체')}, "
        f"언어 {requested_filters.get('language', '전체')}, "
        f"유형 {requested_filters.get('problem_type', '전체')}"
    )
    applied = applied_filters or requested_filters
    applied_line = ""
    if applied != requested_filters:
        applied_line = (
            f"\n- 적용 필터: 난이도 {applied.get('difficulty', '전체')}, "
            f"언어 {applied.get('language', '전체')}, "
            f"유형 {applied.get('problem_type', '전체')}"
        )
    return (
        f"### [{banner}] {problem.title}\n"
        f"- 난이도: {problem.difficulty}\n- 언어: {problem.kind}\n- 문제 유형: {infer_problem_type(problem)}\n"
        f"{selection_line}{applied_line}\n\n{problem.body}{hint_line}"
    )


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
    FAVORITES_PATH.write_text(json.dumps(list(deduped.values()), ensure_ascii=False, indent=2), encoding="utf-8")


def favorite_button_label(pid: str) -> str:
    favorites = load_favorites()
    return "⭐ 즐겨찾기 해제" if any(fav.get("pid") == pid for fav in favorites) else "☆ 즐겨찾기 추가"


def refresh_favorite_choices() -> Tuple[List[str], List[str]]:
    favorites = load_favorites()
    labels = [
        f"{fav['pid']} | {fav.get('difficulty','')} | {fav.get('kind','')} | {fav.get('title','')}"
        for fav in favorites
    ]
    values = [fav["pid"] for fav in favorites]
    return labels, values


def favorite_status_text(pid: str) -> str:
    return (
        "⭐ 즐겨찾기에 저장된 문제입니다." if favorite_button_label(pid).startswith("⭐") else "☆ 즐겨찾기에 추가할 수 있습니다."
    )


def call_llm(system_prompt: str, user_prompt: str, endpoint: str = LM_STUDIO_ENDPOINT) -> str:
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
    except Exception as exc:  # noqa: BLE001
        return (
            "LLM 서버에 연결하지 못했습니다.\n"
            f"로컬 엔드포인트({endpoint})를 확인하세요.\n"
            f"대신 휴리스틱 피드백을 제공합니다. ({exc})"
        )


def heuristics_score(code: str, expected: List[str]) -> Tuple[int, str]:
    upper = code.upper()
    matched = sum(1 for key in expected if key.upper() in upper)
    # 모든 키워드를 포함할 때만 80점 이상
    if matched == len(expected):
        score = 100
        run_result = "핵심 키워드를 모두 포함했습니다."
    elif matched >= len(expected) * 0.5:
        score = 70 + matched * 5
        run_result = f"일부 키워드가 누락되었습니다. ({matched}/{len(expected)}개 포함)"
    else:
        score = 40 + matched * 10
        run_result = f"대부분의 키워드가 누락되었습니다. ({matched}/{len(expected)}개 포함)"
    return min(score, 100), run_result


def evaluate_submission(problem: Problem, code: str) -> Tuple[int, str]:
    score, run_result = heuristics_score(code, problem.expected)
    status = "통과" if score >= 80 else "재도전"
    detail = f"실행 결과 추정: {run_result} (예상 점수: {score}점, 상태: {status})"
    return score, detail


def build_feedback(
    problem: Problem, code: str, score: int, run_detail: str, endpoint: str
) -> Tuple[str, str, str]:
    system_prompt = (
        "당신은 SQL, PySpark, Pseudocode, Technical Decomp문제의 채점을 돕는 조교입니다. 코드 실행 결과를 반영해 짧게 평가하세요. "
        "정답 여부, 놓친 부분, 효율/논리 개선, 작성자의 의도 추정을 포함합니다."
    )
    user_prompt = (
        f"문제: {problem.body}\n코드:```{problem.kind}\n{code}\n```\n"
        f"실행 결과 요약: {run_detail}\n"
        "- 1) 정오 판단과 점수 보정 제안\n- 2) 보완 포인트\n- 3) 더 효율적이거나 간결한 방법\n- 4) 작성자의 의도 추측"
    )
    llm_reply = call_llm(system_prompt, user_prompt, endpoint)
    if "휴리스틱" in llm_reply:
        improvement = problem.hint
        reasoning = "문제에서 요구한 키워드 기반으로 자동 피드백을 생성했습니다."
    else:
        improvement = "효율성/가독성 개선 제안을 참고하세요."
        reasoning = "작성 의도 추정은 피드백 섹션을 확인하세요."
    return llm_reply, improvement, reasoning


def append_attempt(problem: Problem, code: str, score: int, feedback: str, run_detail: str, improvement: str, reasoning: str) -> None:
    """채점 결과를 오답노트에 추가합니다.
    
    JSON 검증을 통해 손상된 데이터 저장을 방지합니다.
    """
    ensure_note_file()
    attempt = Attempt(
        pid=problem.pid,
        title=problem.title,
        difficulty=problem.difficulty,
        score=score,
        status="통과" if score >= 80 else "재도전",
        submitted=code,
        feedback=feedback,
        improvement=improvement,
        reasoning=reasoning,
        question=problem.body,
        code=code,
        kind=problem.kind,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        rechallenge_hint=run_detail,
    )
    
    try:
        serialized = serialize_attempt(attempt)
        NOTE_PATH.write_text(NOTE_PATH.read_text(encoding="utf-8") + serialized, encoding="utf-8")
    except ValueError as e:
        # JSON 직렬화 실패 시 에러 로그만 남기고 계속
        print(f"[오류] Attempt 저장 실패: {e}", file=__import__('sys').stderr)
        raise


def refresh_note_choices() -> Tuple[List[str], List[str]]:
    entries = failed_attempts(load_attempts())
    labels = [f"{a.pid} | {a.score}점 | {a.title}" for a in entries]
    values = [a.pid for a in entries]
    return labels, values


def load_from_notes(selected_pid: str) -> Tuple[str, Dict, gr.update, str, str]:
    entries = failed_attempts(load_attempts())
    for entry in entries:
        if entry.pid == selected_pid:
            problem = next((p for p in PROBLEM_BANK if p.pid == entry.pid), None)
            if problem:
                filters = normalize_filters(None, None, None)
                question = render_question(problem, True, entry.rechallenge_hint, filters)
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


def on_new_problem(difficulty: str, language: str, problem_type: str) -> Tuple[str, Dict, gr.update, str, str, str]:
    filters = normalize_filters(difficulty, language, problem_type)
    problem, rechallenge, hint, applied_filters = pick_problem(difficulty, language, problem_type)
    question = render_question(problem, rechallenge, hint, filters, applied_filters)
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
    return (
        question,
        state,
        gr.update(value="", language=problem.kind),
        favorite_button_label(problem.pid),
        favorite_status_text(problem.pid),
        "",  # exec_result 초기화
    )


def on_submit(state: Dict, code: str, progress=gr.Progress()) -> str:
    state = ensure_state(state)
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다."

    if state.get("in_progress"):
        return "채점이 진행 중입니다. 잠시만 기다려주세요."

    state["in_progress"] = True
    problem: Problem = state["problem"]

    progress(0.3, desc="코드 평가 중")
    score, run_detail = evaluate_submission(problem, code)

    progress(0.7, desc="LLM 피드백 생성 중")
    feedback, improvement, reasoning = build_feedback(
        problem, code, score, run_detail, LM_STUDIO_ENDPOINT
    )

    progress(1.0, desc="결과 저장 중")
    append_attempt(problem, code, score, feedback, run_detail, improvement, reasoning)

    header = f"점수: {score}점 ({'통과' if score >= 80 else '재도전'})"
    state.update({"in_progress": False})
    
    # 통합 결과를 마크다운으로 반환
    combined = (
        f"{header}\n\n"
        f"### 실행 결과\n{run_detail}\n\n"
        f"### LLM 피드백\n{feedback}\n\n"
        f"### 보완점\n{improvement}"
    )
    return combined


def show_hint(state: Dict) -> str:
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다."
    problem: Problem = state["problem"]
    return f"문법 힌트: {problem.hint}"


def toggle_favorite(state: Dict) -> Tuple[gr.update, str, gr.update]:
    if not state or "problem" not in state:
        labels, values = refresh_favorite_choices()
        return gr.update(), "문제가 선택되지 않았습니다.", gr.update(choices=list(zip(labels, values)), value=None)

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
    language_options = ["전체"] + unique_preserve_order([p.kind for p in PROBLEM_BANK])
    problem_type_options = ["전체"] + unique_preserve_order(
        [infer_problem_type(p) for p in PROBLEM_BANK]
    )
    # Create Blocks with a fallback for gradio versions that don't accept `theme`/`css` kwargs.
    try:
        demo = gr.Blocks(title="SQL & PySpark 연습", theme=CUSTOM_THEME, css=CUSTOM_CSS)
    except TypeError:
        demo = gr.Blocks(title="SQL & PySpark 연습")

    with demo:
        gr.Markdown("## SQL & PySpark 연습 스테이션 (LM Studio)")
        with gr.Row():
            difficulty = gr.Dropdown(DIFFICULTY_OPTIONS, value=DIFFICULTY_OPTIONS[0], label="난이도")
            language = gr.Dropdown(language_options, value=language_options[0], label="언어")
            problem_type = gr.Dropdown(problem_type_options, value=problem_type_options[0], label="문제 유형")

        question_md = gr.Markdown("새 문제 버튼을 눌러 시작하세요.")
        favorite_status_md = gr.Markdown("즐겨찾기 상태를 여기에서 확인하세요.")
        code_box = gr.Code(label="코드 에디터", language="sql", lines=16)
        state = gr.State({})

        with gr.Row():
            new_btn = gr.Button("새 문제 출제")
            submit_btn = gr.Button("제출", variant="primary")
            hint_btn = gr.Button("문법 힌트")
            favorite_btn = gr.Button("☆ 즐겨찾기 추가")

        exec_result = gr.Markdown(label="채점 결과")
        score_md = gr.Markdown(label="점수")

        with gr.Accordion("즐겨찾기", open=False):
            fav_refresh_btn = gr.Button("즐겨찾기 불러오기")
            # 초기값 설정
            fav_labels, fav_values = refresh_favorite_choices()
            fav_choices = list(zip(fav_labels, fav_values)) if fav_labels else []
            favorite_choices = gr.Dropdown(choices=fav_choices, label="즐겨찾기 문제 선택")
            load_fav_btn = gr.Button("선택 문제 열기")

        with gr.Accordion("오답노트", open=False):
            refresh_btn = gr.Button("오답노트 불러오기")
            # 초기값 설정
            note_labels, note_values = refresh_note_choices()
            note_choice = list(zip(note_labels, note_values)) if note_labels else []
            note_choices = gr.Dropdown(choices=note_choice, label="재도전 문제 선택")
            load_note_btn = gr.Button("선택 문제 다시 풀기")

        new_btn.click(
            on_new_problem,
            inputs=[difficulty, language, problem_type],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result],
        )
        # Dropdown change 이벤트 추가: 필터 변경 시 자동으로 새 문제 로드
        difficulty.change(
            on_new_problem,
            inputs=[difficulty, language, problem_type],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result],
        )
        language.change(
            on_new_problem,
            inputs=[difficulty, language, problem_type],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result],
        )
        problem_type.change(
            on_new_problem,
            inputs=[difficulty, language, problem_type],
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md, exec_result],
        )
        submit_btn.click(
            on_submit,
            inputs=[state, code_box],
            outputs=[exec_result],
            show_progress="minimal",
        )
        hint_btn.click(show_hint, inputs=state, outputs=exec_result)
        favorite_btn.click(
            toggle_favorite,
            inputs=state,
            outputs=[favorite_btn, favorite_status_md, favorite_choices],
        )

        def refresh_notes():
            labels, values = refresh_note_choices()
            choices = list(zip(labels, values))
            return gr.update(choices=choices, value=None), ""

        refresh_btn.click(refresh_notes, outputs=[note_choices, exec_result])

        def load_selected(pid):
            if not pid:
                return gr.update(), {}, gr.update(), favorite_button_label(""), ""
            return load_from_notes(pid)

        load_note_btn.click(
            load_selected,
            inputs=note_choices,
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md],
        )

        def refresh_favorites():
            labels, values = refresh_favorite_choices()
            return gr.update(choices=list(zip(labels, values)), value=None)

        fav_refresh_btn.click(refresh_favorites, outputs=favorite_choices)

        def load_favorite_selection(pid):
            if not pid:
                return gr.update(), {}, gr.update(), favorite_button_label(""), ""
            return load_favorite_problem(pid)

        load_fav_btn.click(
            load_favorite_selection,
            inputs=favorite_choices,
            outputs=[question_md, state, code_box, favorite_btn, favorite_status_md],
        )

    return demo


app = build_interface()

if __name__ == "__main__":
    app.launch()
