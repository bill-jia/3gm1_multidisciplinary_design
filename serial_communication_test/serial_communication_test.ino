void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  int state = Serial.parseInt();
  if (state == 1) {
    digitalWrite(4, 1);
  }
  else if (state == -1) {
    digitalWrite(4,0);
  }
}
