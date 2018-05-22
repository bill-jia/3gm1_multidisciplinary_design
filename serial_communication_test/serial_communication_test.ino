int state = -1;
int state_duration = 0;
#define DATA_LENGTH 5
float displacement[] = {0, 1, 2, 3, 4, 5};
float timepoints[] = {0, 0.5, 1.0, 1.5, 2};

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
  String o = array_to_string(timepoints);
  //Serial.println(temp_state);
  //Serial.write(temp_state);
  if (state == 1) {
    digitalWrite(4, 1);
    state_duration++;
    if (state_duration == 10) {
      String outputString = array_to_string(timepoints);
      Serial.print("t: " + outputString + ", ");
      outputString = array_to_string(displacement);
      Serial.print("d: " + outputString);
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
