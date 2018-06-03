/*
	HAUL I/O for Game Boy

*/

#include <stdio.h>


#include <gb/font.h>
#include <gb/console.h>
#include <gb/drawing.h>

#define bool char
#define True 1
#define False 0

font_t put_font, shout_font;

// Forward
void main_internal(void);

void put(char *text) {
	printf(text);
	printf("\n");
}

void put_(char *text) {
	printf(text);
}


#define FETCH_MAX 32
char fetch_buf[FETCH_MAX];
char *fetch() {
	//fetch_buf[0] = 0;
	//byte l = get_line(fetch_buf)
	return gets(fetch_buf);
	//return &fetch_buf[0];
}



void beep() {
	unsigned int freq = 1750;  // approx 440 Hz
	
	NR14_REG = 0x80;
	NR12_REG = 0;
	
	NR50_REG = 0xFF;
	NR51_REG = 0xFF;
	NR52_REG = 0x80;	// Turn on sound
	 
	NR10_REG = 0;         // No frequency sweep
	NR11_REG = 0x40;   // 25% duty cycle
	NR12_REG = 0xF0;   // Maximum volume
	NR13_REG = (unsigned char)freq & 0xff;
	NR14_REG = 0x80 | (freq>>8); // Start output
	
	// Wait for as long as you want to output sound..
	for(freq = 10000; freq > 1; freq--) {}
	
	// Mute channel 1 (there are other ways to do this)
	NR12_REG = 0;
	NR14_REG = 0x80;
}


void shout(char *txt) {
	font_set(shout_font);
	printf("! ");
	printf(txt);
	printf(" !\n");
	
	beep();
	
	font_set(put_font);
}



#define INT_STR_MAX 8
char int_str_buf[INT_STR_MAX];
char *int_str(int i) {
	//int_str_buf[0] = (char)'0' + i;
	sprintf(int_str_buf, "%d", i);
	return &int_str_buf[0];
}

char str_compare(char *s1, char *s2) {
	while (1) {
		char str_compare_c1 = *s1;
		char str_compare_c2 = *s2;
		
		if (str_compare_c1 != str_compare_c2)
			return 0;
		
		if ((str_compare_c1 == 0) || (str_compare_c2 == 0))
			return 1;
		
		s1++;
		s2++;
	}
}


void main(void) {
	// First, init the font system
	font_init();
	
	// Load all the fonts that we can
	//put_font = font_load(font_ibm);  // 96 tiles
	//italic_font = font_load(font_italic);   // 93 tiles
	//shout_font = font_load(font_min);	// font_min has some errors ("U" -> "K")
	put_font = font_load(font_ibm);
	
	// Load this one with dk grey background and white foreground
	color(WHITE, DKGREY, SOLID);
	shout_font = font_load(font_spect);
	
	// Turn scrolling off (why not?)
	//mode(get_mode() | M_NO_SCROLL);
	
	beep();
	
	//cls();
	font_set(put_font);
	//shout("HAUL for GameBoy");
	
	main_internal();
}