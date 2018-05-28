// HAUL I/O for C
#include <stdio.h>

void put(const char *data) {
	puts(data);
}

void shout(const char *data) {
	puts(data);
}

char* fetch() {
	char data[255];
	gets(data);
	
	return &data[0];
}