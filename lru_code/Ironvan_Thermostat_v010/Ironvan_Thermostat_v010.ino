#include <Wire.h>

// Constant device address set
const byte DEVICE_ADDR = 0x08;

// Device type is a device signature to signify to the control center the commands that the board will accept:
//    temp - board type "thermostat"
//    b100 - PCB version 1.0.0
//    v010 - firmware version 0.1.0
// NOTE:  All DEVICE_TYPE strings will be 14 bytes (ASCII)
const char DEVICE_TYPE[] = "temp_b100_v010";

// Request number used to determine what value to return to the master. Value is set in receiveEvent() and used in requestEvent(). DEFAULT:  Send DEVICE_TYPE
byte requestNumber;

//
bool pinValues;

void setup()
{
  // -- Enable pull-up resistors on I2C line --

  // 0 - pull-up resistors enabled / 1 - pull-up resistors disabled
  MCUCR &= ~(1 << PUD);

  // With DDCn set to 0 (input), 0 - pull-up disabled for pin / 1 - pull-up enabled for pin
  PORTC |= (1 << PC5 | 1 << PC4);

  // 0 - pin configured as input / 1 - pin configured as output
  DDRC &= ~(1 << DDC5 | 1 << DDC4);

  // -- Initialize I2C --

  // Set device address (declared above)
  Wire.begin(DEVICE_ADDR);

  // When a transmission is received at DEVICE_ADDR, receiveEvent() interrupt will be triggered
  Wire.onReceive(receiveEvent);

  // When a transmission is requested from device at DEVICE_ADDR, requestEvent() interrupt will be triggered
  Wire.onRequest(requestEvent);

  // -- Enable control signal pins --
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
}

void loop()
{
  // -- Constantly read pin values --
  pinValues = PINB;
}

void receiveEvent(int howMany)
{

  while (Wire.available())
  {
    byte msg = Wire.read();

    switch (msg)
    {

      // COMMAND STRUCTURE
      // 0x00 - 0x07:  Write commands directly to the controller to trigger relays
      // Default:  Store value written by master to the global variable requestNumber. This when sending SMBus commands from the Python master script, a value is written to the slave prior to requesting a value. For example:
      //
      //  bus.read_i2c_block_data(8, 10, 14)
      //
      // This command will first write the value 10 to the slave at address 8, then request a block of data containing 14 bytes. The specific requestNumber values are broken out in requestEvent().

    case 0x00:
      // Fan-low on
      digitalWrite(12, HIGH);
      break;

    case 0x01:
      // Fan-low off
      digitalWrite(12, LOW);
      break;

    case 0x02:
      // Fan-high on
      digitalWrite(11, HIGH);
      break;

    case 0x03:
      // Fan-high off
      digitalWrite(11, LOW);
      break;

    case 0x04:
      // AC on (& fan-high on)
      digitalWrite(11, HIGH);
      digitalWrite(10, HIGH);
      break;

    case 0x05:
      // AC off (& fan-high off)
      digitalWrite(10, LOW);
      digitalWrite(11, LOW);
      break;

    case 0x06:
      // Heat pump on (& fan-high on)
      digitalWrite(11, HIGH);
      digitalWrite(9, HIGH);
      break;

    case 0x07:
      // Heat pump off (& fan-high off)
      digitalWrite(9, LOW);
      digitalWrite(11, LOW);
      break;

    default:
      requestNumber = msg;
      break;
    }
  }
}

void requestEvent()
{
  switch (requestNumber)
  {
  case 0x20:
    Wire.write(DEVICE_TYPE);
    break;
  case 0x21:
    Wire.write(PINB);
  }
}
