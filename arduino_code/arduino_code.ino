#include <QList.h>

int encoderIn1 = 0;
int encoderIn2 = 1;
int motorOut = 2;

int tensometerIn = 0;
int coilOut = 5;

float k_p, k_i, k_d;
QList<int> encoder1, encoder2;
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
  encoder1.pop_front();
  encoder2.pop_front();
  encoder1.push_back(getEncoder1());
  encoder2.push_back(getEncoder2());
  tension = getTensometer();
}

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}

