' HAUL I/O for VBScript

Sub put(data)
	WScript.echo(data)
End Sub

Sub put_(data)
	WScript.echo(data)
End Sub

Function fetch()
	data = InputBox("Input")
	fetch = data
End Function

Function int_str(i)
	int_str = Val(i)
End Function
'a = fetch()
'put(a)