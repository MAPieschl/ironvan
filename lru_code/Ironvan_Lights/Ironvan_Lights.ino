/*
 * Ironvan Lighting System v0.1
 * 
 * PIN ASSIGNMENT:
 * 
 *  CONTROL
 *  
 *    CLK_1 - CTRL5_1 - D0  - PD0 - PCINT16    (terminal closest to the linear regulator)
 *    DT_1  - CTRL5_2 - D1  - PD1 - PCINT17
 *    SW_1  - CTRL4_1 - D2  - PD2 - PCINT18
 *    
 *    CLK_2 - CTRL4_2 - D4  - PD4 - PCINT20
 *    DT_2  - CTRL3_1 - D5  - PD5 - PCINT21
 *    SW_2  - CTRL3_2 - D6  - PD6 - PCINT22
 *    
 *    CLK_3 - CTRL2_1 - D7  - PD7 - PCINT23
 *    DT_3  - CTRL2_2 - D8  - PB0 - PCINT0
 *    SW_3  - CTRL1_1 - D13 - PB5 - PCINT5
 *    
 *    MISC  - CTRL1_2 - D12 - PB4 - PCINT4
 *
 *  FEEDBACK
 *  
 *    LS_1  - ADC3    - A3  - PC3 - PCINT11
 *    LS_2  - ADC2    - A2  - PC2 - PCINT10
 *    LS_3  - ADC1    - A1  - PC1 - PCINT9
 *    LS_4  - ADC0    - A0  - PC0 - PCINT8
 *    
 *  OUTPUT
 *  
 *    LS_1  -         - D11 - PB3
 *    LS_2  -         - D10 - PB2
 *    LS_3  -         - D9  - PB1
 *    LS_4  -         - D3  - PD3
 *    
 * ENCODER <-> LS ASSIGNMENT:
 * 
 *  ENCODER 1 <-> LS_1 (dining room) & LS_2 (kitchen)
 *    SINGLE CLICK:   ON/OFF
 *    CW TURN:        INCREASE BRIGHTNESS
 *    CCW TURN:       DECREASE BRIGHTNESS
 *    
 *  ENCODER 2 <-> LS_3 (bedroom)
 *    SINGLE CLICK:   ON/OFF
 *    CW TURN:        INCREASE BRIGHTNESS
 *    CCW TURN:       DECREASE BRIGHTNESS
 *    
 *  ENCODER 3 <-> LS_4 (bathroom)
 *    SINGLE CLICK:   ON/OFF
 *    CW TURN:        INCREASE BRIGHTNESS
 *    CCW TURN:       DECREASE BRIGHTNESS
 *  
 */

// CONTROL VARIABLES

//  Encoder 1
byte clk_1 = 0b00000001;   // PD0 - PCINT16
byte dt_1 = 0b00000010;    // PD1 - PCINT17
byte sw_1 = 0b00000100;    // PD2 - PCINT18
bool readyTurn_1 = false;  // false - no initial direction detected / true - initial direction detected
byte step_1 = 5;           // Step size for each pulse sequence of the encoder
int dir_1 = 1;             // 1 = CW -> CLK followed by DT / -1 = CW -> DT followed by CLK
byte max_1 = 255;          // Maximum value of lights controlled by encoder 1
byte min_1 = 5;            // Minimum value of lights controlled by encoder 1

//  Encoder 2
byte clk_2 = 0b00010000;   // PD4 - PCINT20
byte dt_2 = 0b00100000;    // PD5 - PCINT21
byte sw_2 = 0b01000000;    // PD6 - PCINT22
bool readyTurn_2 = false;  // false - no initial direction detected / true - initial direction detected
byte step_2 = 5;           // Step size for each pulse sequence of the encoder
int dir_2 = 1;             // 1 = CW -> CLK followed by DT / -1 = CW -> DT followed by CLK
byte max_2 = 255;          // Maximum value of lights controlled by encoder 2
byte min_2 = 5;            // Minimum value of lights controlled by encoder 2

//  Encoder 3
byte clk_3 = 0b10000000;   // PD7 - PCINT23
byte dt_3 = 0b00000001;    // PB0 - PCINT0
byte sw_3 = 0b00100000;    // PB5 - PCINT5
bool readyTurn_3 = false;  // false - no initial direction detected / true - initial direction detected
byte step_3 = 5;           // Step size for each pulse sequence of the encoder
int dir_3 = 1;             // 1 = CW -> CLK followed by DT / -1 = CW -> DT followed by CLK
byte max_3 = 255;          // Maximum value of lights controlled by encoder 3
byte min_3 = 5;            // Minimum value of lights controlled by encoder 3

// Pin Masks - Use to mask pins to ensure only interrupt-enabled pins in each port are identified - apply a '1' to all interrupt-enabled pins
byte portBmask = 00110001; // PB0, PB4, and PB5 enabled (see PIN ASSIGNMENT above)
byte portCmask = 00000000; // No Port C pins in use for interrupts
byte portDmask = 11110111; // PD7, PD6, PD5, PD4, PD2, PD1, and PD0 enabled (see PIN ASSIGNMENT above)

//  Volatile Port Variables
volatile byte portBprev;   // Previous state of Port B
volatile byte portCprev;   // -- NOT USED - Use if enabling ADC interrupts -- Previous state of Port C
volatile byte portDprev;   // Previous state of Port D

volatile byte pinIdent;    // byte used to identify which pin caused interrupt

// Debounce Variables
unsigned long lastPress;   // Stores the millis() value at the last time a valid SW interrupt was processed
int debounceDelay = 1000;  // Minimum number of milliseconds between SW activations

// FEEDBACK VARIABLES

//  ADC3 (LS_1)
int pin_ADC3_LS_1 = A3;
int pin_ADC2_LS_2 = A2;
int pin_ADC1_LS_3 = A1;
int pin_ADC0_LS_4 = A0;

// OUTPUT VARIABLES

//   LS_1
int pin_LS_1 = 11;
bool currentState_LS_1 = false;           // false - off / true - on
byte dutyCycle_LS_1 = 0;                  // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_2
int pin_LS_2 = 10;
bool currentState_LS_2 = false;           // false - off / true - on
byte dutyCycle_LS_3 = 0;                  // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_3
int pin_LS_3 = 9;
bool currentState_LS_3 = false;           // false - off / true - on
byte dutyCycle_LS_3 = 0;                  // Current duty cycle -> 0 = 0% & 255 = 100%

//   LS_4
int pin_LS_4 = 3;
bool currentState_LS_4 = false;           // false - off / true - on
byte dutyCycle_LS_4 = 0;                  // Current duty cycle -> 0 = 0% & 255 = 100%

void setup() {
  // CONTROL PIN INITIALIZATION
  pinMode(0, INPUT);
  pinMode(1, INPUT);
  pinMode(2, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);

  // FEEDBACK PIN INITIALIZATION
  pinMode(pin_ADC3_LS_1, INPUT);
  pinMode(pin_ADC2_LS_2, INPUT);
  pinMode(pin_ADC1_LS_3, INPUT);
  pinMode(pin_ADC0_LS_4, INPUT);

  // OUTPUT PIN INITIALIZATION
  pinMode(pin_LS_1, OUTPUT);
  pinMode(pin_LS_2, OUTPUT);
  pinMode(pin_LS_3, OUTPUT);
  pinMode(pin_LS_4, OUTPUT);

  // INTERRUPT INITIALIZATION
  sei();                                            // Global Interrupt Enable
  PCICR |= (1<<PCIE2) | (1<<PCIE1) | (1<<PCIE0);    // Pin change interrupt enable (PCINT23...16) | (PCINT14...8) | (PCINT7...0)
  PCMSK2 = portDmask;                               // Pin change interrupt enable for listed pins corresponding to PCIE2 (PORT D)
  PCMSK1 = portCmask;                               // Pin change interrupt enable for listed pins corresponding to PCIE1 (PORT C)
  PCMSK0 = portBmask;                               // Pin change interrupt enable for listed pins corresponding to PCIE0 (PORT B)

  // Determine initial state of ports
  portDprev = PIND & portDmask;
  portCprev = PINC & portCmask;
  portBprev = PINB & portBmask;
}

void loop() {
  // Add ADC read & PWM adjust code
  delay(10);
}


ISR (PCINT2_vect){
  // PORT D INTERRUPT

  /*
   * ENCODER <-> LS Interrupt sequence:
   * 1. Apply mask to PIND (readable Port D input pin register) to isolate interruptable pins, compare (XOR) with previous state to identify changed pin.
   * 2. Identify if CLK or DT caused the interrupt to occur for one of the encoders. This signifies that the encoder is being turned.
   *    Since direction is determined by the sequence of the CLK and DT pulses, readyTurn = false signifies that the initial pulse has not yet been detected.
   *    If readyTurn is false and a CLK or DT signal is detected, readyTurn is set to true until the next pulse is detected.
   * 3. If readyTurn = true (signaling that either a CLK or DT signal has been detected and the controller is awaiting the second pulse to determine direction),
   *    the detection of CLK or DT will determine the direction and cause the dutyCycle to increment or decrement by step_n according to the value of dir_n.
   *    No changes will occur if the resulting value is less than min_n or greater than max_n.
   * 4. If a SW signal is detected and the time elapsed since the previous valid activation ('lastPress') exceeds the debounce delay, the respective currentState_LS_n
   *    is cycled. All pending turns (readyTurn_n = true) are cancelled.
   *    NOTE:  lastPress is shared by all encoders. This will cause all encoders to blank for the length of debounceDelay after any single SW is activated.
   * 5. Assign either the commanded dutyCycle or an 'off' command (dutyCycle = 0) to each LS_n.
   */
   
  // -- STEP 1 -- //
  
  // Determine which pin caused interrupt
  pinIdent = portDprev ^ (portDmask & PIND)

  // -- STEP 2 -- //
  
  // Identify if CLK_1 or DT_1 is independently affected (signaling that the next pin change is a CW or CCW turn)
  if((pinIdent == clk_1 || pinIdent == dt_1) && readyTurn_1 == false){
    readyTurn_1 = true;
  }
  
  // Identify if CLK_2 or DT_2 is independently affected (singaling that the next pin change is a CW or CCW turn)
  else if((pinIdent == clk_2 || pinIdent == dt_2) && readyTurn_2 == false){
    readyTurn_2 = true;
  }
  
  // Identify if CLK_3 is independently affected (singaling that the next pin change is a CW or CCW turn -- DT_1 is on Port B)
  else if(pinIdent == clk_3 && readyTurn_3 == false){
    readyTurn_3 = true;
  }

  // -- STEP 3 -- //

  // ENCODER 1 turn direction detection & corresponding dutyCycle adjustment
  else if(pinIdent == dt_1 && readyTurn_1 == true){
    if(currentState_LS_1 == true){
      dutyCycle_LS_1 += dir_1*step_1;
    }
    if(currentState_LS_2 == true){
      dutyCycle_LS_2 += dir_1*step_1;
    }
    readyTurn_1 = false;
  }

  else if(pinIdent == clk_1 && readyTurn_1 == true){
    if(currentState_LS_1 == true){
      dutyCycle_LS_1 -= dir_1*step_1;
    }
    if(currentState_LS_2 == true){
      dutyCycle_LS_2 -= dir_1*step_1;
    }
    readyTurn_1 = false;
  }

  // ENCODER 2 turn direction detection & corresponding dutyCycle adjustment
  else if(pinIdent == dt_2 && readyTurn_2 == true){
    if(currentState_LS_3 == true){
      dutyCycle_LS_3 += dir_3*step_3;
    }
    readyTurn_2 = false;
  }

  else if(pinIdent == clk_2 && readyTurn_2 == true){
    if(currentState_LS_3 == true){
      dutyCycle_LS_3 -= dir_3*step_3;
    }
    readyTurn_2 = false;
  }

  // ENCODER 3 turn direction detection & corresponding dutyCycle adjustment
  else if(pinIdent == clk_3 && readyTurn_3 == true){
    if(currentState_LS_4 == true){
      dutyCycle_LS_4 -= dir_4*step_4;
    }
    readyTurn_3 = false;
  }

  // -- STEP 4 -- //

  else if(pinIdent == sw_1){
    if(millis() - lastPress > debounceDelay){
      currentState_LS_1 ^= currentState_LS_1;
      currentState_LS_2 ^= currentState_LS_2;
      lastPress = millis()
    }
    else if(millis() - lastPress < 0){
      lastPress = millis()                    // Ensures SW continues operating after millis rollover (2^32 ms or ~50 days)
    }
    readyTurn_1 = false;
  }

  else if(pinIdent == sw_2){
    if(millis() - lastPress > debounceDelay){
      currentState_LS_3 ^= currentState_LS_3;
      lastPress = millis()
    }
    else if(millis() - lastPress < 0){
      lastPress = millis()                    // Ensures SW continues operating after millis rollover (2^32 ms or ~50 days)
    }
    readyTurn_2 = false;
  }

  // -- STEP 5 -- //
  
  // Reassign duty cycle to each LS
  if(currentState_LS_1 == true){
    analogWrite(pin_LS_1, dutyCycle_LS_1);
  }
  else{
    analogWrite(pin_LS_1, 0);
  }
  
  if(currentState_LS_2 == true){
    analogWrite(pin_LS_2, dutyCycle_LS_2);
  }
  else{
    analogWrite(pin_LS_2, 0);
  }
  
  if(currentState_LS_3 == true){
    analogWrite(pin_LS_3, dutyCycle_LS_3);
  }
  else{
    analogWrite(pin_LS_3, 0); 
  }
  
  if(currentState_LS_4 == true){
    analogWrite(pin_LS_4, dutyCycle_LS_4);
  }
  else{
    analogWrite(pin_LS_4, 0);
  }
}

ISR (PCINT1_vect){
  // PORT C INTERRUPT
  
}

ISR (PCINT0_vect){
  // PORT B INTERRUPT

  /*
   * ENCODER <-> LS Interrupt sequence:
   * 1. Apply mask to PIND (readable Port D input pin register) to isolate interruptable pins, compare (XOR) with previous state to identify changed pin.
   * 2. Identify if CLK or DT caused the interrupt to occur for one of the encoders. This signifies that the encoder is being turned.
   *    Since direction is determined by the sequence of the CLK and DT pulses, readyTurn = false signifies that the initial pulse has not yet been detected.
   *    If readyTurn is false and a CLK or DT signal is detected, readyTurn is set to true until the next pulse is detected.
   * 3. If readyTurn = true (signaling that either a CLK or DT signal has been detected and the controller is awaiting the second pulse to determine direction),
   *    the detection of CLK or DT will determine the direction and cause the dutyCycle to increment or decrement by step_n according to the value of dir_n.
   *    No changes will occur if the resulting value is less than min_n or greater than max_n.
   * 4. If a SW signal is detected and the time elapsed since the previous valid activation ('lastPress') exceeds the debounce delay, the respective currentState_LS_n
   *    is cycled. All pending turns (readyTurn_n = true) are cancelled.
   *    NOTE:  lastPress is shared by all encoders. This will cause all encoders to blank for the length of debounceDelay after any single SW is activated.
   * 5. Assign either the commanded dutyCycle or an 'off' command (dutyCycle = 0) to each LS_n.
   */
   
  // -- STEP 1 -- //
  
  // Determine which pin caused interrupt
  pinIdent = portBprev ^ (portBmask & PINB)

  // -- STEP 2 -- //

  // Identify if DT_3 is independently affected (signaling that the next pin change is a CW or CCW turn - CLK_1 is on Port D)
  if(pinIdent == dt_3 && readyTurn_3 == false){
    readyTurn_3 = true;
  }
  
  // -- STEP 3 -- //

  // ENCODER 3 turn direction detection & corresponding dutyCycle adjustment
  else if(pinIdent == dt_3 && readyTurn_3 == true){
    if(currentState_LS_4 == true){
      dutyCycle_LS_4 += dir_4*step_4;
    }
    readyTurn_3 = false;
  }

  // -- STEP 4 -- //
  
  else if(pinIdent == sw_3){
    if(millis() - lastPress > debounceDelay){
      currentState_LS_4 ^= currentState_LS_4;
      lastPress = millis()
    }
    else if(millis() - lastPress < 0){
      lastPress = millis()                    // Ensures SW continues operating after millis rollover (2^32 ms or ~50 days)
    }
    readyTurn_3 = false;
  }

  // -- STEP 5 -- //
  
  // Reassign duty cycle to each LS
  if(currentState_LS_1 == true){
    analogWrite(pin_LS_1, dutyCycle_LS_1);
  }
  else{
    analogWrite(pin_LS_1, 0);
  }
  
  if(currentState_LS_2 == true){
    analogWrite(pin_LS_2, dutyCycle_LS_2);
  }
  else{
    analogWrite(pin_LS_2, 0);
  }
  
  if(currentState_LS_3 == true){
    analogWrite(pin_LS_3, dutyCycle_LS_3);
  }
  else{
    analogWrite(pin_LS_3, 0); 
  }
  
  if(currentState_LS_4 == true){
    analogWrite(pin_LS_4, dutyCycle_LS_4);
  }
  else{
    analogWrite(pin_LS_4, 0);
  }
}
