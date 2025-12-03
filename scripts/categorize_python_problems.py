#!/usr/bin/env python3
"""
Python 문제들을 라이브러리별로 자동 분류하여 kind 값을 업데이트하는 스크립트
"""
import json
from pathlib import Path
from collections import defaultdict

def categorize_problem(pid: str, title: str, body: str) -> str:
    """
    pid, title, body를 분석하여 적절한 kind 값을 반환합니다.
    """
    # 모든 텍스트를 소문자로 변환하여 검사
    text = f"{pid} {title} {body}".lower()

    # 라이브러리별 키워드 패턴 (우선순위 순서로 정렬)
    if 'pyspark' in text:
        return "Python.Pyspark"
    elif 'numpy' in text or 'np.' in text:
        return "Python.Numpy"
    elif 'pandas' in text or 'pd.' in text or 'dataframe' in text or 'series' in text:
        return "Python.Pandas"
    elif 'matplotlib' in text or 'pyplot' in text or 'plt.' in text:
        return "Python.Matplotlib"
    elif 'seaborn' in text or 'sns.' in text:
        return "Python.Seaborn"
    elif 'scikit' in text or 'sklearn' in text:
        return "Python.Sklearn"
    elif 'tensorflow' in text or 'keras' in text:
        return "Python.Tensorflow"
    elif 'pytorch' in text or 'torch' in text:
        return "Python.Pytorch"
    else:
        # 순수 Python 문제
        return "Python"

def main():
    # problems.json 읽기
    problems_path = Path("data/problems.json")

    if not problems_path.exists():
        print(f"❌ {problems_path} 파일을 찾을 수 없습니다.")
        return

    with open(problems_path, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    # 통계 수집
    stats = defaultdict(int)
    changes = []

    # 각 문제 분석 및 변경
    for problem in problems:
        old_kind = problem['kind']

        # python 문제만 처리 (SQL은 그대로 유지)
        if old_kind.lower() == 'python':
            new_kind = categorize_problem(
                problem['pid'],
                problem['title'],
                problem.get('body', '')
            )
            problem['kind'] = new_kind
            stats[new_kind] += 1

            if new_kind != "Python":
                changes.append({
                    'pid': problem['pid'],
                    'title': problem['title'],
                    'old': old_kind,
                    'new': new_kind
                })
        elif old_kind.lower() == 'sql':
            # SQL은 대문자로 통일
            problem['kind'] = 'SQL'
            stats['SQL'] += 1
        else:
            # 이미 세분화된 경우 통계만 수집
            stats[problem['kind']] += 1

    # 결과 출력
    print("=" * 60)
    print("📊 Python 문제 분류 결과")
    print("=" * 60)

    for kind in sorted(stats.keys()):
        print(f"  {kind:20s}: {stats[kind]:3d}개")

    print("\n" + "=" * 60)
    print(f"📝 변경된 문제들 (총 {len(changes)}개)")
    print("=" * 60)

    for change in changes:
        print(f"\n• [{change['new']}] {change['title']}")
        print(f"  PID: {change['pid']}")
        print(f"  {change['old']} → {change['new']}")

    # 백업 생성
    backup_path = problems_path.with_suffix('.json.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)
    print(f"\n💾 원본 백업: {backup_path}")

    # 업데이트된 내용 저장
    with open(problems_path, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

    print(f"✅ 업데이트 완료: {problems_path}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
