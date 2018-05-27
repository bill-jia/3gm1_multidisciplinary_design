#include <QList.h>


//Digital outputs

int A1A = 6;            //for control of motor A
int A1B = 5;    
int B1A = 10;           //for control of motor B
int B1B = 9;


//Analogue sensors

//potentiometer = A0;       //for displacement measurement
//tensometerIn = A1;        //for closed loop control  

//Digital sensors
//for the microswitches?


//CONSTANTS

int samples = 5;
float kinematicsSampleTimeLength = 0.1; //seconds
float kinematicsSampleInterval = 20; //millisecond
int kinematicsSampleNumber;
float e = 2.71828;
float pi = 3.14159;
float pot_calibrate = 1.0;  //calibration constant to convert voltage across pot into angular displacement
int tension_read, tension_avg, pot_read, pot_avg;  //variables required to perform smoothing
byte data_points = 50;
byte present = data_points - 1;
byte previous = data_points - 2;
int timeIntervalMillis;
byte count;
String str = "";
String Tstr, Dstr, str1, str2;
//to delete
int time_increment = 0.25;
int state = -1;

//Parameters

double k1 = 100;           //for the stomach sphincter
float mean1 = 400;      //set the gaussian centres without calibration for now #########
float variance1 = 100;
double k2 = 200;           //for the mouth sphincter
float mean2 = 900;
float variance2 = 100;


// VARIABLES
float k_p, k_i, k_d, pot;
QList<int> potSampled, tensionSampled, tension, timer; //so that we can take a time average of the readings in order to remove noise
QList<float> displacement;
byte force;
int maxDisplacement, timeoutSec;


// SENSORS
int getPotentiometer() {    //averages the readings to get a smoother response
  potSampled.pop_front();
  potSampled.push_back(analogRead(A0));
  pot_avg = 0;
  for (int i=0; i<samples; i++){
     pot_avg = pot_avg + potSampled[i];
  }
  return pot_avg/samples;
}

int getTensometer() {
  tensionSampled.pop_front();
  tensionSampled.push_back(analogRead(A1));
  tension_avg = 0;
  for (int i=0; i<samples; i++){
     tension_avg = tension_avg + tensionSampled[i];
  }
  return tension_avg/samples;
}

void readSensors() {
  pot = getPotentiometer();     
  tension.pop_front();                //the index [samples - 1] gives the most recent addition to the stack
  tension.push_back(getTensometer());
}


//Timers 

void timerStart() {       //starts the clock
  timer.pop_front();
  timer.push_back(millis());
}

int timerStop() {        //stops the clock and returns the time elapsed since timerStart()
  timer.pop_front();
  timer.push_back(millis());
  return timer[1]-timer[0];
}

//serial communication

String displacement_array_to_string() {
  String str = "";
  for (int i = 0; i < data_points; i++) {
    float j = displacement[i];
    str += String(j) + " ";
  }
  return str;
}

String tension_array_to_string() {
  String str = "";
  Serial.print("called");
  for (int i = 0; i < data_points; i++) {
    int j = tension[i];
    str += String(j) + " ";
  }
  Serial.print("cal");
  return str;
}

void send_Data(QList<int> T, QList<float> D) {
  Serial.println("Sending Data");
  //Tstr = int_array_to_string(T);
  //Dstr = float_array_to_string(D);
}

// ACTUATORS
void stopMotor() {
  analogWrite(A1A, 0);
  analogWrite(A1B, 0);
  analogWrite(B1A, 0);
  analogWrite(B1B, 0);
}

void brake(byte force) {    //force must be from 0-255
  analogWrite(A1A, force);
  analogWrite(A1B, 0);
  analogWrite(B1A, force);
  analogWrite(B1B, 0);
}

void retract() {
  analogWrite(A1A, 100);    //need to make it retract until back to the baseline
  analogWrite(A1B, 0);
  analogWrite(B1A, 100);
  analogWrite(B1B, 0);
}


// CALCULATE PHYSICS

void calculateDisplacement() {
  displacement.push_back(pot*pot_calibrate);
  displacement.pop_front();
}

float gaussian(float x, float mean, float variance) {
  return pow(e, (-1*sq(x-mean))/(2*variance));
}

float modelForce(float d) {
  return k1*gaussian(d, mean1, variance1) + k2*gaussian(d, mean2, variance2) + 50;
}

void controller(float d){   //open loop for now
  force = modelForce(d);
  brake(force);
}

void resetVariables() {
  //TBD
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A1A, OUTPUT);
  pinMode(A1B, OUTPUT);
  pinMode(B1A, OUTPUT);
  pinMode(B1B, OUTPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pot = 0;
  count = 0;
  force = 0;
  for (int i = 0; i < samples; i++){   //creating the stacks of size samples
    potSampled.push_back(0);
    tensionSampled.push_back(0);
  }
  for (int i = 0; i < 2; i++){
    timer.push_back(0); 
  }
  for (int i = 0; i < data_points; i++){   //for force control
    displacement.push_back(0);
    tension.push_back(0);     
  }
  //attachInterrupt(digitalPinToInterrupt(encoderIn1), recordEncoder, RISING);//we dont need this for a pot right?
  //Serial.println("Program start");
}

void loop() {
  // put your main code here, to run repeatedly:
  //Stuff in main loop not permanent for now
  
  if (Serial.available() > 0) {
    state = Serial.parseInt();
    if (state == -1) {
      Serial.println("Leftover data");
      for (int i = 0; i < data_points; i++) {
        tension.pop_front();
        tension.push_back(i);
      } 
      str1 = tension_array_to_string();
      for (int i = 0; i < data_points; i++) {
        displacement.pop_front();
        displacement.push_back(i*1.0);
      }
  str2 = displacement_array_to_string();
  //Serial.print(tension.size());
      Serial.print("dt: " + String(time_increment) + " , ");
      Serial.print("d: " + displacement_array_to_string(displacement) + " , ");
      Serial.print("t: " + tension_array_to_string());
      Serial.print("\n");  
    }
  }
  if (state == 1) {
    brake(400.0);
  }
  

  
  

  
  //delay (2000);

  /*
  timerStart();
  readSensors();
  delay(50);
  timeIntervalMillis = timerStop();
  calculateDisplacement();
  count++;
  Serial.println(count);
  if (count > data_points) {
    count = 0;
    send_Data(tension, displacement);
    //Serial.print(float_array_to_string(displacement));
    
  }
  
  //Serial.println(displacement[present]);
  //controller(displacement[present]);
  */
}




