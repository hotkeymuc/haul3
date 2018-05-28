{ Glue code to run HAUL3 }
{$N+}	{ We need floats }
Unit sys;

Interface

Procedure print(s:String);
{
Function int_str(i:Integer):String;
Function float_str(f:Single):String;
}
Implementation

Procedure print(s:String);
Begin
	WriteLn(s);
End;
{
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
}
End.