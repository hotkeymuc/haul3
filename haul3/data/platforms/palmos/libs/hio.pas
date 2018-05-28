{ HAUL IO for PP on PalmOS}

{$I PalmAPI.pas}

procedure put(data:string);
begin
	writeln(data);
end;
procedure put_direct(data:string);
begin
	write(data);
end;
procedure shout(data:string);
begin
	writeln(data);
	
	// Need resources for that:
	//FrmAlert(0);
	//FrmCustomAlert(alertId:UInt16;const s1,s2,s3:String):UInt16; inline(SYSTRAP,$A194);
end;

function fetch:string;
var
	s: string;
begin
	readln(s);
	fetch := s;
end;


function int_str(i:integer):string;
var s:string;
begin
	StrIToA(s,i);
	int_str:=s+chr(0);
end;

function str_int(s:string):integer;
begin
	str_int:=StrAToI(s);
end;

{
function float_str(f:single):string;
var
	s: string;
begin
	s := int_str(f * 100);
	float_str := s;
end;
}

function inttohexdigit(i:UInt8):char;
begin
	if i<=9 then
		inttohexdigit:=chr(ord('0')+i)
	else
		inttohexdigit:=chr(ord('A')+(i-10))
end;

function inttohex(i:UInt32;digits:Uint8):string;
var
	a:UInt8;
	s:string;
begin
	s:='';
	for a:=0 to digits-1 do
		s := inttohexdigit((i shr (a*4)) and $F)+s;
	inttohex:=s;
end;
