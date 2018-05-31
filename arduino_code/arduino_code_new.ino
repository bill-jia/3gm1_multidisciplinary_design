#include <QList.h>
#define DATA_POINTS 50

//Digital outputs

int A1A = 6;            //for control of motor A
int A1B = 5;    
int B1A = 10;           //for control of motor B
int B1B = 9;
int LED = 7;

//Analogue sensors

//potentiometer = A0;       //for displacement measurement
//tensometerIn = A1;        //for closed loop control  

//Digital sensors
//for the microswitches?


//CONSTANTS

int samples = 2;
float e = 2.71828;
float pi = 3.14159;
float pot_calibrate = 0.7;  //calibration constant to convert voltage across pot into displacement
float tension_calibrate = 0.4;  
int tension_avg, pot_avg, tension_single, displacement_single;  //variables required to perform smoothing
int store = 0;
int count = 0;
String Tstr, Dstr;
int state = -1;  //need to start of as -1 but here as 1 for testing 
int start = 1;
int Kp;

//Parameters

int oes_length, baseline_force;
int k1, mean1, variance1;   //stomach sphincter
int k2, mean2, variance2;   //mouth sphincter or gag reflex
int k3, mean3, variance3;   //extra spasm (if needed)

// VARIABLES
QList<int> potSampled, tensionSampled; //so that we can take a time average of the readings in order to remove noise
int tension[DATA_POINTS], displacement[DATA_POINTS], time_increment[DATA_POINTS], timer[2], pot, k_p, k_i, k_d; 
byte force;    //integer representation of displacement, just divide by 10 to get real displacement from cm to mm 
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
  tension_single = getTensometer();   //the index [samples - 1] gives the most recent addition to the stack
}

void store_data() {
  tension[count - 1] = tension_single;
  displacement[count - 1] = displacement_single;
}

//Timers 

void timerStart() {       //starts the clock
  timer[0] = millis();
}

int timerStop() {        //stops the clock and returns the time elapsed since timerStart()
  timer[1] = millis();
  return timer[1]-timer[0];
}

//serial communication

String displacement_array_to_string() {
  String str = "";
  int j = 0;
  for (int i = 0; i < DATA_POINTS; i++) {
    j = displacement[i];
    str += String(j) + " ";
  }
  return str;
}

String tension_array_to_string() {
  String str = "";
  int j = 0;
  for (int i = 0; i < DATA_POINTS; i++) {
    j = tension[i];
    str += String(j) + " ";
  }
  return str;
}

String time_increment_array_to_string() {
  String str = "";
  int j = 0;
  for (int i = 0; i < DATA_POINTS; i++) {
    j = time_increment[i];
    str += String(j) + " ";
  }
  return str;
}

void send_data() {
  Serial.println("Sending Data");
  Serial.println("dt: " + time_increment_array_to_string() + " , ");
  Serial.println("d: " + displacement_array_to_string() + " , ");
  Serial.println("t: " + tension_array_to_string());
  Serial.print("\n");
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

void calculateDisplacement() {
  pot = pot - 350;
  float pot_ = pot;
  float dis = pot * pot_calibrate;
  int displace = dis;
  displacement_single = displace; //pot will give a reading from approx 350-1023 and displacement should be from 0-400mm ie pot_calibrate = 400/(1023-350)
}

void retract() {
  while (displacement_single > 10) {   //no need for feedback because the electrical system stores the displacement 
    readSensors();
    calculateDisplacement();
    analogWrite(A1A, 0);    //need to make it retract until back to the baseline
    analogWrite(A1B, 100);
    analogWrite(B1A, 100);
    analogWrite(B1B, 0);  
  }
  //Serial.print(displacement_single); // for testing
}


// CALCULATE PHYSICS

float gaussian(float x, float mean, float variance) {
  return pow(e, (-1*sq(x-mean))/(2*variance));
}

int modelForce() {    //returns the force that should be applied at that displacement
  float D = displacement_single;
  float force = k1*gaussian(D, mean1, variance1) + k2*gaussian(D, mean2, variance2) + k3*gaussian(D, mean3, variance3) + baseline_force;
  byte Force = force; 
  return Force;  
}

void controller() {
  float float_tension = tension_single;
  if (float_tension > 635.0) {    //saturation
    float_tension = 635.0;
  } 
  float actualForce = float_tension * tension_calibrate; //changes the tension reading from a 0-634 value to a 0-255 force byte (need to set the calibration parameter)
  byte actual_force = actualForce; //conversion of float to int 0-255
  byte error = modelForce() - actual_force;
  //Serial.println(error);
  force = modelForce() + error * Kp;
  if (force > 255) {  //saturation
    force = 255;
  }
  brake(force);
  if (displacement_single > 400) {  //when the cytosponge comes out of the throat
    store = 2;
    count = DATA_POINTS;
    stopMotor();
  }
}

void resetVariables() {
  force = 0; 
  pot = 0;
  count = 0;
  timer[0] = 0;
  timer[1] = 0;
  start = 1;

  for (int i = 0; i < DATA_POINTS; i++){   //for force control
    displacement[i] = 0;
    tension[i] = 0;     
    time_increment[i] = 0; 
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A1A, OUTPUT);
  pinMode(A1B, OUTPUT);
  pinMode(B1A, OUTPUT);
  pinMode(B1B, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  
  pot = 0;
  count = 0;
  force = 0;
  store = 0;
  start = 1;
  
  for (int i = 0; i < samples; i++){   //creating the stacks of size samples
    potSampled.push_back(0);
    tensionSampled.push_back(0);
  }
  for (int i = 0; i < 2; i++){
    timer[i] = 0; 
  }
  for (int i = 0; i < DATA_POINTS; i++){   //for force control
    displacement[i] = 0;
    tension[i] = 0;     
    time_increment[i] = 0;
  }
  Serial.println("Program start"); //need to comment this out when using serial with pi
  
  brake(255);
  delay(5000);
  stopMotor();
  Serial.println("Motor Stop");
} 

void loop() {
  // put your main code here, to run repeatedly:
  //Stuff in main loop not permanent for now
//
//  if (Serial.available() > 0) {   //start up by sending case {2, 3, 4} and then start (1)
//    int newState = Serial.parseInt();
//    if (newState == -1) {
//      stopMotor();
//      send_data();
//      start = 1;
//    }
//    else if (newState == 1){
//      //oesphageal length? oes_length = Serial.parseInt();
//      if (state == 2 || state == 3 || state == 4) { 
//        state = newState;
//        Serial.print("Program Starting"); //sending back an ack
//        digitalWrite(LED, HIGH);
//        delay (500);
//        digitalWrite(LED, LOW);
//        delay (500);                      
//        digitalWrite(LED, HIGH);
//        delay (500);
//        digitalWrite(LED, LOW);
//        delay (500);
//        digitalWrite(LED, HIGH);
//        delay (500);
//        digitalWrite(LED, LOW);
//      }       
//    }
//  else if (newState == 2) {
//      //case for patient 1: healthy
//      state = newState;
//      oes_length = 400;
//      baseline_force = 30;
//      k1 = 500;
//      mean1 = 50; 
//      variance1 = 100;
//      k2 = 1000;
//      mean2 = 350;
//      variance2 = 100;
//      k3 = 0;
//      mean3 = 0;
//      variance3 = 0;       
//    }
//    else if (newState == 3) {
//      //case for patient 2: spasms?
//      state = newState;
//      oes_length = 400;
//      baseline_force = 80;
//      k1 = 500;
//      mean1 = 50;
//      variance1 = 100; 
//      k2 = 250;
//      mean2 = 200;
//      variance2 = 200;
//      k3 = 1000;
//      mean3 = 350;
//      variance3 = 100;      
//    }
//    else if (newState == 4) {
//      //case for patient 3: short patient?
//      state = newState;
//      oes_length = 300;
//      baseline_force = 30;
//      k1 = 500;
//      mean1 = 50;
//      variance1 = 100; 
//      k2 = 1000;
//      mean2 = 250;
//      variance2 = 100;
//      k3 = 0; 
//      mean3 = 0;
//      variance3 = 0;  
//    }
//    else if (newState == -2) {
//      state = newState;
//      retract();
//    }
//    else {
//        Serial.print("Error");
//      }
//  }
//
////  if (state == 2) {
////    //case for patient 1: healthy
////    oes_length = 400;
////    baseline_force = 50;
////    k1 = 500;
////    mean1 = 50; 
////    variance1 = 100;
////    k2 = 1000;
////    mean2 = 350;
////    variance2 = 100;
////    k3 = 0;
////    mean3 = 0;
////    variance3 = 0;     
////    state = 1;  
////  }
//
//  else if (state == 1) {
//  if (start==1) {
//    timerStart();
//  }
//  store++;
//  readSensors();
//  calculateDisplacement();
//  controller();         
//  delay(50);
//  if (store > 2) {    //this stores every other displacement reading to allow for better control (smaller delay) without cutting the total run time
//    time_increment[count] = timerStop();
//    count++;
//    store_data();
//    store = 0;
//    timerStart();
//  }
//  if (count > DATA_POINTS - 1) {
//    state = -1;
//    send_data();
//    resetVariables();
//    }
//  }
}




