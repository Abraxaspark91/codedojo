import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import gradio as gr
import requests
from problem_bank import DIFFICULTY_OPTIONS, PROBLEM_BANK, Problem

NOTE_PATH = Path("data/wrong_notes.md")
NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)

LM_STUDIO_ENDPOINT = (
    Path(".env").read_text().split("LM_STUDIO_ENDPOINT=")[-1].strip()
    if Path(".env").exists() and "LM_STUDIO_ENDPOINT=" in Path(".env").read_text()
    else "http://127.0.0.1:1234/v1/chat/completions"
)

LANGUAGE_OPTIONS = ["전체", "SQL", "PySpark"]
TYPE_KEYWORDS = {
    "기본/필터": ["filter", "where", "기본"],
    "조인": ["join", "조인"],
    "집계": ["group by", "sum", "count", "agg", "average", "avg"],
    "윈도우": ["window", "lag", "lead", "rank", "row_number", "over", "rolling"],
    "피벗": ["pivot"],
}


def infer_problem_type(problem: Problem) -> str:
    corpus = f"{problem.pid} {problem.title} {problem.body} {' '.join(problem.expected)}".lower()
    for label, keywords in TYPE_KEYWORDS.items():
        if any(key.lower() in corpus for key in keywords):
            return label
    return "일반"


PROBLEM_TYPE_OPTIONS = ["전체", *sorted({infer_problem_type(p) for p in PROBLEM_BANK})]


def display_language(kind: str) -> str:
    return "PySpark" if kind.lower() == "pyspark" else "SQL"

@dataclass
class Attempt:
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


def ensure_note_file() -> None:
    if not NOTE_PATH.exists():
        NOTE_PATH.write_text("# 오답노트 기록\n\n")


def serialize_attempt(attempt: Attempt) -> str:
    meta = json.dumps(asdict(attempt), ensure_ascii=False, indent=2)
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
    ensure_note_file()
    text = NOTE_PATH.read_text(encoding="utf-8")
    entries: List[Attempt] = []
    for block in text.split("```meta"):
        if "```" not in block:
            continue
        meta_str = block.split("```", 1)[0].strip()
        if not meta_str:
            continue
        try:
            data = json.loads(meta_str)
            entries.append(Attempt(**data))
        except json.JSONDecodeError:
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


def call_llm(system_prompt: str, user_prompt: str) -> str:
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
        response = requests.post(LM_STUDIO_ENDPOINT, json=payload, timeout=120)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        return (
            "LLM 서버에 연결하지 못했습니다.\n"
            f"로컬 엔드포인트({LM_STUDIO_ENDPOINT})를 확인하세요.\n"
            f"대신 휴리스틱 피드백을 제공합니다. ({exc})"
        )


def heuristics_score(code: str, expected: List[str]) -> Tuple[int, str]:
    upper = code.upper()
    matched = sum(1 for key in expected if key.upper() in upper)
    score = int(60 + (40 * matched / max(len(expected), 1)))
    run_result = (
        "핵심 키워드를 모두 포함했습니다." if matched == len(expected) else "일부 키워드가 누락되었습니다."
    )
    return score, run_result


def evaluate_submission(problem: Problem, code: str) -> Tuple[int, str]:
    score, run_result = heuristics_score(code, problem.expected)
    status = "통과" if score >= 80 else "재도전"
    detail = f"실행 결과 추정: {run_result} (예상 점수: {score}점, 상태: {status})"
    return score, detail


def build_feedback(problem: Problem, code: str, score: int, run_detail: str) -> Tuple[str, str, str]:
    system_prompt = (
        "당신은 SQL, PySpark, Pseudocode, Technical Decomp문제의 채점을 돕는 조교입니다. 코드 실행 결과를 반영해 짧게 평가하세요. "
        "정답 여부, 놓친 부분, 효율/논리 개선, 작성자의 의도 추정을 포함합니다."
    )
    user_prompt = (
        f"문제: {problem.body}\n코드:```{problem.kind}\n{code}\n```\n"
        f"실행 결과 요약: {run_detail}\n"
        "- 1) 정오 판단과 점수 보정 제안\n- 2) 보완 포인트\n- 3) 더 효율적이거나 간결한 방법\n- 4) 작성자의 의도 추측"
    )
    llm_reply = call_llm(system_prompt, user_prompt)
    if "휴리스틱" in llm_reply:
        improvement = problem.hint
        reasoning = "문제에서 요구한 키워드 기반으로 자동 피드백을 생성했습니다."
    else:
        improvement = "효율성/가독성 개선 제안을 참고하세요."
        reasoning = "작성 의도 추정은 피드백 섹션을 확인하세요."
    return llm_reply, improvement, reasoning


def append_attempt(problem: Problem, code: str, score: int, feedback: str, run_detail: str, improvement: str, reasoning: str) -> None:
    ensure_note_file()
    attempt = Attempt(
        pid=problem.pid,
        title=problem.title,
        difficulty=problem.difficulty,
        score=score,
        status="통과" if score >= 80 else "재도전",
        submitted=run_detail,
        feedback=feedback,
        improvement=improvement,
        reasoning=reasoning,
        question=problem.body,
        code=code,
        kind=problem.kind,
        timestamp=datetime.now().isoformat(timespec="seconds"),
        rechallenge_hint=run_detail,
    )
    NOTE_PATH.write_text(NOTE_PATH.read_text(encoding="utf-8") + serialize_attempt(attempt), encoding="utf-8")


def refresh_note_choices() -> Tuple[List[str], List[str]]:
    entries = failed_attempts(load_attempts())
    labels = [f"{a.pid} | {a.score}점 | {a.title}" for a in entries]
    values = [a.pid for a in entries]
    return labels, values


def load_from_notes(selected_pid: str) -> Tuple[str, Dict, Dict[str, str]]:
    entries = failed_attempts(load_attempts())
    for entry in entries:
        if entry.pid == selected_pid:
            problem = next((p for p in PROBLEM_BANK if p.pid == entry.pid), None)
            if problem:
                filters = normalize_filters(
                    problem.difficulty, display_language(problem.kind), infer_problem_type(problem)
                )
                question = render_question(problem, True, entry.rechallenge_hint, filters)
                return (
                    question,
                    {
                        "problem": problem,
                        "rechallenge": True,
                        "hint": entry.rechallenge_hint,
                        "filters": filters,
                        "applied_filters": filters,
                    },
                    filters,
                )
    return "선택한 문제가 없습니다.", {}, normalize_filters(None, None, None)


def on_new_problem(difficulty: str, language: str, problem_type: str) -> Tuple[str, Dict, str, Dict[str, str]]:
    requested_filters = normalize_filters(difficulty, language, problem_type)
    problem, rechallenge, hint, applied_filters = pick_problem(difficulty, language, problem_type)
    question = render_question(problem, rechallenge, hint, requested_filters, applied_filters)
    state = {
        "problem": problem,
        "rechallenge": rechallenge,
        "hint": hint,
        "filters": requested_filters,
        "applied_filters": applied_filters,
    }
    return question, state, problem.kind, requested_filters


def on_new_problem(difficulty: str) -> Tuple[str, Dict, gr.Update, str, str, str, str]:
    problem, rechallenge, hint = pick_problem(difficulty)
    return reset_outputs(problem, rechallenge, hint)


def on_submit(
    state: Dict, code: str, progress=gr.Progress()
) -> Generator[Tuple[str, str, str, str, Dict, gr.Update], None, None]:
    state = ensure_state(state)

    if not state or "problem" not in state:
        state["in_progress"] = False
        yield "문제가 선택되지 않았습니다.", "", "", "", state, gr.update(interactive=True)
        return

    if state.get("in_progress"):
        message = "채점이 진행 중입니다. 잠시만 기다려주세요."
        yield (
            message,
            state.get("last_run_detail", ""),
            state.get("last_feedback", ""),
            state.get("last_improvement", ""),
            state,
            gr.update(interactive=False),
        )
        return

    state["in_progress"] = True
    problem: Problem = state["problem"]

    yield "채점 중입니다...", "", "", "", state, gr.update(interactive=False)

    progress(0, desc="채점 중")
    score, run_detail = evaluate_submission(problem, code)
    progress(0.33, desc="채점 중")

    feedback, improvement, reasoning = build_feedback(problem, code, score, run_detail)
    progress(0.66, desc="채점 중")

    append_attempt(problem, code, score, feedback, run_detail, improvement, reasoning)
    progress(1.0, desc="채점 완료")

    header = f"점수: {score}점 ({'통과' if score >= 80 else '재도전'})"
    state.update(
        {
            "in_progress": False,
            "last_run_detail": run_detail,
            "last_feedback": feedback,
            "last_improvement": improvement,
        }
    )
    yield header, run_detail, feedback, improvement, state, gr.update(interactive=True)


def show_hint(state: Dict) -> str:
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다."
    problem: Problem = state["problem"]
    return f"문법 힌트: {problem.hint}"


def build_interface() -> gr.Blocks:
    with gr.Blocks(title="SQL & PySpark 연습") as demo:
        gr.Markdown("## SQL & PySpark 연습 스테이션 (LM Studio)")
        with gr.Row():
            difficulty = gr.Dropdown(DIFFICULTY_OPTIONS, value=DIFFICULTY_OPTIONS[0], label="난이도")
            language = gr.Dropdown(LANGUAGE_OPTIONS, value=LANGUAGE_OPTIONS[0], label="언어")
            problem_type = gr.Dropdown(PROBLEM_TYPE_OPTIONS, value=PROBLEM_TYPE_OPTIONS[0], label="문제 유형")
        question_md = gr.Markdown("새 문제 버튼을 눌러 시작하세요.")
        code_box = gr.Code(label="코드 에디터", language="sql", lines=16)
        state = gr.State({})
        filter_state = gr.State(normalize_filters(DIFFICULTY_OPTIONS[0], LANGUAGE_OPTIONS[0], PROBLEM_TYPE_OPTIONS[0]))

        with gr.Row():
            new_btn = gr.Button("새 문제 출제")
            submit_btn = gr.Button("제출", variant="primary")
            hint_btn = gr.Button("문법 힌트")

        exec_result = gr.Markdown(label="실행 결과")
        feedback_md = gr.Markdown(label="LLM 피드백")
        improvement_md = gr.Markdown(label="보완점")
        score_md = gr.Markdown(label="점수")

        with gr.Accordion("오답노트", open=False):
            refresh_btn = gr.Button("오답노트 불러오기")
            note_choices = gr.Dropdown(choices=[], label="재도전 문제 선택")
            load_note_btn = gr.Button("선택 문제 다시 풀기")

        new_btn.click(
            on_new_problem,
            inputs=[difficulty, language, problem_type],
            outputs=[question_md, state, code_box, filter_state],
        )
        submit_btn.click(
            on_submit, inputs=[state, code_box], outputs=[score_md, exec_result, feedback_md, improvement_md]
        )
        hint_btn.click(show_hint, inputs=state, outputs=feedback_md)

        def sync_filters(diff: str, lang: str, ptype: str):
            return normalize_filters(diff, lang, ptype)

        for dropdown in (difficulty, language, problem_type):
            dropdown.change(sync_filters, inputs=[difficulty, language, problem_type], outputs=filter_state)

        def refresh_notes():
            labels, values = refresh_note_choices()
            choices = list(zip(labels, values))
            return gr.update(choices=choices, value=None), "재도전할 문제를 선택하세요."

        refresh_btn.click(refresh_notes, outputs=[note_choices, feedback_md])

        def load_selected(pid, current_filters):
            if not pid:
                return gr.update(), {}, "", current_filters
            question, new_state, filters = load_from_notes(pid)
            language_choice = new_state.get("problem").kind if new_state else "sql"
            return question, new_state, language_choice, filters

        load_note_btn.click(
            load_selected, inputs=[note_choices, filter_state], outputs=[question_md, state, code_box, filter_state]
        )

    return demo


app = build_interface()

if __name__ == "__main__":
    app.launch()
