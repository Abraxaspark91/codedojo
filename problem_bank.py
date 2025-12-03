from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence


@dataclass
class Problem:
    pid: str
    title: str
    body: str
    difficulty: str
    kind: str  # "Python.Pyspark", "Python.Numpy", "Python", "SQL" 등
    expected: List[str]
    hint: str
    schema: str = ""
    sample_rows: List[str] = field(default_factory=list)
    problem_type: str = "코딩"  # "코딩", "개념문제", "빈칸채우기"

    @property
    def language(self) -> str:
        """
        kind에서 언어 부분만 추출하여 소문자로 반환합니다.
        Gradio의 gr.Code language 파라미터용으로 사용됩니다.
        '.'이 있으면 앞부분만, 없으면 전체를 반환합니다.
        예: "Python.Pyspark" -> "python", "SQL" -> "sql"
        """
        return self.kind.split('.')[0].lower()

    @property
    def library(self) -> str | None:
        """
        kind에서 라이브러리 부분을 추출합니다.
        '.'이 있으면 뒷부분을, 없으면 None을 반환합니다.
        예: "Python.Pyspark" -> "Pyspark", "SQL" -> None
        """
        parts = self.kind.split('.')
        return parts[1] if len(parts) > 1 else None


def _unique_preserve_order(items: Sequence[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def load_problem_bank(path: Path | str = Path("data/problems.json")) -> List[Problem]:
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Problem data file not found: {data_path}")

    raw = json.loads(data_path.read_text(encoding="utf-8"))
    problems: List[Problem] = []
    for item in raw:
        problems.append(
            Problem(
                pid=item["pid"],
                title=item["title"],
                body=item["body"],
                difficulty=item["difficulty"],
                kind=item["kind"],
                expected=item.get("expected", []),
                hint=item.get("hint", ""),
                schema=item.get("schema", ""),
                sample_rows=item.get("sample_rows", []),
                problem_type=item.get("problem_type", "코딩"),
            )
        )
    return problems


PROBLEM_BANK: List[Problem] = load_problem_bank()
DIFFICULTY_OPTIONS: List[str] = _unique_preserve_order([p.difficulty for p in PROBLEM_BANK])
