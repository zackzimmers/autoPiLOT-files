

const int QRD1114_PIN = A0; // Sensor output voltage
int homeSwitch = 2;  // Push button
bool home_found = 0;

void setup() {
  Serial.begin(9600);  //Starting serial communication
  pinMode(QRD1114_PIN, INPUT);
  Serial.println("Sensor Ready");
  }

void loop() {

  if (home_found == 0){
       if (digitalRead(homeSwitch) == LOW){
         home_found = 1;
         Serial.println("Home Marked, Awaiting Serial Command");
        }
    }

    if (home_found == 1){
      int proximityADC = analogRead(QRD1114_PIN);
      Serial.println(proximityADC);
    }
}
