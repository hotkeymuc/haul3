// HAUL IO

//#import <Arduino.h>
//#import <HardwareSerial.h>
//#import <SoftwareSerial.h>
//#include <stdio.h>
#define print(s)	/* Serial.print(s) */
#define println(s)	/* Serial.println(s) */

char buf[10];
char *int_str(int i) {
	sprintf(buf, "%d", i);
	return buf;
}


void put(const char *data) {
	println(data);
}
void put_direct(const char *data) {
	print(data);
}
void shout(const char *data) {
	println(data);
}


char data[255];
char* fetch() {
	return &data[0];
}

/*
void put(String data) {
	Serial.println(data);
}

String fetch() {
	return Serial.readString();
}
*/