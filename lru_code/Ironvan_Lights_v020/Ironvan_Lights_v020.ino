/*
 * Ironvan Lighting System v0.2.0
 */

#include <Wire.h>
#include <Arduino.h>
#include <avr/wdt.h>

// I2C VARIABLES

// Constant device address set
const byte DEVICE_ADDR = 0x09;

// Device type is a device signature to signify to the control center the commands that the board will accept:
//    ltsy - board type "lighting systems"
//    b100 - PCB version 1.0.0
//    v020 - firmware version 0.2.0
// NOTE:  All DEVICE_TYPE strings will be 14 bytes (ASCII)
const char DEVICE_TYPE[] = "ltsy_b100_v020";

// Initial check-in (false - awaiting // true - complete)
bool check_in = false;

// Request number used to determine what value to return to the master. Value is set in receiveEvent() and used in requestEvent().
byte requestNumber;

// FEEDBACK VARIABLES
const short ADC_SAMPLES = 10;
short adc_sample_array[4][ADC_SAMPLES] = {0};
short adc_sample_ave[4] = {0};
short adc_on_nominal[4] = {0};
float adc_correction[4] = {1};
short sample_num = 0;

// OUTPUT VARIABLES
constexpr int pin_LS[4] = {11, 10, 9, 3};
uint8_t dutyCycle_LS[4] = {191, 191, 191, 191}; // Current set duty cycle -> 0 = 0% & 255 = 100%
uint8_t corrected_dutyCycle_LS[4] = {191, 191, 191, 191}; // Current corrected duty cycle -> 0 = 0% & 255 = 100%

//   pin_LS_n currently selected by I2C command
int active_LS_pin = 0;

void calibrationSequence()
{
  // Set all light circuits to 100% duty cycle
  analogWrite(pin_LS[0], 255);
  analogWrite(pin_LS[1], 255);
  analogWrite(pin_LS[2], 255);
  analogWrite(pin_LS[3], 255);

  // Start ADC
  ADCSRA |= (1 << ADSC);

  // Wait 0.25 seconds for calibration to complete
  delay(250);

  // Stop ADC
  ADCSRA &= ~(1 << ADSC);

  // Turn off lights and await control center check-in
  analogWrite(pin_LS[0], 0);
  analogWrite(pin_LS[1], 0);
  analogWrite(pin_LS[2], 0);
  analogWrite(pin_LS[3], 0);

  // Reset and stop watchdog timer to await check-in
  //wdt_reset();

  if (check_in == false)
  {
    WDTCSR &= ~(1 << WDE);
  }
}

void setup()
{

  // ------------- Begin Setup -----------------

  // Disable interrupts
  cli();

  // ------------- I2C Setup -----------------

  // -- Enable pull-up resistors on I2C line --

  // 0 - pull-up resistors enabled / 1 - pull-up resistors disabled
  MCUCR &= ~(1 << PUD);

  // With DDCn set to 0 (input), 0 - pull-up disabled for pin / 1 - pull-up enabled for pin
  PORTC |= (1 << PC5) | (1 << PC4);

  // 0 - pin configured as input / 1 - pin configured as output
  DDRC &= ~(1 << DDC5) | ~(1 << DDC4);

  // -- Initialize I2C --

  // Set device address (declared above)
  Wire.begin(DEVICE_ADDR);

  // When a transmission is received at DEVICE_ADDR, receiveEvent() interrupt will be triggered
  Wire.onReceive(receiveEvent);

  // When a transmission is requested from device at DEVICE_ADDR, requestEvent() interrupt will be triggered
  Wire.onRequest(requestEvent);

  // ------------- Lighting Output Setup -----------------

  // OUTPUT PIN INITIALIZATION
  pinMode(pin_LS[0], OUTPUT);
  pinMode(pin_LS[1], OUTPUT);
  pinMode(pin_LS[2], OUTPUT);
  pinMode(pin_LS[3], OUTPUT);
  analogWrite(pin_LS[3], 5);

  // ------------- Feedback ADC Setup -----------------

  // Configure pins

  // AVCC voltage reference / output right aligned / begins on ADCO
  //ADMUX |= (1 << REFS0);

  // ADC enabled / ADC start conversion LOW (begins when set HIGH) / Trigger disabled (single conversion mode) / Interrupt enabled / 62.5kHz clock
  //ADCSRA |= (1 << ADEN) | (1 << ADIE) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);

  // ADCSRB set to defaults - ACME disabled / ADTS ignored

  // ------------- Watchdog Timer Setup -----------------

  // Reset watchdog timer
  //wdt_reset();

  // Clear the system reset flag
  //MCUSR &= ~(1 << WDRF);

  // Begin timed changed sequence (pg 46)
  //WDTCSR |= (1 << WDCE) | (1 << WDE);

  // Set prescaler value (0.5s reset timer)
  //WDTCSR |= (1 << WDE) | (1 << WDP3) | (1 << WDP0);

  // Stop watchdog timer until control center check-in
  //WDTCSR &= ~(1 << WDE);

  wdt_disable();
  delay(3000);
  wdt_enable(WDTO_8S);

  // ------------- Final Setup -----------------

  // Enable interrupts
  sei();

  // Run calibration sequence
  //calibrationSequence();
}

void loop()
{
  // Add ADC read & PWM adjust code
  delay(10);
}

// I2C Interrupt Sequences

void receiveEvent(int howMany)
{

  while (Wire.available())
  {
    byte msg = Wire.read();

    switch (msg)
    {

      // COMMAND STRUCTURE
      // 0x01 - 0x04:  Signal the light targeted by the PWM value (10 - 255) in the second byte of the command.
      // Default:
      //  1. If a light has been signaled for command, the default case will assign the second byte as the PWM value to the pin.
      //  2. If note, it will store value written by master to the global variable requestNumber. This when sending SMBus commands from the Python master script, a value is written to the slave prior to requesting a value. For example:
      //
      //  bus.read_i2c_block_data(8, 10, 14)
      //
      // This command will first write the value 10 to the slave at address 8, then request a block of data containing 14 bytes. The specific requestNumber values are broken out in requestEvent().
      //
      // NOTE:  The light commands (currently 0x01 - 0x04) MUST fall between the off value (0x00) and the minimum value set by the user (normally 0x0A). Otherwise, the PWM signal will not fall to the default case.

    case 0x01:
      active_LS_pin = pin_LS[0];
      break;

    case 0x02:
      active_LS_pin = pin_LS[1];
      break;

    case 0x03:
      active_LS_pin = pin_LS[2];
      break;

    case 0x04:
      active_LS_pin = pin_LS[3];
      break;

    default:
      if (active_LS_pin != 0)
      {

        switch (active_LS_pin)
        {
        case pin_LS[0]:
          dutyCycle_LS[0] = msg;
          break;

        case pin_LS[1]:
          dutyCycle_LS[1] = msg;
          break;

        case pin_LS[2]:
          dutyCycle_LS[2] = msg;
          break;

        case pin_LS[3]:
          dutyCycle_LS[3] = msg;
          break;
        }

        analogWrite(active_LS_pin, msg);

        active_LS_pin = 0;
      }

      else
      {
        requestNumber = msg;
      }

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
    //if(check_in == false){
      //ADCSRA |= (1 << ADSC);
      //WDTCSR |= (1 << WDE);
    //}
    //check_in = true;
    break;
  case 0x21:
    //Wire.write(ADMUX&0b00001111);
    //Wire.write(ADCH);
    //Wire.write(ADCL);
    //Wire.write(dutyCycle_LS[0]);
    //Wire.write(corrected_dutyCycle_LS[0]);
    //Wire.write(dutyCycle_LS[1]);
    //Wire.write(corrected_dutyCycle_LS[1]);
    //Wire.write(dutyCycle_LS[2]);
    //Wire.write(corrected_dutyCycle_LS[2]);
    //Wire.write(dutyCycle_LS[3]);
    //Wire.write(corrected_dutyCycle_LS[3]);
    break;
  case 0x22:
    Wire.write(dutyCycle_LS[0]);
    break;
  case 0x23:
    Wire.write(dutyCycle_LS[1]);
    break;
  case 0x24:
    Wire.write(dutyCycle_LS[2]);
    break;
  case 0x25:
    Wire.write(dutyCycle_LS[3]);
    break;
  }
  wdt_reset();
}

// ADC Interrupt Sequences
ISR(ADC_vect)
{
  byte current_adc = ADMUX & 0b00000011;
  adc_sample_array[current_adc][sample_num] = (ADCH << 8) + ADCL;

  if (sample_num >= ADC_SAMPLES)
  {
    // Esnure ADC is stopped
    ADCSRA &= ~(1 << ADSC);

    // Compute and send correction
    int num_samples_on = 0;
    int sample_accumulator = 0;

    for (byte i = 0; i < ADC_SAMPLES; i++)
    {
      if (adc_sample_array[current_adc][i] > 50)
      {
        // Assumes that any value 0.5A read across the sense resistor means that the circuit is "on"

        sample_accumulator += adc_sample_array[current_adc][i];
        num_samples_on += 1;
      }
    }

    if (num_samples_on != 0)
    {
      adc_sample_ave[current_adc] = sample_accumulator / num_samples_on;

      if (adc_on_nominal[current_adc] != 0)
      {
        adc_correction[current_adc] = adc_sample_ave[current_adc] / adc_on_nominal[current_adc];
      }
      else
      {
        adc_on_nominal[current_adc] = adc_sample_ave[current_adc];
      }

      corrected_dutyCycle_LS[current_adc] = (byte)(dutyCycle_LS[current_adc] / adc_correction[current_adc]);
      if (corrected_dutyCycle_LS[current_adc] > 255)
      {
        corrected_dutyCycle_LS[current_adc] = 255;
      }
    }
    else
    {
      adc_sample_ave[current_adc] = 0;
      corrected_dutyCycle_LS[current_adc] = dutyCycle_LS[current_adc];
    }

    //analogWrite(pin_LS[current_adc], corrected_dutyCycle_LS[current_adc]);
    analogWrite(pin_LS[current_adc], dutyCycle_LS[current_adc]);

    // Reset ADC ISR
    sample_num = 0;
    if (current_adc < 3)
    {
      current_adc += 1;
    }
    else
    {
      current_adc = 0;
    }
    ADMUX &= ~(1 << MUX3 | 1 << MUX2 | 1 << MUX1 | 1 << MUX0);
    ADMUX |= current_adc;
    ADCSRA |= (1 << ADSC);
  }
  else
  {
    sample_num += 1;
    ADCSRA |= (1 << ADSC);
  }
}
