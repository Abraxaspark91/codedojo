#!/usr/bin/env python3
"""
변경사항 테스트 스크립트
"""
from pathlib import Path
import sys

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from problem_bank import PROBLEM_BANK, Problem
from collections import defaultdict

def test_problem_properties():
    """Problem 클래스의 language와 library property 테스트"""
    print("=" * 60)
    print("🧪 Problem 클래스 속성 테스트")
    print("=" * 60)

    test_cases = [
        ("Python.Pyspark", "python", "Pyspark"),
        ("Python.Numpy", "python", "Numpy"),
        ("Python", "python", None),
        ("SQL", "sql", None),
    ]

    all_passed = True
    for kind, expected_lang, expected_lib in test_cases:
        # 임시 Problem 객체 생성
        p = Problem(
            pid="test",
            title="Test",
            body="Test",
            difficulty="Lv0",
            kind=kind,
            expected=[],
            hint=""
        )

        lang_match = p.language == expected_lang
        lib_match = p.library == expected_lib

        status = "✅" if (lang_match and lib_match) else "❌"
        print(f"{status} kind='{kind}' -> language='{p.language}', library='{p.library}'")

        if not (lang_match and lib_match):
            print(f"   Expected: language='{expected_lang}', library='{expected_lib}'")
            all_passed = False

    return all_passed


def test_problem_bank_loading():
    """PROBLEM_BANK 로딩 및 통계 테스트"""
    print("\n" + "=" * 60)
    print("📊 PROBLEM_BANK 통계")
    print("=" * 60)

    stats = defaultdict(lambda: {"language": None, "library": None, "count": 0})

    for p in PROBLEM_BANK:
        key = p.kind
        stats[key]["language"] = p.language
        stats[key]["library"] = p.library
        stats[key]["count"] += 1

    print(f"\n총 문제 수: {len(PROBLEM_BANK)}개\n")
    print(f"{'Kind':<20} {'Language':<10} {'Library':<15} {'Count':>5}")
    print("-" * 60)

    for kind in sorted(stats.keys()):
        info = stats[kind]
        lib = info['library'] or "-"
        print(f"{kind:<20} {info['language']:<10} {lib:<15} {info['count']:>5}개")

    return True


def test_filter_logic():
    """필터 로직 테스트 (간단 버전)"""
    print("\n" + "=" * 60)
    print("🔍 필터 로직 테스트")
    print("=" * 60)

    # Python.Pyspark 문제만 필터링
    pyspark_problems = [p for p in PROBLEM_BANK if p.kind == "Python.Pyspark"]
    print(f"✅ Python.Pyspark 문제: {len(pyspark_problems)}개")

    # Python 계열 모든 문제 필터링
    python_problems = [p for p in PROBLEM_BANK if p.language == "python"]
    print(f"✅ Python 계열 문제: {len(python_problems)}개")

    # SQL 문제 필터링
    sql_problems = [p for p in PROBLEM_BANK if p.language == "sql"]
    print(f"✅ SQL 문제: {len(sql_problems)}개")

    return True


def test_render_display():
    """문제 표시 포맷 테스트"""
    print("\n" + "=" * 60)
    print("📝 문제 표시 포맷 테스트")
    print("=" * 60)

    # 샘플 문제 선택
    samples = []
    for p in PROBLEM_BANK:
        if p.kind == "Python.Pyspark" and len(samples) == 0:
            samples.append(p)
        elif p.kind == "Python" and len(samples) == 1:
            samples.append(p)
        elif p.kind == "SQL" and len(samples) == 2:
            samples.append(p)

        if len(samples) == 3:
            break

    for p in samples:
        library_info = f" ({p.library})" if p.library else ""
        display = f"- 언어: {p.language}{library_info}"
        print(f"\n✅ {p.title}")
        print(f"   kind='{p.kind}' -> {display}")

    return True


def main():
    """모든 테스트 실행"""
    print("\n🚀 변경사항 테스트 시작\n")

    tests = [
        ("Problem 클래스 속성", test_problem_properties),
        ("PROBLEM_BANK 로딩", test_problem_bank_loading),
        ("필터 로직", test_filter_logic),
        ("문제 표시 포맷", test_render_display),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ {name} 테스트 실패: {e}")
            results.append((name, False))

    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{status}: {name}")

    all_passed = all(passed for _, passed in results)

    if all_passed:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n⚠️ 일부 테스트 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
