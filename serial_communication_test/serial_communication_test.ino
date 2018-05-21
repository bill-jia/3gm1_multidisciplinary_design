int i = 0;
int state = -1;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int temp_state = Serial.parseInt();
  if (temp_state == 1) {
    state = 1;
    //Serial.write("Hello Arduino");
  }
  else if (temp_state == -1) {
    state = -1;
  }
  if (state == 1) {
    digitalWrite(4, 1);
    Serial.write("Hello Raspberry Pi " + i);  
  }
  else if (state == -1) {
    digitalWrite(4,0);
  }
  
  i++;
  delay(500);
}
