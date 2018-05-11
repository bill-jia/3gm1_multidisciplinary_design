#include <QList.h>

int encoderIn1 = 2;
int encoderIn2 = 3;
int motorOut = 4;

int tensometerIn = 0;
int coilOut = 5;
int j = 0;

int encoderSamples = 20;
float k_p, k_i, k_d;
volatile QList<int> encoder1, encoder2;
int tensiontest[250];
int tension, displacement, velocity, acceleration;
int maxDisplacement, timeoutSec;


int getEncoder1() {
  return digitalRead(encoderIn1);
}

int getEncoder2(){
  return digitalRead(encoderIn2);
}

int getTensometer(){
  return analogRead(tensometerIn);
}

void motorOff(){
  digitalWrite(motorOut, 0);
}

void motorOn(){
  digitalWrite(motorOut,1);
}

void setCoilPosition(int value) {
  analogWrite(coilOut, value);
}

void readSensors() {
  tension = getTensometer();
}

void recordEncoder() {
  encoder1.pop_front();
  encoder1.push_back(millis());
}


float calculateFrequency() {
  float totalDelta = 0;
  for (int i = 0; i < encoderSamples-1; i++) {
    totalDelta += encoder1[i+1] - encoder1[i];
  }
  float frequency = 1/(totalDelta/(encoderSamples-1)/1000);
  return frequency;
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

