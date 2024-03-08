/*
 * Ironvan Lighting System v0.1.0
 */

#include <Wire.h>

// I2C VARIABLES

// Constant device address set
const byte DEVICE_ADDR = 0x18;

// Device type is a device signature to signify to the control center the commands that the board will accept:
//    ltsy - board type "lighting systems"
//    b100 - PCB version 1.0.0
//    v010 - firmware version 0.1.0
// NOTE:  All DEVICE_TYPE strings will be 14 bytes (ASCII)
const char DEVICE_TYPE[] = "ltsy_b100_v010";

// Request number used to determine what value to return to the master. Value is set in receiveEvent() and used in requestEvent(). DEFAULT:  Send DEVICE_TYPE
byte requestNumber;

// FEEDBACK VARIABLES

//  ADC3 (LS_1)
int pin_ADC3_LS_1 = A3;
int pin_ADC2_LS_2 = A2;
int pin_ADC1_LS_3 = A1;
int pin_ADC0_LS_4 = A0;

// OUTPUT VARIABLES

//   LS_1
int pin_LS_1 = 11;
byte dutyCycle_LS_1 = 0; // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_2
int pin_LS_2 = 10;
byte dutyCycle_LS_3 = 0; // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_3
int pin_LS_3 = 9;
byte dutyCycle_LS_3 = 0; // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_4
int pin_LS_4 = 3;
byte dutyCycle_LS_4 = 0; // Current duty cycle -> 0 = 0% & 255 = 100%

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

    // ------------- Feedback ADC Setup -----------------

    // FEEDBACK PIN INITIALIZATION
    pinMode(pin_ADC3_LS_1, INPUT);
    pinMode(pin_ADC2_LS_2, INPUT);
    pinMode(pin_ADC1_LS_3, INPUT);
    pinMode(pin_ADC0_LS_4, INPUT);

    // ------------- Lighting Output Setup -----------------

    // OUTPUT PIN INITIALIZATION
    pinMode(pin_LS_1, OUTPUT);
    pinMode(pin_LS_2, OUTPUT);
    pinMode(pin_LS_3, OUTPUT);
    pinMode(pin_LS_4, OUTPUT);
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
            // 0x00 - 0x03:  Write commands directly to the controller to change light PWM signals
            // Default:  Store value written by master to the global variable requestNumber. This when sending SMBus commands from the Python master script, a value is written to the slave prior to requesting a value. For example:
            //
            //  bus.read_i2c_block_data(8, 10, 14)
            //
            // This command will first write the value 10 to the slave at address 8, then request a block of data containing 14 bytes. The specific requestNumber values are broken out in requestEvent().

        case 0x00:
            // Determine how I2C block data is sent - assign PWM value to pin between 0 & 255

            // Temp code -> toggle light on and off using edge values 0 & 255 using the ADC variables (incorrectly)

            pin_ADC3_LS_1 = analogRead(pin_LS_1);
            if (pin_ADC3_LS_1 >= 512)
            {
                analogWrite(pin_LS_1, 0);
            }
            else
            {
                analogWrite(pin_LS_1, 255);
            }
            break;

        case 0x01:
            // Determine how I2C block data is sent - assign PWM value to pin between 0 & 255

            // Temp code -> toggle light on and off using edge values 0 & 255 using the ADC variables (incorrectly)

            pin_ADC2_LS_2 = analogRead(pin_LS_2);
            if (pin_ADC2_LS_2 >= 512)
            {
                analogWrite(pin_LS_2, 0);
            }
            else
            {
                analogWrite(pin_LS_2, 255);
            }
            break;

        case 0x02:
            // Determine how I2C block data is sent - assign PWM value to pin between 0 & 255

            // Temp code -> toggle light on and off using edge values 0 & 255 using the ADC variables (incorrectly)

            pin_ADC1_LS_3 = analogRead(pin_LS_3);
            if (pin_ADC1_LS_3 >= 512)
            {
                analogWrite(pin_LS_3, 0);
            }
            else
            {
                analogWrite(pin_LS_3, 255);
            }
            break;

        case 0x03:
            // Determine how I2C block data is sent - assign PWM value to pin between 0 & 255

            // Temp code -> toggle light on and off using edge values 0 & 255 using the ADC variables (incorrectly)

            pin_ADC0_LS_4 = analogRead(pin_LS_4);
            if (pin_ADC0_LS_4 >= 512)
            {
                analogWrite(pin_LS_4, 0);
            }
            else
            {
                analogWrite(pin_LS_4, 255);
            }
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
    }
