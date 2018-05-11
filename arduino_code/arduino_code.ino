#include <QList.h>

int encoderIn1 = 2;
int encoderIn2 = 3;
int motorOut = 4;

int tensometerIn = 0;
int coilOut = 5;
int j = 0;

float k_p, k_i, k_d;
QList<int> encoder1, encoder2;
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

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i = 0; i < 100; i++){
    encoder1.push_back(0);
    encoder2.push_back(0);
  }
  //attachInterrupt(digitalPinToInterrupt(encoder1, recordEncoder, RISING));
  //Serial.println("Hello World");
  //Serial.println(j);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (j < 250) {
    readSensors();
    tensiontest[j]= tension;
    int i = 0;
    while (i < 1000) {
      i++;
    }
    motorOn();
    motorOff();
    j++;
  }
  else if (j < 500) {
    //Serial.println(j-250);
    Serial.println(tensiontest[j-250]);
    delay(250);
    j++;
  }
  else {
    exit(0);
  }
}

