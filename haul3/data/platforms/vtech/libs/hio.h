/*
	HAUL I/O for V-Tech Genius Leader Learning Notebook

Headers for writing V-Tech ROMs

Mostly done via reverse-engineering
2017-01-08 Bernhard "HotKey" Slawik

*/

#include <math.h>
#include <float.h>
#include <vtech.h>

// No float? Int should be precise enough for every one :-D
//#define float signed int

#define bool unsigned char
#define True 255
#define False 0

// Those two are missing. Used for float handling.
#asm
dstore:
	ret
dload:
	ret
dldpah:
	ret
dldpsh:
	ret
dleq:
	ret
#endasm

#define VAR_START_HIO VAR_START_VTECH + VAR_SIZE_VTECH

extern byte zero				@ (VAR_START_HIO + 0);
extern float hiofloat				@ (VAR_START_HIO + 4);
extern byte str_compare_c1	@ (VAR_START_HIO + 8);
extern byte str_compare_c2	@ (VAR_START_HIO + 9);


#define FETCH_SIZE 128
extern byte fetch_buf[FETCH_SIZE]	@ (VAR_START_HIO + 10);
#define VAR_SIZE_HIO + 10 + FETCH_SIZE


#define VAR_START_USER VAR_START_HIO + VAR_SIZE_HIO

void put(byte *text) {
	//screen_put_char(text);
	p_put(text);
	p_put_char(0x0a);
}

void put_direct(char *txt) {
	p_put(txt);
}


char *fetch() {
	byte l = get_line(fetch_buf);
	return &fetch_buf[0];
}

void shout(byte *txt) {
	put(txt);
	put_char(0x0a);
	beep();
	//get_char();	// Wait for key
}



byte *int_str(int i) {
	return &zero;
}

byte str_compare(byte *s1, byte *s2) {
	while (1) {
		str_compare_c1 = *s1;
		str_compare_c2 = *s2;
		
		if (str_compare_c1 != str_compare_c2)
			return 0;
		
		if ((str_compare_c1 == 0) || (str_compare_c2 == 0))
			return 1;
		
		s1++;
		s2++;
	}
}


main_internal() {
	vtech_init();
	
	zero = 0;
	
	hiofloat = 3.2;
	
	screen_reset();	// Especially when you compile in "rom_autorun" mode (where the screen is not yet properly initialized)
	key_reset();
	screen_clear();	// Clear screen (contains garbage left in RAM)
	
	shout("HAUL for V-Tech");	// \r
	
	/*
	if (hiofloat <= 3.0)
		shout("smaller");
	else
		shout("bigger");
	*/
	
	main();
}