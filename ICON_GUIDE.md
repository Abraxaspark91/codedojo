# 아이콘 추가 가이드 (Windows)

CodeDojo 바로가기에 멋진 아이콘을 추가할 수 있습니다!

## 📋 준비물

1. **아이콘 파일 (`.ico` 형식)**
   - 크기: 16x16, 32x32, 48x48, 256x256 (여러 크기 포함 권장)
   - 형식: `.ico` (Windows 아이콘 형식)

## 🎨 아이콘 만들기

### 방법 1: 온라인 변환 도구 사용
1. 이미지 파일 (PNG, JPG 등) 준비
2. 아래 사이트 중 하나에서 `.ico`로 변환:
   - https://www.icoconverter.com/
   - https://convertio.co/kr/png-ico/
   - https://favicon.io/
3. 변환된 `.ico` 파일 다운로드

### 방법 2: 무료 아이콘 다운로드
- https://www.flaticon.com/ (무료 아이콘 검색)
- https://icons8.com/ (다양한 아이콘 제공)
- 검색어: "code", "dojo", "martial arts", "terminal" 등

### 방법 3: Photoshop/GIMP 사용
- 이미지 편집 프로그램으로 직접 제작
- 여러 크기로 저장 (16x16, 32x32, 48x48, 256x256)
- `.ico` 형식으로 내보내기

## 📂 아이콘 파일 설치

1. 만든 아이콘 파일 이름을 `icon.ico`로 변경
2. CodeDojo 프로젝트 폴더 (이 파일이 있는 폴더)에 복사
3. `create_shortcuts.vbs`를 실행하여 바로가기 재생성

```
codedojo/
├── icon.ico          ← 여기에 아이콘 파일 넣기
├── setup_windows.vbs
├── run_codedojo.vbs
└── create_shortcuts.vbs
```

## ✅ 적용 확인

1. `create_shortcuts.vbs`를 더블클릭
2. 데스크톱에 생성된 바로가기 확인
3. 아이콘이 제대로 표시되는지 확인!

## 💡 추천 아이콘 디자인

CodeDojo에 어울리는 아이콘:
- 🥋 도장(도복) + 코드 기호
- 💻 컴퓨터 + 무술 요소
- 📊 데이터베이스 아이콘
- 🐍 Python 로고 스타일

## ❓ 문제 해결

### 아이콘이 표시되지 않아요
1. 파일 이름이 정확히 `icon.ico`인지 확인
2. 파일이 올바른 폴더에 있는지 확인
3. `create_shortcuts.vbs`를 다시 실행
4. 바로가기를 삭제하고 다시 생성

### 아이콘이 흐릿해요
- 더 큰 해상도의 아이콘 사용 (256x256 이상)
- 여러 크기가 포함된 `.ico` 파일 사용

### 다른 이름의 아이콘을 사용하고 싶어요
`create_shortcuts.vbs` 파일을 텍스트 에디터로 열고:
```vbs
strIconPath = strScriptPath & "\icon.ico"
```
이 부분을 원하는 파일 이름으로 변경하세요.

---

**참고:** Mac 사용자는 `.icns` 형식을 사용합니다. Mac 아이콘 가이드는 별도로 제공됩니다.
