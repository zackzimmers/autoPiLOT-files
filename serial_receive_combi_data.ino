
// Example 5 - Receive with start- and end-markers combined with parsing

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
int positionFromPC = 0;
int speedFromPC = 0;

boolean newData = false;

#include <AccelStepper.h>
int pinStep = 7;
int pinDirection = 6;
int homeSwitch = 2;  // Push button
bool home_found = 0;
AccelStepper stepper(1, pinStep, pinDirection);


//============

void setup() {
    Serial.begin(9600);
//    Serial.println("Expects 3 data - text, position (integer), speed (integer)");
//    Serial.println("Enter data in this style <HelloWorld, 12, 24>  ");
//    Serial.println();
    pinMode(homeSwitch, INPUT);
    stepper.setMaxSpeed(1000);
    Serial.println("Feeding Tube, Push button when home reached");
    stepper.setSpeed(-200);
}

//============

void loop() {
  if (home_found == 0){
      while (digitalRead(homeSwitch) == HIGH){
        stepper.runSpeed();
       }

       if (digitalRead(homeSwitch) == LOW){
         stepper.setSpeed(0);
         stepper.setCurrentPosition(0);
         home_found = 1;
         Serial.println("Home Marked, Awaiting Serial Command");
        }
    }

    if (home_found == 1){
      stepper.setMaxSpeed(5000);
      stepper.setSpeed(speedFromPC);
      stepper.runSpeedToPosition();
//      Serial.println(stepper.currentPosition());
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        showParsedData();
        newData = false;
    }
    
   }

    
    
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
 
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    positionFromPC = atoi(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    speedFromPC = atoi(strtokIndx);     // convert this part to a float

}

//============

void showParsedData() {
//    Serial.print("Message ");
//    Serial.println(messageFromPC);
//    Serial.print("Position: ");
//    Serial.println(positionFromPC);
//    Serial.print("Speed: ");
//    Serial.println(speedFromPC);
    stepper.moveTo(positionFromPC);
}
