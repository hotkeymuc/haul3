
#include <stdio.h>
#include <string.h>	// for strlen
#include <sound.h>

put(char *text) {
	printf(text);
	printf("\n");
}

put_(char *text) {
	printf(text);
}

shout(char *text) {
	printf(text);
	printf("\n");
}

#define INPUT_SIZE 64
char* fetch() {
	static char result[INPUT_SIZE];
	putchar('>');
	if (!fgets(result, sizeof(result), stdin)) {
		//exit(1);
	}
	
	result[strlen(result) - 1] = '\0';
	return result;
}

//@FIXME: Implement
#define OUTPUT_SIZE 10
char *int_str(short i) {
	static char result[OUTPUT_SIZE];
	short j;
	char o;
	
	if (i < 0) {
		j = -i;
		result[0] = '-';
		o = 1;
	} else {
		j = i;
		o = 0;
	}
	while (j > 10) {
		j /= 10;
		o++;
	}
	result[o+1] = '\0';
	
	if (j < 0) j = -i;
	else j = i;
	
	while(o >= 0) {
		result[o] = ('0' + (j % 10));
		j /= 10;
		o--;
	}
	
	return result;
}

/*
void hio_sound(unsigned short frq, unsigned short len) {
	// Perform a beep (frq is actually a delay...)
	#asm
		di
		pop	bc
		pop	de	; len
		pop	hl	; frq
		push	hl
		push	de
		push	bc
		
		
	
		push	hl
		push	de
		push	bc
		
		_sound_loop:
			; Speaker on
			ld	a, 8h	; +20h
			out	(12h), a
			call _sound_delay
			
			; Speaker on
			ld	a, 0h	; +20h
			out	(12h), a
			call _sound_delay
		
		dec	e
		jr	nz, _sound_loop
		dec	d
		jr	nz, _sound_loop
		jr _sound_end
		
		_sound_delay:
			push    hl
			push    af
			_sound_delay_loop:
				dec	hl
				ld	a,h
				or	l
				jr	nz, _sound_delay_loop
			pop     af
			pop     hl
		ret
		
		
		
	_sound_end:
		pop	bc
		pop	de
		pop	hl
		ei
	#endasm
}

void hio_sound_note(unsigned char n, unsigned short len) {
	unsigned short frq;
	
	// My own, working great!
	switch(n % 12) {
		case 0:	frq = 0x0900;	break;
		case 1:	frq = 0x087e;	break;
		case 2:	frq = 0x0804;	break;
		case 3:	frq = 0x0791;	break;
		case 4:	frq = 0x0724;	break;
		case 5:	frq = 0x06be;	break;
		case 6:	frq = 0x065d;	break;
		case 7:	frq = 0x0601;	break;
		case 8:	frq = 0x05ab;	break;
		case 9:	frq = 0x0559;	break;
		case 10:	frq = 0x050d;	break;
		case 11:	frq = 0x04c4;	break;
	}
	
	frq = frq >> (n/12);
	len = 0x0100 + (len / frq);	// Length according to delay
	hio_sound(frq, len);
}
*/
void beep() {
	//sound(0x0303, 0x011f);
	//hio_sound_note(12*3 + 0, 0x2000);
	
	bit_beep(100, 880);
}

