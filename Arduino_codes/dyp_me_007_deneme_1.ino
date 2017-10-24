#include <NewPing.h>
 
#define TRIGGER_PIN  12
#define ECHO_PIN     11
#define MAX_DISTANCE 200
#define LEDPIN 13
int average_distance = 0;
boolean calibration_flag = false;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200);
  pinMode(LEDPIN, OUTPUT);
}
 
void loop() {
  if(calibration_flag == false)
  {
    // Calibration Process
    digitalWrite(LEDPIN, HIGH);
    int i = 0;
//    int average_distance = 0;
    int total_distance = 0;
    delay(100);
    for(i=0; i<40; i++)
    {
      total_distance += sonar.ping_cm();
      delay(50);
      Serial.println(9999);
    }
    average_distance = total_distance/40;
    digitalWrite(LEDPIN, LOW);
    calibration_flag = true;
  }
  else
  {
    int last_measurement = 0;
    int current_measurement = 0;
    int counter = 0;
    int loop_average = 0;
    int loop_total = 0;
    for(int i = 0; i<10; i++)
    {
      current_measurement = sonar.ping_cm();
      if((current_measurement - last_measurement) < 2)
      {
        loop_total += sonar.ping_cm();
        delay(100);
        counter += 1;
      }
      last_measurement = current_measurement;
    }
    if(counter > 4)
    {
      loop_average = loop_total/counter;
      if((average_distance - loop_average) > 5)
      {
        Serial.println(average_distance - loop_average);
      }
      else
      {
        Serial.println(0);
      }
    }
  }
}

