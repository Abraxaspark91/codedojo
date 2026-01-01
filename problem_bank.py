from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

# 제외할 파일 목록 (문제 파일이 아닌 JSON 파일들)
EXCLUDED_FILES = {"favorites.json"}
DEFAULT_PROBLEM_FILE = "problems.json"

# Gradio Code 컴포넌트가 지원하는 언어 목록
GRADIO_SUPPORTED_LANGUAGES = {
    "python", "c", "cpp", "markdown", "latex", "json",
    "html", "css", "javascript", "jinja2", "typescript",
    "yaml", "dockerfile", "shell", "r", "sql"
}


@dataclass
class Problem:
    pid: str
    title: str
    body: str
    difficulty: str
    kind: str  # "Python.Pyspark", "Python.Numpy", "Python", "SQL" 등
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

    @property
    def safe_language(self) -> str | None:
        """
        Gradio가 지원하지 않는 언어는 None으로 fallback하여 일반 텍스트로 표시합니다.
        """
        lang = self.language
        return lang if lang in GRADIO_SUPPORTED_LANGUAGES else None


def unique_preserve_order(items: Sequence[str]) -> List[str]:
    """순서를 유지하면서 중복을 제거합니다."""
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
                hint=item.get("hint", ""),
                schema=item.get("schema", ""),
                sample_rows=item.get("sample_rows", []),
                problem_type=item.get("problem_type", "코딩"),
            )
        )
    return problems


PROBLEM_BANK: List[Problem] = load_problem_bank()
DIFFICULTY_OPTIONS: List[str] = unique_preserve_order([p.difficulty for p in PROBLEM_BANK])


def get_available_problem_files(data_dir: Path | str = Path("data")) -> List[str]:
    """data 폴더에서 사용 가능한 문제 파일 목록을 반환합니다.

    favorites.json 등 제외 파일을 제외한 모든 .json 파일을 반환합니다.

    Args:
        data_dir: 데이터 디렉토리 경로

    Returns:
        List[str]: 문제 파일명 목록 (예: ["problems.json", "problems_advanced.json"])
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return [DEFAULT_PROBLEM_FILE]

    files = [
        f.name for f in data_path.glob("*.json")
        if f.name not in EXCLUDED_FILES
    ]

    # 기본 파일이 맨 앞에 오도록 정렬
    if DEFAULT_PROBLEM_FILE in files:
        files.remove(DEFAULT_PROBLEM_FILE)
        files = [DEFAULT_PROBLEM_FILE] + sorted(files)
    else:
        files = sorted(files)

    return files if files else [DEFAULT_PROBLEM_FILE]


def reload_problem_bank(filename: str = DEFAULT_PROBLEM_FILE) -> tuple[List[Problem], List[str], List[str]]:
    """문제 은행을 지정된 파일로 재로드합니다.

    Args:
        filename: 문제 파일명 (예: "problems.json")

    Returns:
        tuple: (PROBLEM_BANK, DIFFICULTY_OPTIONS, LANGUAGE_OPTIONS)
    """
    global PROBLEM_BANK, DIFFICULTY_OPTIONS

    file_path = Path("data") / filename
    PROBLEM_BANK = load_problem_bank(file_path)
    DIFFICULTY_OPTIONS = unique_preserve_order([p.difficulty for p in PROBLEM_BANK])

    # 언어 옵션도 함께 반환
    language_options = ["전체"] + sorted(unique_preserve_order([p.kind for p in PROBLEM_BANK]))

    return PROBLEM_BANK, DIFFICULTY_OPTIONS, language_options
