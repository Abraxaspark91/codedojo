' ====================================================================
' CodeDojo 실행 스크립트 VBS 래퍼 (Windows용)
' ====================================================================
' 이 스크립트는 콘솔 창 없이 CodeDojo를 실행합니다.
' 깔끔한 사용자 경험을 제공합니다.
' ====================================================================

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 현재 스크립트가 있는 디렉토리로 이동
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptPath

' ─────────────────────────────────────────────────────────────────
' 사전 체크 1: run_codedojo.bat 파일 존재 확인
' ─────────────────────────────────────────────────────────────────
strBatchFile = strScriptPath & "\run_codedojo.bat"
If Not objFSO.FileExists(strBatchFile) Then
    MsgBox "오류: run_codedojo.bat 파일을 찾을 수 없습니다!" & vbCrLf & vbCrLf & _
           "경로: " & strBatchFile, vbCritical, "CodeDojo 실행"
    WScript.Quit 1
End If

' ─────────────────────────────────────────────────────────────────
' 사전 체크 2: Python 설치 확인
' ─────────────────────────────────────────────────────────────────
On Error Resume Next
intReturn = objShell.Run("python --version", 0, True)
On Error GoTo 0

If intReturn <> 0 Then
    intResponse = MsgBox("Python을 찾을 수 없어요!" & vbCrLf & vbCrLf & _
                         "Python 3.8 이상을 설치해야 합니다." & vbCrLf & vbCrLf & _
                         "지금 Python 다운로드 페이지를 열까요?", _
                         vbQuestion + vbYesNo, "CodeDojo 실행")

    If intResponse = vbYes Then
        objShell.Run "https://www.python.org/downloads/", 1, False
    End If
    WScript.Quit 1
End If

' ─────────────────────────────────────────────────────────────────
' 사전 체크 3: 가상환경 확인
' ─────────────────────────────────────────────────────────────────
strVenvPath = strScriptPath & "\.venv\Scripts\activate.bat"
If Not objFSO.FileExists(strVenvPath) Then
    intResponse = MsgBox("가상환경이 설치되지 않았어요!" & vbCrLf & vbCrLf & _
                         "먼저 설치 스크립트를 실행해야 합니다." & vbCrLf & vbCrLf & _
                         "지금 설치 스크립트를 실행할까요?", _
                         vbQuestion + vbYesNo, "CodeDojo 실행")

    If intResponse = vbYes Then
        ' setup_windows.bat 실행
        strSetupFile = strScriptPath & "\setup_windows.bat"
        If objFSO.FileExists(strSetupFile) Then
            objShell.Run "cmd.exe /c """ & strSetupFile & """", 1, True
            ' 설치 후 다시 시도할지 물어봄
            intRetry = MsgBox("설치가 완료되었습니다!" & vbCrLf & vbCrLf & _
                             "이제 CodeDojo를 실행할까요?", _
                             vbQuestion + vbYesNo, "CodeDojo 실행")
            If intRetry = vbNo Then
                WScript.Quit 0
            End If
        Else
            MsgBox "setup_windows.bat 파일을 찾을 수 없습니다!", vbCritical, "CodeDojo 실행"
            WScript.Quit 1
        End If
    Else
        WScript.Quit 0
    End If
End If

' ─────────────────────────────────────────────────────────────────
' 사전 체크 4: LM Studio 연결 확인 (경고만 표시)
' ─────────────────────────────────────────────────────────────────
' HTTP 요청을 통한 체크는 VBS에서 복잡하므로, bat 파일에서 처리하도록 합니다.
' 여기서는 사용자에게 알림만 표시합니다.

' ─────────────────────────────────────────────────────────────────
' CodeDojo 실행
' ─────────────────────────────────────────────────────────────────
' 안내 메시지
MsgBox "CodeDojo를 시작합니다!" & vbCrLf & vbCrLf & _
       "잠시 후 브라우저가 자동으로 열립니다." & vbCrLf & vbCrLf & _
       "참고:" & vbCrLf & _
       "- LM Studio가 실행 중이어야 피드백을 받을 수 있어요" & vbCrLf & _
       "- 종료하려면 작업 관리자에서 python.exe를 종료하세요", _
       vbInformation, "CodeDojo 실행"

' 배치 파일 실행 (콘솔 창 숨김: 0, 대기하지 않음: False)
' 백그라운드에서 실행되므로 사용자는 콘솔 창을 보지 않습니다.
objShell.Run "cmd.exe /c """ & strBatchFile & """", 0, False

' 성공 메시지는 표시하지 않음 (브라우저가 자동으로 열림)
WScript.Quit 0
