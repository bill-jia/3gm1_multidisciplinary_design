#include <QList.h>

int encoderIn1 = 2;
int encoderIn2 = 3;
int motorOut = 4;

int tensometerIn = 0;
int coilOut = 5;
int j = 0;

//CONSTANTS
int encoderSamples = 20;
float e = 2.71828;
float pi = 3.14159;

// VARIABLES
float k_p, k_i, k_d;
volatile QList<int> encoder1, encoder2;
int tensiontest[250];
int tension, displacement, velocity, acceleration;
int maxDisplacement, timeoutSec;

// SENSORS
int getEncoder1() {
  return digitalRead(encoderIn1);
}

int getEncoder2(){
  return digitalRead(encoderIn2);
}

int getTensometer(){
  return analogRead(tensometerIn);
}

void readSensors() {
  tension = getTensometer();
}

void recordEncoder() {
  encoder1.pop_front();
  encoder1.push_back(millis());
}


// ACTUATORS
void motorOff(){
  digitalWrite(motorOut, 0);
}

void motorOn(){
  digitalWrite(motorOut,1);
}

void setCoilPosition(int value) {
  analogWrite(coilOut, value);
}

// CALCULATE PHYSICAL CONSTANTS
float calculateFrequency() {
  float totalDelta = 0;
  for (int i = 0; i < encoderSamples-1; i++) {
    totalDelta += encoder1[i+1] - encoder1[i];
  }
  float frequency = 1/(totalDelta/(encoderSamples-1)/1000);
  return frequency;
}

float calculateSpeed(float frequency) {
  //TBD
  return 0;
}

float calculateDisplacement(float v){
  //TBD
  return 0;
}

float calculateAcceleration(float v) {
  //TBD
  return 0;
}

float gaussian(float x, float mean, float variance) {
  return 1/sqrt(2*pi*variance)*pow(e, 1/(2*sq(variance))*sq(x-mean));
}

float modelForce(float v, float d) {
  float k = 1;
  float mean1 = 1;
  float mean2 = 2;
  float variance1 = 1;
  float variance2 = 2;
  return k*v*(gaussian(d, mean1, variance1) + gaussian(d, mean2, variance2));
}

float controller(float modelForce){
  //TBD
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i = 0; i < encoderSamples; i++){
    encoder1.push_back(0);
    encoder2.push_back(0);
  }
  attachInterrupt(digitalPinToInterrupt(encoderIn1), recordEncoder, RISING);
}

void loop() {
  // put your main code here, to run repeatedly:
  readSensors();
  int i = 0;
  while (i < 1000) {
    i++;
  }
  motorOn();
  motorOff();
  noInterrupts();
  float f = calculateFrequency();
  interrupts();
  Serial.println(f);
  delay(20);
}

