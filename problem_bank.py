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
    kind: str  # "sql" or "pyspark"
    expected: List[str]
    hint: str
    schema: str = ""
    sample_rows: List[str] = field(default_factory=list)


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
            )
        )
    return problems


PROBLEM_BANK: List[Problem] = load_problem_bank()
DIFFICULTY_OPTIONS: List[str] = _unique_preserve_order([p.difficulty for p in PROBLEM_BANK])
