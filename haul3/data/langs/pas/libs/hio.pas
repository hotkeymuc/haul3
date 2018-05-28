{ HAUL IO }
Unit hio;

Interface

Procedure put(data:String);
Procedure put_direct(data:String);
Procedure shout(data:String);
Function fetch():String;

Function int_str(i:Integer):String;
{Function str(f:Float):String; overload;}

Implementation

Procedure put(data:String);
Begin
	WriteLn(data);
End;
Procedure put_direct(data:String);
Begin
	Write(data);
End;
Procedure shout(data:String);
Begin
	WriteLn('!! ', data);
	ReadLn;
End;

Function fetch():String;
begin
	Result := ReadLn();
end;


Function int_str(i:Integer):String;
Var
	s:String;
begin
	{str := IntToStr(i);}
	Str(i, s);
	int_str := s;
End;
{
Function str(f:Float):String;
begin
	Result := FloatToStr(v);
End;
}
End.