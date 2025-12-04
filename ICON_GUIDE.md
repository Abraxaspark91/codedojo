# 아이콘 추가 가이드

CodeDojo에 멋진 아이콘을 추가할 수 있습니다!

- [Windows 아이콘 가이드](#windows-아이콘-가이드-ico)
- [Mac 아이콘 가이드](#mac-아이콘-가이드-icns)

---

# Windows 아이콘 가이드 (.ico)

Windows 바로가기에 아이콘을 추가하는 방법입니다.

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

# Mac 아이콘 가이드 (.icns)

Mac 앱 번들에 아이콘을 추가하는 방법입니다.

## 📋 준비물

1. **아이콘 파일 (`.icns` 형식)**
   - 크기: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
   - 형식: `.icns` (Mac 아이콘 형식)

## 🎨 아이콘 만들기

### 방법 1: 온라인 변환 도구 사용

1. 1024x1024 PNG 이미지 준비 (정사각형, 투명 배경 권장)
2. 아래 사이트 중 하나에서 `.icns`로 변환:
   - https://cloudconvert.com/png-to-icns
   - https://iconverticons.com/online/
   - https://anyconv.com/png-to-icns-converter/
3. 변환된 `.icns` 파일 다운로드

### 방법 2: Mac 명령어 사용 (고급)

Terminal에서 다음 명령어 실행:

```bash
# 1. iconset 폴더 생성
mkdir MyIcon.iconset

# 2. 여러 크기의 이미지 생성 (원본: icon_1024x1024.png)
sips -z 16 16     icon_1024x1024.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     icon_1024x1024.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     icon_1024x1024.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     icon_1024x1024.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   icon_1024x1024.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   icon_1024x1024.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   icon_1024x1024.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   icon_1024x1024.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   icon_1024x1024.png --out MyIcon.iconset/icon_512x512.png
sips -z 1024 1024 icon_1024x1024.png --out MyIcon.iconset/icon_512x512@2x.png

# 3. icns 파일 생성
iconutil -c icns MyIcon.iconset

# 4. 생성된 MyIcon.icns 사용
```

### 방법 3: 이미지 편집 앱 사용

- **Image2icon** (무료 Mac 앱) - 추천!
  - https://img2icnsapp.com/
  - 드래그 앤 드롭으로 쉽게 변환

- **Icon Composer** (Xcode 도구)
  - Xcode를 설치한 경우 사용 가능

## 📂 아이콘 파일 설치

1. 만든 아이콘 파일 이름을 `AppIcon.icns`로 변경
2. `CodeDojo.app/Contents/Resources/` 폴더에 복사

```
codedojo/
└── CodeDojo.app/
    └── Contents/
        ├── Info.plist
        ├── MacOS/
        │   └── launch
        └── Resources/
            └── AppIcon.icns  ← 여기에 아이콘 파일 넣기
```

3. Finder에서 CodeDojo.app 아이콘 확인

## ✅ 적용 확인

1. `AppIcon.icns`를 `CodeDojo.app/Contents/Resources/`에 넣기
2. Finder에서 CodeDojo.app을 새로고침 (폴더 나갔다 들어오기)
3. 아이콘이 변경되었는지 확인!

### 아이콘이 바로 표시되지 않는 경우

Terminal에서 다음 명령어 실행:

```bash
# 아이콘 캐시 강제 업데이트
sudo rm -rf /Library/Caches/com.apple.iconservices.store
killall Finder
killall Dock
```

## 💡 추천 아이콘 디자인

CodeDojo에 어울리는 아이콘:
- 🥋 도장(도복) + 코드 기호
- 💻 Mac 스타일 그라데이션 배경
- 📊 데이터베이스 + 터미널 조합
- 🐍 Python 로고 스타일 (라운드 코너)

**Mac 스타일 디자인 팁:**
- 라운드 코너 사용
- 그라데이션 배경
- 투명 배경 또는 부드러운 그림자
- 1024x1024 고해상도 권장

## ❓ 문제 해결

### 아이콘이 표시되지 않아요
1. 파일 이름이 정확히 `AppIcon.icns`인지 확인
2. 파일이 `CodeDojo.app/Contents/Resources/` 폴더에 있는지 확인
3. Finder와 Dock 재시작 (위의 명령어 실행)
4. 앱을 휴지통에 넣었다가 다시 꺼내기

### 아이콘이 흐릿해요
- 1024x1024 고해상도 이미지 사용
- Retina 디스플레이용 @2x 이미지 포함
- 벡터 이미지로 시작해서 변환

### 기본 폴더 아이콘이 표시돼요
- `.icns` 파일 형식이 올바른지 확인
- `Info.plist`에 `CFBundleIconFile` 키가 있는지 확인
- 아이콘 파일명이 `AppIcon.icns`인지 확인 (확장자 제외하고 지정됨)

---

## 🆓 무료 아이콘 리소스

### Windows (.ico) & Mac (.icns) 공통
- **Flaticon**: https://www.flaticon.com/
- **Icons8**: https://icons8.com/
- **Iconfinder**: https://www.iconfinder.com/
- **Noun Project**: https://thenounproject.com/

### 검색어 추천
- "code", "coding", "programming"
- "dojo", "martial arts", "karate"
- "database", "sql", "data"
- "terminal", "console", "python"

---

**도움이 필요하신가요?**
- Windows: `.ico` 파일 (여러 크기 포함)
- Mac: `.icns` 파일 (Retina 지원)
