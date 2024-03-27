/*#include <Arduino.h>
#include <Wire.h>
#include <DS3231.h>
#include <Ultrasonic.h>
// #include <SerialTransfer.h>
#include <SerialCommands.h>

#define USONIC_2_TRIG_PIN 3
#define USONIC_2_ECHO_PIN 4

#define USONIC_1_TRIG_PIN 5
#define USONIC_1_ECHO_PIN 6

Ultrasonic ultrasonic_1(USONIC_1_TRIG_PIN, USONIC_1_ECHO_PIN);
unsigned int usonic_1_distance = -1;
Ultrasonic ultrasonic_2(USONIC_2_TRIG_PIN, USONIC_2_ECHO_PIN);
unsigned int usonic_2_distance = -1;
unsigned int maxDistance = 10;

int backPin = 2;
bool backWarning = false;

int frontPin = 7;
bool frontWarning = false;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  Wire.begin();
  pinMode(backPin, OUTPUT);
  pinMode(frontPin, OUTPUT);
  
}

void loop() {
  
  usonic_1_distance = ultrasonic_1.read();
  frontWarning = usonic_1_distance < maxDistance;
  digitalWrite(frontPin, frontWarning);
  Serial.print("Distance from sensor 1: ");
  Serial.print(usonic_1_distance);
  Serial.println(" cm");

  usonic_2_distance = ultrasonic_2.read();
  backWarning = usonic_2_distance < maxDistance;
  digitalWrite(backPin, backWarning);

  Serial.print("Distance from sensor 2: ");
  Serial.print(usonic_2_distance);
  Serial.println(" cm");

  delay(1000);
}
*/

#include <Arduino.h>
#include <Wire.h>
#include <DS3231.h>
#include <Ultrasonic.h>
// #include <SerialTransfer.h>
#include <SerialCommands.h>

#define USONIC_2_TRIG_PIN 3
#define USONIC_2_ECHO_PIN 4

#define USONIC_1_TRIG_PIN 5
#define USONIC_1_ECHO_PIN 6

Ultrasonic ultrasonic_1(USONIC_1_TRIG_PIN, USONIC_1_ECHO_PIN);
unsigned int usonic_1_distance = -1;
Ultrasonic ultrasonic_2(USONIC_2_TRIG_PIN, USONIC_2_ECHO_PIN);
unsigned int usonic_2_distance = -1;
unsigned int maxDistance = 10;

DS3231 rtc;
bool century = false;
bool h12Flag;
bool pmFlag;

int backPin = 2;
bool backWarning = false;

int frontPin = 7;
bool frontWarning = false;

char serial_command_buffer_[32];
SerialCommands serial_commands_(&Serial, serial_command_buffer_, sizeof(serial_command_buffer_), "\r\n", " ");

void setMaxDistance(SerialCommands* sender)
{
  char* distanceStr = sender->Next();
	if (distanceStr == NULL)
	{
		sender->GetSerial()->println("ERROR: no value specified of max distance");
		return;
	}

  char* endDistanceStr = distanceStr;
  unsigned long readDistance = strtoul(distanceStr, &endDistanceStr, 10);
  if (distanceStr == endDistanceStr) {
    	sender->GetSerial()->println("ERROR: no valid value specified of max distance");
		  return;
  }
  maxDistance = (unsigned int) readDistance;
}
SerialCommand cmd_setMaxDistance("setmaxdistance", setMaxDistance);


void getMaxDistance(SerialCommands* sender)
{
  sender->GetSerial()->println(maxDistance);
}
SerialCommand cmd_getMaxDistance("getmaxdistance", getMaxDistance);


void getDistance(SerialCommands* sender)
{
  char* deviceStr = sender->Next();
	if (deviceStr == NULL)
	{
		sender->GetSerial()->println("ERROR: no device specified");
		return;
	}

  if (*deviceStr == '1') {
    sender->GetSerial()->println(usonic_1_distance);
  }
  else if (*deviceStr == '2') {
    sender->GetSerial()->println(usonic_2_distance);
  }
  else {
    	sender->GetSerial()->println("ERROR: no device specified");
		  return;
  }
}
SerialCommand cmd_getDistance("getdistance", getDistance);


void getTime(SerialCommands* sender)
{
  char* modeStr = sender->Next();
	if (modeStr == NULL)
	{
		sender->GetSerial()->println("ERROR: no mode specified");
		return;
	}

  char response[20];
  if (strncmp(modeStr, "alltime", 7 ) == 0)  {
    sprintf(&response[0], "%02u", rtc.getHour(h12Flag, pmFlag));
    sprintf(&response[2], "%c", ':');
    sprintf(&response[3], "%02u", rtc.getMinute());
    sprintf(&response[5], "%c", ':');
    sprintf(&response[6], "%02u", rtc.getSecond());
    sender->GetSerial()->println(response);
  }
  else if (strncmp(modeStr, "alldate", 7 ) == 0)  {
    sprintf(&response[0], "%02u", rtc.getDate());
    sprintf(&response[2], "%c", '-');
    sprintf(&response[3], "%02u", rtc.getMonth(century));
    sprintf(&response[5], "%c", '-');
    sprintf(&response[6], "%c", '2');
    sprintf(&response[7], "%c", '0');
    sprintf(&response[8], "%02u", rtc.getYear());
    sender->GetSerial()->println(response);
  }
  else if (strncmp(modeStr, "all", 3 ) == 0)  {
    sprintf(&response[0], "%c", '2');
    sprintf(&response[1], "%c", '0');
    sprintf(&response[2], "%02u", rtc.getYear());
    sprintf(&response[4], "%c", '-');

    sprintf(&response[5], "%02u", rtc.getMonth(century));
    sprintf(&response[7], "%c", '-');

    sprintf(&response[8], "%02u", rtc.getDate());
    

    sprintf(&response[10], "%c", ' ');

    sprintf(&response[11], "%02u", rtc.getHour(h12Flag, pmFlag));
    sprintf(&response[13], "%c", ':');
    sprintf(&response[14], "%02u", rtc.getMinute());
    sprintf(&response[16], "%c", ':');
    sprintf(&response[17], "%02u", rtc.getSecond());
    sender->GetSerial()->println(response);
  }
  else if (strncmp(modeStr, "hour", 4 ) == 0)  {
    sender->GetSerial()->println(rtc.getHour(h12Flag, pmFlag), DEC);
  }
  else if (strncmp(modeStr, "minute", 7 ) == 0)  {
    sender->GetSerial()->println(rtc.getMinute(), DEC);
  }
  else if (strncmp(modeStr, "second", 7 ) == 0)  {
    sender->GetSerial()->println(rtc.getSecond(), DEC);
  }
  else if (strncmp(modeStr, "year", 4 ) == 0)  {
    sprintf(&response[0], "%c", '2');
    sprintf(&response[1], "%c", '0');
    sprintf(&response[2], "%02u", rtc.getYear());
    sender->GetSerial()->println(response);
  }
  else if (strncmp(modeStr, "month", 5 ) == 0)  {
    sender->GetSerial()->println(rtc.getMonth(century), DEC);
  }
  else if (strncmp(modeStr, "day", 3 ) == 0)  {
    sender->GetSerial()->println(rtc.getDate(), DEC);
  }
  else  {
    DateTime now(2000 + rtc.getYear(), rtc.getMonth(century), rtc.getDate(),
                rtc.getHour(h12Flag, pmFlag), rtc.getMinute(), rtc.getSecond());
    sender->GetSerial()->println(now.unixtime());
  }
}
SerialCommand cmd_getTime("gettime", getTime);


void setTime(SerialCommands* sender)
{
  char* modeStr = sender->Next();
	if (modeStr == NULL)
	{
		sender->GetSerial()->println("ERROR: no mode specified");
		return;
	}

  char* valueStr = sender->Next();
  if (valueStr == NULL)
	{
		sender->GetSerial()->println("ERROR: no value specified");
		return;
	}
  char* endValueStr = valueStr;
  unsigned long value = strtoul(valueStr, &endValueStr, 10);
  if (valueStr == endValueStr) {
    	sender->GetSerial()->println("ERROR: no valid value specified");
		  return;
  }

  
  if (strncmp(modeStr, "year", 4) == 0) {
    rtc.setYear(value);
  }
  // else if (strncmp(modeStr, "year", 4) == 0) {
  //   DateTime adjusted(value, now.month(), now.day(), now.hour(), now.minute(), now.second());
  //   rtc.adjust(adjusted);
  // }
  else if (strncmp(modeStr, "month", 5) == 0) {
    rtc.setMonth(value);
  }
  else if (strncmp(modeStr, "day", 3) == 0) {
    rtc.setDate(value);
  }
  else if (strncmp(modeStr, "hour", 4) == 0) {
    rtc.setHour(value);
  }
  else if (strncmp(modeStr, "minute", 6) == 0) {
    rtc.setMinute(value);
  }
  else if (strncmp(modeStr, "second", 6) == 0) {
    rtc.setSecond(value);
  }
}
SerialCommand cmd_setTime("settime", setTime);


void cmdUnrecognizedHandler(SerialCommands* sender, const char* cmd)
{
	sender->GetSerial()->print("Unrecognized command [");
	sender->GetSerial()->print(cmd);
	sender->GetSerial()->println("]");
	sender->GetSerial()->println("\r\n");
}



void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  Wire.begin();
  pinMode(backPin, OUTPUT);
  pinMode(frontPin, OUTPUT);

  serial_commands_.SetDefaultHandler(cmdUnrecognizedHandler);
	serial_commands_.AddCommand(&cmd_setMaxDistance);
	serial_commands_.AddCommand(&cmd_getMaxDistance);
	serial_commands_.AddCommand(&cmd_getDistance);
	serial_commands_.AddCommand(&cmd_getTime);
	serial_commands_.AddCommand(&cmd_setTime);

  
}

void loop() {
  
  usonic_1_distance = ultrasonic_1.read();
  //frontWarning = usonic_1_distance < maxDistance;
  //digitalWrite(frontPin, frontWarning);
  //Serial.print("Front Warning: ");
  //Serial.print(frontWarning);
  delay(500);
  if (usonic_1_distance < maxDistance) {
    digitalWrite(13, HIGH);
  }
  else {
    digitalWrite(13, LOW);
  }

  Serial.print("Distance from sensor 1: ");
  Serial.print(usonic_1_distance);
  Serial.println(" cm");
  delay(500);


  usonic_2_distance = ultrasonic_2.read();
  if (usonic_2_distance < maxDistance) {
    digitalWrite(13, HIGH);
  }
  else {
    digitalWrite(13, LOW);
  }
  //backWarning = usonic_2_distance < maxDistance;
  //digitalWrite(backPin, backWarning);
  //Serial.print("Back Warning: ");
  //Serial.print(backWarning);
  delay(500);

  Serial.print("Distance from sensor 2: ");
  Serial.print(usonic_2_distance);
  Serial.println(" cm");
  delay(500);

  serial_commands_.ReadSerial();

  delay(1000);  
}

/*#include <Arduino.h>
void setup() {
  // start serial port at 9600 bps:
  Serial.begin(9600);
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  while (!Serial) {
    ; // wait for serial port to connect.
  }

}

void loop() {
  char buffer[16];
  // if we get a command, turn the LED on or off:
  if (Serial.available() > 0) {
    int size = Serial.readBytesUntil('\n', buffer, 12);
    if (buffer[0] == 'Y') {
      digitalWrite(LED_BUILTIN, HIGH);
    }
    if (buffer[0] == 'N') {
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}*/