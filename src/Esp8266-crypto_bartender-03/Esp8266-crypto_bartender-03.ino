//Release  v0.0.2 2020-05-31
// The Pump attached to GPIO0 (D3)
// The Flow sensor attached to GPIO2 (D4)
// Humidity sensor attached to GPI14 (D5)

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET    LED_BUILTIN // 12
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define RELAY_PIN 0
#define HALL_SENSOR 2
#define HUM_PIN 14

const char *topic_pub1 = "cryptobartender/state/device0001";
const char *topic_sub1 = "cryptobartender/ctl/device0001";

const char *ssid =  "login";  // WiFi SSID
const char *pass =  "password"; // WiFi password

const char *mqtt_server = "mqtt.korotach.com"; //  MQTT broker
const int mqtt_port = 1883; //  MQTT port
const char *mqtt_user = "login"; // MQTT user
const char *mqtt_pass = "password"; // MQTT password

bool RelayState = false;
int tm=300;
int FillDelay=4188;
int Filled = 50000;
volatile int NbTopsFan = 0; //measuring the rising edges of the signal
int Calc = 0;
// bool Ready = true;
String Status = "Ready";
bool Pump_On = false;
int val = 0;
boolean invert = true;
int scroll_type = 0;
String account = "";
String recv_sequence = "";
int ping_time = 0;
String code = "";

// Get data from the server

void callback(const MQTT::Publish& pub)
{
  Serial.print(pub.topic());   // print topic
  Serial.print(" => ");
  Serial.println(pub.payload_string()); // print to the Serial the received data

  char payload[200];
  pub.payload_string().toCharArray(payload, 200);
  
  if(String(pub.topic()) == topic_sub1) // is it the right topic? 
  {
  if (Status == "Ready" or Status == "NO CONNECT") {
    DynamicJsonBuffer jsonBuffer(200);
    JsonObject& root = jsonBuffer.parseObject(payload);
    if (!root.success()) {
      Serial.println("JSON parsing failed!");
      return;
    } else {
        String code1 = root["code"];
        code = code1;
        if (code != "ping") {
            if (code == "give_the_goods") {
              String account1 = root["customer"];
              account = account1;
              Serial.println(account);
              scrolltext(account, 2);
              Pump_On = true;
            }
        } else {  // ping from python script
          ping_time = millis();
        }
      }
    }
  }
}


WiFiClient wclient;      
PubSubClient client(wclient, mqtt_server, mqtt_port);

void ICACHE_RAM_ATTR rpm()     //This is the function that the interupt calls 
{ 
  NbTopsFan++;  //This function measures the rising and falling edge of the hall effect sensors signal
} 

void setup() {
  pinMode(HALL_SENSOR, INPUT_PULLUP);
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt (HALL_SENSOR), rpm, RISING);
  delay(10);
  Serial.println();
  Serial.println();
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
  pinMode(HUM_PIN, INPUT);
    if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C, true)) {
    Serial.println(F("SSD1306 allocation failed"));
  }
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();
}

void loop() {
  // connecting to WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting to ");
    Serial.print(ssid);
    Serial.println("...");
    WiFi.begin(ssid, pass);

    if (WiFi.waitForConnectResult() != WL_CONNECTED)
      return;
    Serial.println("WiFi connected");
  }

  // connecting to MQTT broker
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      Serial.println("Connecting to MQTT server");
      if (client.connect(MQTT::Connect("device0001")
                         .set_auth(mqtt_user, mqtt_pass))) {
        Serial.println("Connected to MQTT server");
        client.set_callback(callback);
        client.subscribe(topic_sub1); // subscribe to the topic which controls the device
      } else {
        Serial.println("Could not connect to MQTT server");   
      }
    }

    if (client.connected()){
      client.loop();
      if (Status == "Ready" and Pump_On) {
        FillGlass(FillDelay);
      }
      ReadySend();
    }  
  }
} // the end of main loop


// Send signal "Ready" to the manager
void ReadySend(){
  if (tm<=0)
  {
    val = digitalRead(HUM_PIN);
    if (val) {
      Status = "Empty";
    } else {
        int ping_time1 = millis();
        if (ping_time1 - ping_time < 10000) {
          Status = "Ready";
        } else {
            Status = "NO CONNECT";
        }
    }
    client.publish(topic_pub1, "{\"status\": \"" + Status + "\"}");
    Serial.println(Status);
    scrolltext(Status, 2);
    tm = 300;  // the delay between the "Ready" signals is approximately 3 sec (300 milliseconds * 10)
  }
  tm--; 
  delay(10);  
}

// pour 50 grams
void FillGlass(int FDelay){
  Status = "Busy";
  client.publish(topic_pub1, "{\"status\": \"" + Status + "\"}");
  digitalWrite(RELAY_PIN, true);
  NbTopsFan = 0;
  Calc = 0;
  delay(FDelay);
  digitalWrite(RELAY_PIN, false);
  ping_time = millis();
  Calc = NbTopsFan;
  if (Calc < 230) {
    Status = "Error";
    client.publish(topic_pub1, "{\"status\": \"" + Status + "\", \"filled\": \"" + String(Calc) + "\"}");
    for (int i=0; i <= 12; i++) {
      scroll_type = 1;
      invert = !invert;
      display.invertDisplay(invert);
      scrolltext(Status, 3);  
      delay(250);
    }
    ping_time = millis();
  } else {
    Status = "Ok";
    client.publish(topic_pub1, "{\"status\": \"" + Status + "\", \"filled\": \"" + String(Calc) + "\", \"account\": \"" + account + "\"}");        
    scrolltext(Status, 3);
    delay(3000);
    scrolltext("THANK YOU!", 2);
    delay(3000);
    ping_time = millis();
  }
  delay(50);
  Pump_On = false;
  scrolltext(Status, 2);
}

void scrolltext(String text, int size) {
  display.clearDisplay();

  display.setTextSize(size); // Draw 2X-scale text
  display.setTextColor(WHITE);
  display.setCursor(5, 3);
  display.println(text);
  display.display();      // Show initial text
  delay(100);
  switch(scroll_type) {
  // Scroll in various directions, pausing in-between:
  case 1:
    display.startscrollright(0x00, 0x0F);
    break;
  case 2:
    display.startscrollleft(0x00, 0x0F);
    break;
  case 3:
    display.startscrolldiagright(0x00, 0x07);
    break;
  case 4:
    display.startscrolldiagleft(0x00, 0x07);
    break;
  default:
    scroll_type = 0;
    invert = !invert;
    display.invertDisplay(invert);
  }
  scroll_type += 1; 
}
