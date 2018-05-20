#include <QList.h>

int encoderIn1 = 3;
int encoderIn2 = 2;
int motorOut = 4;

int tensometerIn = 0;
int coilOut = 5;

//CONSTANTS
int encoderSamples = 5;
float kinematicsSampleTimeLength = 0.1; //seconds
float kinematicsSampleInterval = 20; //millisecond
int kinematicsSampleNumber;
float e = 2.71828;
float pi = 3.14159;
float encoderRadius;
float encoderSpacing;

// VARIABLES
float k_p, k_i, k_d;
volatile QList<int> encoder1, encoder2;
volatile QList<float> displacement, velocity, acceleration;
int tensiontest[250];
int tension;
int maxDisplacement, timeoutSec;
int encoderTicks = 0;

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
  encoderTicks++;
  //Serial.println(encoderTicks);
  int timeInterval = encoder1[encoderSamples-1] - encoder1[encoderSamples-2];
  //Serial.println(timeInterval);
  updateKinematics(timeInterval);
  //Serial.println(calculateDisplacement());
  //TBD: Forward and backwards counting
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

void updateKinematics(float timeIntervalMillis){
  displacement.push_back(calculateDisplacement());
  displacement.pop_front();
  //Serial.print(displacement[0]);
  for (int i = 0; i < kinematicsSampleNumber; i++) {
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
  acceleration.push_back(calculateAcceleration(timeIntervalMillis));
  acceleration.pop_front();
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
  kinematicsSampleNumber = (int) (kinematicsSampleTimeLength*1000/kinematicsSampleInterval);
  for (int i = 0; i < encoderSamples; i++){
    encoder1.push_back(0);
    encoder2.push_back(0);
  }
  for (int i = 0; i < kinematicsSampleNumber; i++){
    displacement.push_back(0);
    velocity.push_back(0);
    acceleration.push_back(0);
  }
  attachInterrupt(digitalPinToInterrupt(encoderIn1), recordEncoder, RISING);
  Serial.println("Program start");
}

void loop() {
  // put your main code here, to run repeatedly:
  //Stuff in main loop not permanent for now
  readSensors();
  Serial.print("Tension: ");
  Serial.print(tension);
  Serial.print("\n");
  motorOn();
  motorOff();
  //Serial.println(displacement[kinematicsSampleNumber-1]);
  delay(100);
}

