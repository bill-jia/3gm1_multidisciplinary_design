int state = -1;
int state_duration = 0;
#define DATA_LENGTH 5
float displacement[] = {0, 1, 2, 3, 4, 5};
float force[] = {5, 3, 8, 2, 1};
float time_increment = 1;

String array_to_string(float arr[]) {
  //Serial.println(sizeof(arr));
  String str = "";
  for (int i = 0; i < DATA_LENGTH; i++) {
    str += String(arr[i]) + " ";
  }
  return str;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    state = Serial.parseInt();
    if (state == -1) {
      Serial.println("Leftover data");
    }
  }
  //Serial.println(temp_state);
  //Serial.write(temp_state);
  if (state == 1) {
    digitalWrite(4, 1);
    state_duration++;
    if (state_duration == 10) {
      Serial.print("dt: " + String(time_increment) + " , ");
      Serial.print("d: " + array_to_string(displacement) + " , ");
      Serial.print("f: " + array_to_string(force));
      Serial.print("\n");
      state = -1;
      state_duration = 0;
    }
  }
  else if (state == -1) {
    digitalWrite(4,0);
  }
  //Serial.println("State: " + String(state));
  delay(200);
}
