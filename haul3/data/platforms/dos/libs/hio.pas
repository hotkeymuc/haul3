{ HAUL IO }
Unit hio;
{$N+}

Interface

Procedure put(data:String);
Procedure put_(data:String);
Procedure shout(data:String);
Function fetch:String;

Function int_str(i:Integer):String;
Function float_str(f:Single):String;

Implementation

Procedure put(data:String);
Begin
	WriteLn(data);
End;
Procedure put_(data:String);
Begin
	Write(data);
End;
Procedure shout(data:String);
Begin
	WriteLn('!! ', data);
End;

Function fetch:String;
var
	s: String;
begin
	readln(s);
	fetch := s;
end;


Function int_str(i:Integer):String;
Var
	s:String;
begin
	Str(i, s);
	int_str := s;
End;

Function float_str(f:Single):String;
var
	s: String;
begin
	Str(f, s);
	float_str := s;
End;

End.