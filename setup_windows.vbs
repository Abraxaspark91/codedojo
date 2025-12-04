' ====================================================================
' CodeDojo 설치 스크립트 VBS 래퍼 (Windows용)
' ====================================================================
' 이 스크립트는 setup_windows.bat를 실행합니다.
' 설치 과정을 보여주기 위해 콘솔 창을 표시합니다.
' ====================================================================

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 현재 스크립트가 있는 디렉토리로 이동
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strScriptPath

' setup_windows.bat 파일 존재 확인
strBatchFile = strScriptPath & "\setup_windows.bat"
If Not objFSO.FileExists(strBatchFile) Then
    MsgBox "오류: setup_windows.bat 파일을 찾을 수 없습니다!" & vbCrLf & vbCrLf & _
           "경로: " & strBatchFile, vbCritical, "CodeDojo 설치"
    WScript.Quit 1
End If

' 배치 파일 실행 (콘솔 창 표시: 1, 대기: True)
' 사용자가 설치 과정을 볼 수 있도록 창을 표시합니다.
intReturn = objShell.Run("cmd.exe /c """ & strBatchFile & """", 1, True)

' 종료 코드 확인
If intReturn = 0 Then
    ' 성공 - 아무 메시지 없이 종료 (배치 파일에서 이미 메시지 표시)
    WScript.Quit 0
Else
    ' 실패
    MsgBox "설치 중 오류가 발생했습니다." & vbCrLf & _
           "종료 코드: " & intReturn, vbExclamation, "CodeDojo 설치"
    WScript.Quit intReturn
End If
