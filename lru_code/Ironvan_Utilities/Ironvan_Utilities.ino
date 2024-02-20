#include <Wire.h>

char msg;

void setup() {
  // put your setup code here, to run once:

  // Enable pull-up resistors on I2C line
  MCUCR &= ~(1<<PUD);
  PORTC |= (1<<PC5 | 1<<PC4);
  DDRC &= ~(1<<DDC5 | 1<<DDC4);
  
  Wire.begin(8);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(100);
}

void receiveEvent(int howMany){
  while(Wire.available()){
    msg = Wire.read();
    
    switch(msg){
      case 0x00:
        digitalWrite(12, HIGH);
        break;

      case 0x01:
        digitalWrite(12, LOW);
        break;

      case 0x02:
        digitalWrite(11, LOW);
        break;

      case 0x03:
        digitalWrite(11, HIGH);
        break;

      case 0x04:
        digitalWrite(10, LOW);
        break;

      case 0x05:
        digitalWrite(10, HIGH);
        break;

      case 0x06:
        digitalWrite(9, HIGH);
        break;

      case 0x07:
        digitalWrite(9, LOW);
        break;
    }
  }
}

void requestEvent(){
  Wire.write(msg);
}
