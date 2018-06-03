#ifndef HAUL_IO_H
#define HAUL_IO_H
// HAUL IO

#import <Arduino.h>
//#import <HardwareSerial.h>
//#import <SoftwareSerial.h>
//#include <stdio.h>
//#define Serial HardwareSerial

#define println(s)	Serial.println(s)
#define print(s)	Serial.print(s)

void put(const char *data) {
	println(data);
}
void put_(const char *data) {
	print(data);
}
void shout(const char *data) {
	println(data);
}


#define MAX_INPUT 64
char* fetch() {
	//return Serial.readString();
	
	static char input_line[MAX_INPUT];
	static unsigned int input_pos;
	
	input_pos = 0;
	while(1) {
		
		if (Serial.available() == 0) {
			delay(1);
			continue;
		}
		
		char inByte = Serial.read();
		switch (inByte) {
			case '\n':
				input_line[input_pos] = 0;  // terminating null byte
				return input_line;
				break;
			
			case '\r':   // discard carriage return
				break;
			
			default:
				// keep adding if not full ... allow for terminating null byte
				if (input_pos < (MAX_INPUT - 1))
					input_line[input_pos] = inByte;
					input_pos++;
				break;
		}
	}	// end of incoming data
	return &input_line[0];
	
}


char buf[10];
char *int_str(int i) {
	sprintf(buf, "%d", i);
	return buf;
}


/*
void put(String data) {
	Serial.println(data);
}

String fetch() {
	return Serial.readString();
}
*/
#endif