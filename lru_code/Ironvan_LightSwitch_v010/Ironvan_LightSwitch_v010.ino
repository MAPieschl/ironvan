/*
 * Ironvan Light Switch & Thermometer v0.1.0
 *
 *  PIN ASSIGNMENT:
 *
 *  CONTROL
 *
 *    CLK_1 - CTRL5_1 - D0  - PD0 - PCINT16
 *    DT_1  - CTRL5_2 - D1  - PD1 - PCINT17
 *    SW_1  - CTRL4_1 - D2  - PD2 - PCINT18
 *
 *  THERMOMETER
 *
 *    ADC0    - A0  - PC0 - PCINT8
 *
 *  I/O
 *
 *    This module has two distinct functions: a light switch/dimmer and a thermometer.
 *
 *    Light Switch/Dimmer:
 *
 *      The output consists of 2 variable - lightOn and lightChange.
 *
 *        - lightOn - 0 (off) or 1 (on)
 *        - lightChange - number of steps read from rotary encoder since last I2C transmission (signed)
 *
 *      The fastest quarter-turn (5 pulses of a K-040 rotary encoder) made by a human hand is about 0.15 seconds, resulting in a maximum processing time of 30 milliseconds. Since this device will be included on a bus with multiple devices, this means that the device status (request code 0x21) must be requested once every 30 milliseconds.
 */

#include <Wire.h>

// I2C VARIABLES

// Constant device address set
const byte DEVICE_ADDR = 0x0B;

// Device type is a device signature to signify to the control center the commands that the board will accept:
//    ltsy - board type "lighting systems"
//    b100 - PCB version 1.0.0
//    v010 - firmware version 0.1.0
// NOTE:  All DEVICE_TYPE strings will be 14 bytes (ASCII)
const char DEVICE_TYPE[] = "ltsw_b100_v010";

// Request number used to determine what value to return to the master. Value is set in receiveEvent() and used in requestEvent(). DEFAULT:  Send DEVICE_TYPE
byte requestNumber;

// THERMOMETER VARIABLES
const int pin_ADC0_Thermometer = A0;
unsigned short thermometerOutput = 0;

// LIGHT SWITCH VARIABLES

//  Encoder Masks
const byte clk = 0b00000001;     // PD0 - PCINT16
const byte dt = 0b00000010;      // PD1 - PCINT17
const byte sw = 0b00000100;      // PD2 - PCINT18
const byte portDmask = 00000111; // PD2, PD1, and PD0 enabled (see PIN ASSIGNMENT above)

// Rotation variables
bool readyTurnCW = false;
bool readyTurnCCW = false;
volatile byte portDprev; // Previous state of Port D
volatile byte pinIdent;  // byte used to identify which pin caused interrupt

// Debounce Variables
unsigned long lastPress;  // Stores the millis() value at the last time a valid SW interrupt was processed
int debounceDelay = 1000; // Minimum number of milliseconds between SW activations

// Output variables
signed char lightChange = 0; // Number of steps taken since last I2C read
byte lightOn = 0;            // 0 - off / 1 - on

void setup()
{
  // ------------- I2C Setup -----------------

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

  // ------------- Thermometer ADC Setup -----------------

  // THERMOMETER PIN INITIALIZATION
  pinMode(pin_ADC0_Thermometer, INPUT);

  // ------------- Light Switch Pin Setup -----------------

  // Global interrupt enable
  sei();

  // Pin change interrupt enable (PCINT23...16)
  PCICR |= (1 << PCIE2);
  PCMSK2 = portDmask;

  // Read initial state of port
  portDprev = PIND & portDmask;
}

void loop()
{
  thermometerOutput = analogRead(pin_ADC0_Thermometer);
  delay(10);
}

void receiveEvent(int howMany)
{

  while (Wire.available())
  {
    byte msg = Wire.read();
  }

  // No commands currently programmed
}

void requestEvent()
{
  switch (requestNumber)
  {
  // device_type
  case 0x20:
    Wire.write(DEVICE_TYPE);
    break;

  // device_status
  case 0x21:
    Wire.write({(lightOn,
                 lightChange,
                 thermometerOutput >> 8) &
                    3,
                thermometerOutput & 255});
    break;
  }

  ISR(PCINT2_vect)
  {
    // PORT D INTERRUPT

    /*
     * ENCODER <-> LS Interrupt sequence:
     * 1. Apply mask to PIND (readable Port D input pin register) to isolate interruptable pins, compare (XOR) with previous state to identify changed pin.
     * 2. If a SW signal is detected and the time elapsed since the previous valid activation ('lastPress') exceeds the debounce delay, then lightOn is cycled. Pending turns (readyTurn = true) are cancelled.
     * 3. Identify if CLK or DT caused the interrupt. This signifies that the encoder is being turned.
     *    Since direction is determined by the sequence of the CLK and DT pulses, readyTurn = false signifies that the initial pulse has not yet been detected.
     *    If readyTurn is false and a CLK or DT signal is detected, readyTurn is set to true until the next pulse is detected.
     * 4. If readyTurn = true (signaling that either a CLK or DT signal has been detected and the controller is awaiting the second pulse to determine direction), the detection of CLK or DT will determine the direction and increment or decrement the lightChange value.
     */

    // -- STEP 1 -- //

    // Determine which pin caused interrupt
    pinIdent = portDprev ^ (portDmask & PIND);

    // -- STEP 2 -- //

    // Identify switch activation and toggle light state (lightOn)

    if (pinIdent == sw)
    {
      if (millis() - lastPress > debounceDelay)
      {
        lightOn ^= lightOn;
        lastPress = millis()
      }
      else if (millis() - lastPress < 0)
      {
        lastPress = millis() // Ensures SW continues operating after millis rollover (2^32 ms or ~50 days)
      }
      readyTurnCW = false;
      readyTurnCCW = false;
    }

    // -- STEP 3 -- //

    // Identify if CLK or DT is independently affected (signaling that the next pin change is a CW or CCW turn)
    else if (readyTurnCW == false && readyTurnCCW == false)
    {
      switch (pinIdent)
      {
      case clk:
        readyTurnCW = true;
        break;
      case dt:
        readyTurnCCW = true;
        break;
      }
    }

    // -- STEP 4 -- //

    // ENCODER turn direction detection & corresponding lightChange

    // CW turn (CLK followed by DT)
    else if (pinIdent == dt && readyTurnCW == true)
    {
      if (lightOn == true)
      {
        lightChange += 1;
      }
      readyTurnCW = false;
      readyTurnCCW = false;
    }

    // CCW turn (DT followed by CLK)
    else if (pinIdent == clk && readyTurnCCW == true)
    {
      if (lightOn == true)
      {
        lightChange -= 1;
      }
      readyTurnCW = false;
      readyTurnCCW = false;
    }
  }