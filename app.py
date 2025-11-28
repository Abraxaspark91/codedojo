import json
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

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


def pick_problem(difficulty: str) -> Tuple[Problem, bool, str]:
    entries = load_attempts()
    failed = failed_attempts(entries)
    rechallenge = False
    hint = ""
    if failed and random.random() < 0.3:
        target = random.choice(failed)
        problem = next((p for p in PROBLEM_BANK if p.pid == target.pid), None)
        if problem:
            rechallenge = True
            hint = target.rechallenge_hint or "지난 시도에서 놓친 부분을 점검해 보세요."
            return problem, rechallenge, hint
    candidates = [p for p in PROBLEM_BANK if p.difficulty == difficulty]
    problem = random.choice(candidates) if candidates else random.choice(PROBLEM_BANK)
    return problem, rechallenge, hint


def render_question(problem: Problem, rechallenge: bool, rechallenge_hint: str) -> str:
    banner = "재도전" if rechallenge else "신규 문제"
    hint_line = f"\n> 🔁 재도전 힌트: {rechallenge_hint}\n" if rechallenge_hint else ""
    sections = [
        f"### [{banner}] {problem.title}",
        f"- 난이도: {problem.difficulty}",
        f"- 유형: {problem.kind}",
        "",
        problem.body,
    ]

    if problem.schema:
        sections.extend(["", "**스키마**", "```", problem.schema, "```"])

    if problem.sample_rows:
        sections.extend(["", "**샘플 데이터**", "```", *problem.sample_rows, "```"])

    if hint_line:
        sections.append(hint_line)

    return "\n".join(sections)


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


def load_from_notes(selected_pid: str) -> Tuple[str, Dict]:
    entries = failed_attempts(load_attempts())
    for entry in entries:
        if entry.pid == selected_pid:
            problem = next((p for p in PROBLEM_BANK if p.pid == entry.pid), None)
            if problem:
                question = render_question(problem, True, entry.rechallenge_hint)
                return question, {"problem": problem, "rechallenge": True, "hint": entry.rechallenge_hint}
    return "선택한 문제가 없습니다.", {}


def on_new_problem(difficulty: str) -> Tuple[str, Dict, str]:
    problem, rechallenge, hint = pick_problem(difficulty)
    question = render_question(problem, rechallenge, hint)
    return question, {"problem": problem, "rechallenge": rechallenge, "hint": hint}, problem.kind


def on_submit(state: Dict, code: str, progress=gr.Progress()) -> Tuple[str, str, str, str]:
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다.", "", "", ""
    problem: Problem = state["problem"]
    
    progress(0, desc="채점 중")
    score, run_detail = evaluate_submission(problem, code)
    progress(0.33, desc="채점 중")
    
    feedback, improvement, reasoning = build_feedback(problem, code, score, run_detail)
    progress(0.66, desc="채점 중")
    
    append_attempt(problem, code, score, feedback, run_detail, improvement, reasoning)
    progress(1.0, desc="채점 완료")
    
    header = f"점수: {score}점 ({'통과' if score >= 80 else '재도전'})"
    return header, run_detail, feedback, improvement


def show_hint(state: Dict) -> str:
    if not state or "problem" not in state:
        return "문제가 선택되지 않았습니다."
    problem: Problem = state["problem"]
    return f"문법 힌트: {problem.hint}"


def build_interface() -> gr.Blocks:
    with gr.Blocks(title="SQL & PySpark 연습") as demo:
        gr.Markdown("## SQL & PySpark 연습 스테이션 (LM Studio)")
        difficulty = gr.Dropdown(DIFFICULTY_OPTIONS, value=DIFFICULTY_OPTIONS[0], label="난이도")
        question_md = gr.Markdown("새 문제 버튼을 눌러 시작하세요.")
        code_box = gr.Code(label="코드 에디터", language="sql", lines=16)
        state = gr.State({})

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

        new_btn.click(on_new_problem, inputs=difficulty, outputs=[question_md, state, code_box])
        submit_btn.click(on_submit, inputs=[state, code_box], outputs=[score_md, exec_result, feedback_md, improvement_md])
        hint_btn.click(show_hint, inputs=state, outputs=feedback_md)

        def refresh_notes():
            labels, values = refresh_note_choices()
            choices = list(zip(labels, values))
            return gr.update(choices=choices, value=None), "재도전할 문제를 선택하세요."

        refresh_btn.click(refresh_notes, outputs=[note_choices, feedback_md])

        def load_selected(pid):
            if not pid:
                return gr.update(), {}, ""
            question, new_state = load_from_notes(pid)
            language = new_state.get("problem").kind if new_state else "sql"
            return question, new_state, language

        load_note_btn.click(load_selected, inputs=note_choices, outputs=[question_md, state, code_box])

    return demo


app = build_interface()

if __name__ == "__main__":
    app.launch()
