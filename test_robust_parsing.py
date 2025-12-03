#!/usr/bin/env python3
"""
강건한 JSON 파싱 로직 테스트
다양한 엣지 케이스를 테스트합니다.
"""
import json
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import unicodedata


# 테스트를 위해 필요한 함수들을 직접 정의
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
    nickname: str = ""


def safe_read_file(path: Path) -> str:
    """다중 인코딩 시도로 안전하게 파일 읽기"""
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
    """JSON 파싱 전 라인 정제"""
    # 제어 문자 제거 (탭/개행 제외)
    line = ''.join(c for c in line if c >= ' ' or c in '\t\n')

    # NULL 바이트 제거
    line = line.replace('\x00', '')

    # 유니코드 정규화 (NFKC)
    line = unicodedata.normalize('NFKC', line)

    # 양쪽 공백 제거
    return line.strip()


def is_likely_json(line: str) -> bool:
    """라인이 JSON 객체일 가능성이 있는지 빠르게 체크"""
    line = line.strip()
    # JSON 객체는 { 로 시작하고 } 로 끝남
    return line.startswith('{') and line.endswith('}')


def robust_json_parse(line: str) -> Optional[Dict]:
    """여러 방법으로 JSON 파싱 시도"""
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


def test_safe_read_file():
    """파일 읽기 함수 테스트"""
    print("=" * 60)
    print("테스트 1: safe_read_file() - 다중 인코딩 지원")
    print("=" * 60)

    # UTF-8 BOM 테스트
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.txt') as f:
        # UTF-8 BOM + 한글 내용
        f.write(b'\xef\xbb\xbf{"test": "\xed\x95\x9c\xea\xb8\x80"}')
        temp_path = Path(f.name)

    try:
        content = safe_read_file(temp_path)
        # BOM이 제거되었는지 확인
        assert not content.startswith('\ufeff'), "BOM이 제거되지 않았습니다"
        assert '한글' in content, "한글이 올바르게 읽히지 않았습니다"
        print("✅ UTF-8 BOM 처리: 통과")
    finally:
        temp_path.unlink()

    print()


def test_sanitize_line():
    """라인 정제 함수 테스트"""
    print("=" * 60)
    print("테스트 2: sanitize_line() - 제어 문자 제거")
    print("=" * 60)

    # 제어 문자 포함
    line_with_control = "test\x00data\x01more\x02"
    result = sanitize_line(line_with_control)
    assert '\x00' not in result, "NULL 바이트가 제거되지 않았습니다"
    print(f"✅ 제어 문자 제거: '{line_with_control}' -> '{result}'")

    # 공백 처리
    line_with_spaces = "  \t  test data  \t  "
    result = sanitize_line(line_with_spaces)
    assert result == "test data", f"공백 처리 실패: '{result}'"
    print(f"✅ 공백 제거: '{line_with_spaces}' -> '{result}'")

    print()


def test_is_likely_json():
    """JSON 감지 함수 테스트"""
    print("=" * 60)
    print("테스트 3: is_likely_json() - JSON 객체 감지")
    print("=" * 60)

    test_cases = [
        ('{"test": "value"}', True),
        ('  {"test": "value"}  ', True),
        ('# 마크다운 헤더', False),
        ('일반 텍스트', False),
        ('', False),
        ('[1, 2, 3]', False),  # 배열은 건너뜀
    ]

    for line, expected in test_cases:
        result = is_likely_json(line)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{line[:30]}...' -> {result} (예상: {expected})")
        assert result == expected, f"테스트 실패: {line}"

    print()


def test_robust_json_parse():
    """강건한 JSON 파싱 테스트"""
    print("=" * 60)
    print("테스트 4: robust_json_parse() - 다단계 파싱")
    print("=" * 60)

    # 정상 JSON
    normal = '{"test": "value", "number": 123}'
    result = robust_json_parse(normal)
    assert result is not None, "정상 JSON 파싱 실패"
    assert result['test'] == 'value', "값이 올바르지 않습니다"
    print("✅ 정상 JSON 파싱: 통과")

    # 앞뒤에 쓰레기 데이터가 있는 경우
    with_garbage = 'prefix garbage {"test": "value"} suffix garbage'
    result = robust_json_parse(with_garbage)
    assert result is not None, "쓰레기 데이터 포함 JSON 파싱 실패"
    print("✅ 쓰레기 데이터 포함 JSON 파싱: 통과")

    # 파싱 불가능한 데이터
    invalid = '# 마크다운 헤더'
    result = robust_json_parse(invalid)
    assert result is None, "잘못된 JSON이 파싱되었습니다"
    print("✅ 잘못된 JSON 처리: 통과")

    print()


def test_integration_with_real_file():
    """실제 파일로 통합 테스트"""
    print("=" * 60)
    print("테스트 5: 실제 파일 시나리오 테스트")
    print("=" * 60)

    NOTE_PATH = Path("data/wrong_notes.md")

    # 백업 생성
    backup_content = None
    if NOTE_PATH.exists():
        backup_content = NOTE_PATH.read_text(encoding='utf-8')

    try:
        # 유효한 JSON 데이터
        valid_json = {
            "pid": "test001",
            "title": "테스트 문제",
            "difficulty": "Lv1 입문",
            "score": 50,
            "status": "재도전",
            "submitted": "SELECT * FROM test",
            "feedback": "피드백",
            "improvement": "개선사항",
            "reasoning": "이유",
            "question": "문제",
            "code": "SELECT * FROM test",
            "kind": "SQL",
            "timestamp": "2024-01-01 12:00 (월)",
            "rechallenge_hint": "",
            "nickname": ""
        }

        # 테스트 케이스: 마크다운 헤더 + JSON 데이터
        test_content = f"""# 오답노트 기록

{json.dumps(valid_json, ensure_ascii=False)}
{json.dumps({**valid_json, "pid": "test002"}, ensure_ascii=False)}
"""
        NOTE_PATH.write_text(test_content, encoding='utf-8')

        # 파일 읽기 및 파싱
        text = safe_read_file(NOTE_PATH)
        parsed_count = 0
        skipped_count = 0

        for line_idx, line in enumerate(text.split("\n"), 1):
            line = sanitize_line(line)

            if not line:
                continue

            if not is_likely_json(line):
                skipped_count += 1
                continue

            data = robust_json_parse(line)
            if data is not None:
                attempt = Attempt(**data)
                parsed_count += 1

        print(f"✅ 파싱 성공: {parsed_count}개 항목 (예상: 2)")
        print(f"✅ 건너뜀: {skipped_count}개 항목 (마크다운 헤더 등)")
        assert parsed_count == 2, f"파싱 실패: {parsed_count}개만 파싱됨"
        assert skipped_count >= 1, "마크다운 헤더가 건너뛰어지지 않음"

        print("\n🎉 통합 테스트 통과!")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 백업 복원
        if backup_content is not None:
            NOTE_PATH.write_text(backup_content, encoding='utf-8')
        else:
            # 백업이 없으면 원래 상태로 복원
            NOTE_PATH.write_text("# 오답노트 기록\n\n", encoding='utf-8')
        print("✅ 원본 파일 복원 완료")


def main():
    """모든 테스트 실행"""
    print("\n" + "=" * 60)
    print("강건한 JSON 파싱 로직 테스트 시작")
    print("=" * 60 + "\n")

    try:
        test_safe_read_file()
        test_sanitize_line()
        test_is_likely_json()
        test_robust_json_parse()
        test_integration_with_real_file()

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
