' Anime Haber Sessiz Baslatici
Set WshShell = CreateObject("WScript.Shell")
strCurDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' pythonw kontrolu (konsolsuz calistirici)
strPythonW = WshShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\Programs\Python\Python312\pythonw.exe"
Set fso = CreateObject("Scripting.FileSystemObject")

If fso.FileExists(strPythonW) Then
    WshShell.CurrentDirectory = strCurDir
    WshShell.Run """" & strPythonW & """ """ & strCurDir & "\main.py""", 0, False
Else
    WshShell.Run """" & strCurDir & "\baslat.bat""", 0, False
End If
