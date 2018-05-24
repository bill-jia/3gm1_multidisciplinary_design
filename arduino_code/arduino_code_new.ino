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
int data_points = 200;
int present = data_points - 1;
int previous = data_points - 2;
int timeIntervalMillis;

//Parameters

double k1 = 100;           //for the stomach sphincter
float mean1 = 400;      //set the gaussian centres without calibration for now #########
float variance1 = 100;
double k2 = 200;           //for the mouth sphincter
float mean2 = 900;
float variance2 = 100;


// VARIABLES
float k_p, k_i, k_d;
QList<int> potSampled, tensionSampled, tension, timer; //so that we can take a time average of the readings in order to remove noise
QList<float> displacement, force;
int maxDisplacement, timeoutSec, pot;


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

float controller(float modelForce){   //open loop for now
  byte force = modelForce; 
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
  for (int i = 0; i < samples; i++){   //creating the stacks of size samples
    //pot.push_back(0);             //note that the pot and tension do not need to be the same length as the smoothing samples 
    //tension.push_back(0);         //because we are just using their contents to calculate vel and acc.
    potSampled.push_back(0);
    tensionSampled.push_back(0);
  }
  for (int i = 0; i < 2; i++){
    tension.push_back(0); 
    timer.push_back(0); 
  }
  for (int i = 0; i < data_points; i++){   //same for kinematics 
    displacement.push_back(0);
    force.push_back(0);
  }
  //attachInterrupt(digitalPinToInterrupt(encoderIn1), recordEncoder, RISING);//we dont need this for a pot right?
  Serial.println("Program start");
}

void loop() {
  // put your main code here, to run repeatedly:
  //Stuff in main loop not permanent for now
  timerStart();
  readSensors();
  delay(50);
  timeIntervalMillis = timerStop();
  calculateDisplacement();
  //now for the current disp, vel and acc we can determine the force output but for now we will base it just on disp
  Serial.print("Displacement: ");
  Serial.print(displacement[present]);
  Serial.print(" ");
  Serial.print("Force: ");
  Serial.print(" ");
  Serial.println(modelForce(displacement[present]));
  //controller(modelForce(displacement[present]));

}




