' ## Basic functions

Public lastPut
Sub put(txt)
	If Len(lastPut) > 0 Then
		Call WScript.Echo(lastPut & txt & vbCRLF)
		lastPut = ""
	Else
		Call WScript.Echo(txt & vbCRLF)
	End If
End Sub
Sub putR(txt)
	lastPut = lastPut & txt
End Sub

Sub file_putString(filename, data)
	Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")
	Dim FSTS: Set FSTS = FS.CreateTextFile(filename, True)
	FSTS.Write data
End Sub
Sub file_getString(filename)
	Dim FS: Set FS = CreateObject("Scripting.FileSystemObject")
	Dim FSTS: Set FSTS = FS.OpenTextFile(filename, 1)
	file_getString = FSTS.ReadAll()
	FSTS.Close
End Sub

Function res_getString(key)
	Dim i
	For i = 0 To UBound(RESidx)
		If RESidx(i) = key Then
			res_getString = RES(i)
			Exit Function
		End If
	Next
End Function

Function explode(del, s)
	Dim i
	Dim j
	Dim c
	j = 0
	Dim r(2048)
	j = 0
	For i = 1 To Len(s)
		c = Mid(s, i, 1)
		If c = del Then
			j = j + 1
			r(j) = ""
		Else
			r(j) = r(j) & c
		End If
	Next
	explode = r
End Function

' ### Hybernation code
Public HY_STATE
HY_STATE = ""
Public HY_PARAM

Sub hyber_allowSleep(state, param)
	HY_STATE = state
	HY_PARAM = param
End Sub

' ### Translate/load run-time libraries on-the-fly
' res_load("someLib.inc.php");