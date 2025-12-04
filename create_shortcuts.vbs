' ====================================================================
' CodeDojo 바로가기 생성 스크립트 (Windows용)
' ====================================================================
' 데스크톱에 CodeDojo 설치 및 실행 바로가기를 만듭니다.
' ====================================================================

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 현재 스크립트가 있는 디렉토리
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' 데스크톱 경로
strDesktop = objShell.SpecialFolders("Desktop")

' 아이콘 파일 경로 (있다면)
strIconPath = strScriptPath & "\icon.ico"
bHasIcon = objFSO.FileExists(strIconPath)

' ─────────────────────────────────────────────────────────────────
' 확인 메시지
' ─────────────────────────────────────────────────────────────────
intResponse = MsgBox("데스크톱에 CodeDojo 바로가기를 만들까요?" & vbCrLf & vbCrLf & _
                     "생성될 바로가기:" & vbCrLf & _
                     "  1. CodeDojo 설치" & vbCrLf & _
                     "  2. CodeDojo 실행", _
                     vbQuestion + vbYesNo, "CodeDojo 바로가기 생성")

If intResponse <> vbYes Then
    WScript.Quit 0
End If

' ─────────────────────────────────────────────────────────────────
' 바로가기 1: CodeDojo 설치
' ─────────────────────────────────────────────────────────────────
strSetupTarget = strScriptPath & "\setup_windows.vbs"
If objFSO.FileExists(strSetupTarget) Then
    Set objShortcut = objShell.CreateShortcut(strDesktop & "\CodeDojo 설치.lnk")
    objShortcut.TargetPath = "wscript.exe"
    objShortcut.Arguments = """" & strSetupTarget & """"
    objShortcut.WorkingDirectory = strScriptPath
    objShortcut.Description = "CodeDojo를 설치합니다 (가상환경 및 의존성)"
    objShortcut.WindowStyle = 1 ' 일반 창

    ' 아이콘이 있으면 설정
    If bHasIcon Then
        objShortcut.IconLocation = strIconPath & ",0"
    End If

    objShortcut.Save

    strMessage = "✓ '코드도장 설치' 바로가기 생성 완료" & vbCrLf
Else
    strMessage = "✗ setup_windows.vbs를 찾을 수 없습니다" & vbCrLf
End If

' ─────────────────────────────────────────────────────────────────
' 바로가기 2: CodeDojo 실행
' ─────────────────────────────────────────────────────────────────
strRunTarget = strScriptPath & "\run_codedojo.vbs"
If objFSO.FileExists(strRunTarget) Then
    Set objShortcut = objShell.CreateShortcut(strDesktop & "\CodeDojo 실행.lnk")
    objShortcut.TargetPath = "wscript.exe"
    objShortcut.Arguments = """" & strRunTarget & """"
    objShortcut.WorkingDirectory = strScriptPath
    objShortcut.Description = "CodeDojo를 실행합니다"
    objShortcut.WindowStyle = 1 ' 일반 창

    ' 아이콘이 있으면 설정
    If bHasIcon Then
        objShortcut.IconLocation = strIconPath & ",0"
    End If

    objShortcut.Save

    strMessage = strMessage & "✓ '코드도장 실행' 바로가기 생성 완료" & vbCrLf
Else
    strMessage = strMessage & "✗ run_codedojo.vbs를 찾을 수 없습니다" & vbCrLf
End If

' ─────────────────────────────────────────────────────────────────
' 완료 메시지
' ─────────────────────────────────────────────────────────────────
strMessage = strMessage & vbCrLf & "바로가기 생성이 완료되었습니다!" & vbCrLf & vbCrLf

If Not bHasIcon Then
    strMessage = strMessage & "참고: icon.ico 파일이 없어서 기본 아이콘을 사용합니다." & vbCrLf & _
                             "아이콘을 추가하려면 icon.ico 파일을 프로젝트 폴더에 넣고" & vbCrLf & _
                             "이 스크립트를 다시 실행하세요."
End If

MsgBox strMessage, vbInformation, "CodeDojo 바로가기 생성"

' 데스크톱 폴더 열기 (선택사항)
intResponse = MsgBox("데스크톱 폴더를 열어볼까요?", vbQuestion + vbYesNo, "CodeDojo 바로가기 생성")
If intResponse = vbYes Then
    objShell.Run "explorer.exe /select," & strDesktop, 1, False
End If

WScript.Quit 0
