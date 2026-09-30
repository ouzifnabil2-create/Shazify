Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strPath = fso.GetAbsolutePathName(".")

WshShell.Run Chr(34) & strPath & "\venv\Scripts\pythonw.exe" & Chr(34) & " " & Chr(34) & strPath & "\tray_app.py" & Chr(34), 0, False

