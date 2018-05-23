#include <QList.h>

//Digital outputs
int A1A = 6;            //for control of motor A
int A1B = 5;    
int B1A = 10;           //for control of motor B
int B1B = 9;

//Analogue sensors
int potentiometer = A0;           //for displacement measurement
int tensometerIn = A1;  //for closed loop control  

//Digital sensors
//for the microswitches?


//CONSTANTS
int potSamples = 5;
float kinematicsSampleTimeLength = 0.1; //seconds
float kinematicsSampleInterval = 20; //millisecond
int kinematicsSampleNumber;
float e = 2.71828;
float pi = 3.14159;

//Parameters
float k1 = 1;           //for the stomach sphincter
float mean1 = 1;
float variance1 = 1;

float k2 = 1;           //for the mouth sphincter
float mean2 = 2;
float variance2 = 2;

// VARIABLES
float k_p, k_i, k_d;
volatile QList<int> pot, tension; //so that we can take a time average of the readings in order to remove noise
volatile QList<float> displacement, velocity, acceleration;
int maxDisplacement, timeoutSec;

// SENSORS
int getPotentiometer {
  return analogRead(potentiometer);
}

int getTensometer() {
  return analogRead(tensometerIn);
}

void readSensors() {
  tension = getTensometer();
  pot = getPotentiometer();
}

void recordEncoder() {
  encoder1.pop_front();
  encoder1.push_back(millis());
  encoderTicks++;
  //Serial.println(encoderTicks);
  int timeInterval = encoder1[encoderSamples-1] - encoder1[encoderSamples-2];
  //Serial.println(timeInterval);
  updateKinematics(timeInterval);
  //Serial.println(calculateDisplacement());
  //TBD: Forward and backwards counting
}


// ACTUATORS
void stopMotor() {
  analogWrite(A1A, 0);
  analogWrite(A1B, 0);
  analogWrite(B1A, 0);
  analogWrite(B1B, 0);
}

void brake(byte force) {
  analogWrite(A1A, force);
  analogWrite(A1B, 0);
  analogWrite(B1A, force);
  analogWrite(B1B, 0);
}

void retract() {
  analogWrite(A1A, 100);
  analogWrite(A1B, 0);
  analogWrite(B1A, 160);
  analogWrite(B1B, 0);
}

// CALCULATE PHYSICS


float calculateVelocity(float timeIntervalMillis) {
  // Return angular speed in degrees/second for now
  return (displacement[kinematicsSampleNumber-1] - displacement[kinematicsSampleNumber-2])/(timeIntervalMillis/1000);
}

float calculateDisplacement(void){
  // Return angular displacement in degrees for now
  return encoderTicks*15;
}

float calculateAcceleration(float timeIntervalMillis) {
  // Return angular acceleration in degrees/second^2 for now
  return (velocity[kinematicsSampleNumber-1] - velocity[kinematicsSampleNumber-2])/(timeIntervalMillis/1000);
}

void updateKinematics(float timeIntervalMillis) {
  displacement.push_back(calculateDisplacement());
  displacement.pop_front();
  //Serial.print(displacement[0]);
  for (int i = 0; i < kinematicsSampleNumber; i++) {  //just printing out all the values stored in the stack
    Serial.print(displacement[i]);
    Serial.print(" ");
  }
  Serial.println();
  velocity.push_back(calculateVelocity(timeIntervalMillis)); 
  velocity.pop_front();
  for (int i = 0; i < kinematicsSampleNumber; i++) {
    Serial.print(velocity[i]);
    Serial.print(" ");
  }
  Serial.println();
  acceleration.push_back(calculateAcceleration(timeIntervalMillis)); //puts the newest value on the back of the list?
  acceleration.pop_front();                                          //could we also do pop_back and push_front?
}

float gaussian(float x, float mean, float variance) {
  return 1/sqrt(2*pi*variance)*pow(e, 1/(2*sq(variance))*sq(x-mean));
}

float modelForce(float v, float d) {
  float k1 = 1;
  float k2 = 1;
  float mean1 = 1;
  float mean2 = 2;
  float variance1 = 1;
  float variance2 = 2;
  return v*(k1*gaussian(d, mean1, variance1) + k2*gaussian(d, mean2, variance2));
}

float controller(float modelForce){
  //TBD
}

void resetVariables() {
  //TBD
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  kinematicsSampleNumber = (int) (kinematicsSampleTimeLength*1000/kinematicsSampleInterval); //=5, same as pot samples number
  pinMode(A1A, OUTPUT); //setting all pins
  pinMode(A1B, OUTPUT);
  pinMode(B1A, OUTPUT);
  pinMode(B1B, OUTPUT);
  pinMode(potentiometer, INPUT);
  pinMode(tensometerIn, INPUT);
  for (int i = 0; i < potSamples; i++){
    encoder1.push_back(0);
  }
  for (int i = 0; i < kinematicsSampleNumber; i++){
    displacement.push_back(0);
    velocity.push_back(0);
    acceleration.push_back(0);
  }
  //attachInterrupt(digitalPinToInterrupt(encoderIn1), recordEncoder, RISING);//we dont need this for a pot right?
  Serial.println("Program start");
}

void loop() {
  // put your main code here, to run repeatedly:
  //Stuff in main loop not permanent for now
  


  
  /*readSensors();
  Serial.print("Tension: ");
  Serial.print(tension);
  Serial.print("\n");
  motorOn();
  motorOff();
  //Serial.println(displacement[kinematicsSampleNumber-1]);
  delay(100);
  */
}

int A1A = 6;    //must all be PWM output pins
int A1B = 5;    //the pin layout has been taken to be how it is on the board
int B1A = 10;
int B1B = 9;

byte force = 255; //force is just the pwm value set from 0-255

void setup() {
  pinMode(A1A, OUTPUT); //setting all pins to output
  pinMode(A1B, OUTPUT);
  pinMode(B1A, OUTPUT);
  pinMode(B1B, OUTPUT);
}


