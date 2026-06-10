#include <Arduino.h>
/* =====================================================================
   AEGIS - Autonomous Edge Guardian for Interplanetary Stations
   Estacao de monitoramento de habitat (base lunar/marciana) - ESP32

   Fluxo:  sensores -> inferencia TFLite (local) -> MQTT -> atuadores
   Plataforma: broker MQTT publico + Node-RED + Telegram

   Entradas do modelo (nesta ordem):
       [0] temperatura (C)   - DHT22
       [1] umidade (%)       - DHT22
       [2] pressao (kPa)     - potenciometro 1
       [3] co2 (ppm)         - potenciometro 2
       [4] radiacao (uSv/h)  - LDR
   Saidas: 0=NOMINAL 1=SOBRECARGA_TERMICA 2=RISCO_DESPRESSURIZACAO 3=AR_CRITICO
   ===================================================================== */

#include <WiFi.h>
#include <PubSubClient.h>
#include "DHTesp.h"
#include <ESP32Servo.h>

// ---- TensorFlow Lite Micro ----
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model.h"   // <-- coloque AQUI o model.h gerado no Colab

// =====================  PINOS  =====================
#define PIN_DHT      23
#define PIN_PRESSAO  34   // ADC1 (entrada analogica)
#define PIN_CO2      35   // ADC1
#define PIN_RAD      32   // ADC1 (LDR)
#define PIN_SERVO    18
#define PIN_LED_R    27
#define PIN_LED_G    25
#define PIN_LED_B    26
#define PIN_BUZZER   13

// =====================  WIFI / MQTT  =====================
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT = 1883;

// IMPORTANTE: troque "RM00000" pelo seu RM para nao colidir no broker publico
#define BASE_TOPIC      "fiap/aegis/RM00000"
#define TOPIC_TELEMETRIA BASE_TOPIC "/telemetria"
#define TOPIC_STATUS     BASE_TOPIC "/status"
#define TOPIC_COMANDO    BASE_TOPIC "/comando"

WiFiClient   espClient;
PubSubClient mqtt(espClient);

// =====================  SENSORES / ATUADORES  =====================
DHTesp dht;
Servo  servo;

// =====================  TFLITE GLOBALS  =====================
namespace {
  tflite::ErrorReporter* error_reporter = nullptr;
  const tflite::Model*   model = nullptr;
  tflite::MicroInterpreter* interpreter = nullptr;
  TfLiteTensor* input = nullptr;
  TfLiteTensor* output = nullptr;
  constexpr int kTensorArenaSize = 16 * 1024;   // folga sobre os ~8KB sugeridos
  uint8_t tensor_arena[kTensorArenaSize];
}

const char* CLASSES[] = {
  "NOMINAL", "SOBRECARGA_TERMICA", "RISCO_DESPRESSURIZACAO", "AR_CRITICO"
};

// =====================  ESTADO GLOBAL  =====================
bool  modoManual = false;   // comando remoto sobrepoe a atuacao automatica
int   servoManual = 0;
bool  mudo = false;         // silencia o buzzer
unsigned long ultimaLeitura = 0;
const unsigned long INTERVALO = 2000;  // ms entre leituras

// ---------------------------------------------------------------------
void setRGB(bool r, bool g, bool b) {
  digitalWrite(PIN_LED_R, r);
  digitalWrite(PIN_LED_G, g);
  digitalWrite(PIN_LED_B, b);
}

// ---------------------------------------------------------------------
void conectarWiFi() {
  Serial.print("Conectando ao WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.printf("\nWiFi OK | IP: %s\n", WiFi.localIP().toString().c_str());
}

// ---------------------------------------------------------------------
void callbackMQTT(char* topic, byte* payload, unsigned int len) {
  String cmd;
  for (unsigned int i = 0; i < len; i++) cmd += (char)payload[i];
  cmd.trim();
  Serial.printf("Comando recebido: %s\n", cmd.c_str());

  // pisca azul para sinalizar recebimento
  setRGB(0, 0, 1); delay(120);

  if (cmd == "VENTILAR_ON")  { modoManual = true;  servoManual = 90; }
  else if (cmd == "VENTILAR_OFF") { modoManual = true; servoManual = 0; }
  else if (cmd == "AUTO")    { modoManual = false; }
  else if (cmd == "MUTE")    { mudo = true; noTone(PIN_BUZZER); }
  else if (cmd == "UNMUTE")  { mudo = false; }
}

// ---------------------------------------------------------------------
void conectarMQTT() {
  while (!mqtt.connected()) {
    String id = "aegis-esp32-" + String((uint32_t)esp_random(), HEX);
    Serial.print("Conectando ao MQTT...");
    if (mqtt.connect(id.c_str())) {
      Serial.println(" OK");
      mqtt.subscribe(TOPIC_COMANDO);
      Serial.printf("Inscrito em %s\n", TOPIC_COMANDO);
    } else {
      Serial.printf(" falhou (rc=%d), tentando de novo\n", mqtt.state());
      delay(2000);
    }
  }
}

// ---------------------------------------------------------------------
void setupTFLite() {
  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;

  model = tflite::GetModel(aegis_model_tflite);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("ERRO: versao do schema do modelo incompativel!");
    while (true) delay(1000);
  }

  static tflite::AllOpsResolver resolver;
  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
  interpreter = &static_interpreter;

  if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("ERRO: AllocateTensors() falhou (aumente kTensorArenaSize)");
    while (true) delay(1000);
  }
  input  = interpreter->input(0);
  output = interpreter->output(0);
  Serial.println("TFLite pronto.");
}

// ---------------------------------------------------------------------
// Classifica e retorna o indice da classe; preenche 'confianca'
int classificar(float temp, float umid, float pres, float co2, float rad,
                float& confianca) {
  input->data.f[0] = temp;
  input->data.f[1] = umid;
  input->data.f[2] = pres;
  input->data.f[3] = co2;
  input->data.f[4] = rad;

  if (interpreter->Invoke() != kTfLiteOk) {
    Serial.println("ERRO: Invoke() falhou");
    confianca = 0;
    return 0;
  }

  int   melhor = 0;
  float maxP = output->data.f[0];
  for (int i = 1; i < 4; i++) {
    if (output->data.f[i] > maxP) { maxP = output->data.f[i]; melhor = i; }
  }
  confianca = maxP;
  return melhor;
}

// ---------------------------------------------------------------------
// Aciona atuadores conforme o estado classificado
void atuar(int estado, float confianca) {
  int anguloServo;

  // semaforo de status (verde = ok, amarelo = risco c/ baixa confianca,
  // vermelho = risco confirmado)
  if (estado == 0) {
    setRGB(0, 1, 0);                         // verde
  } else if (confianca < 0.60) {
    setRGB(1, 1, 0);                         // amarelo (incerto)
  } else {
    setRGB(1, 0, 0);                         // vermelho
  }

  // logica de ventilacao por estado
  switch (estado) {
    case 1: anguloServo = 90; break;  // SOBRECARGA_TERMICA -> ventila p/ dissipar
    case 3: anguloServo = 90; break;  // AR_CRITICO -> ventila p/ renovar o ar
    case 2: anguloServo = 0;  break;  // RISCO_DESPRESSURIZACAO -> sela o habitat
    default: anguloServo = 0; break;  // NOMINAL -> fechado
  }
  if (modoManual) anguloServo = servoManual;  // override remoto
  servo.write(anguloServo);

  // alarme sonoro
  bool alarme = (estado != 0) && (confianca >= 0.60);
  if (alarme && !mudo) tone(PIN_BUZZER, 2000);
  else                 noTone(PIN_BUZZER);
}

// ---------------------------------------------------------------------
void publicar(float temp, float umid, float pres, float co2, float rad,
              int estado, float confianca, int anguloServo) {
  char buf[256];

  snprintf(buf, sizeof(buf),
    "{\"temp\":%.2f,\"umid\":%.1f,\"pressao\":%.2f,\"co2\":%.0f,\"radiacao\":%.3f}",
    temp, umid, pres, co2, rad);
  mqtt.publish(TOPIC_TELEMETRIA, buf);

  snprintf(buf, sizeof(buf),
    "{\"estado\":\"%s\",\"classe\":%d,\"confianca\":%.3f,\"modo\":\"%s\",\"servo\":%d}",
    CLASSES[estado], estado, confianca, modoManual ? "manual" : "auto",
    anguloServo);
  mqtt.publish(TOPIC_STATUS, buf);
}

// ---------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PIN_LED_R, OUTPUT);
  pinMode(PIN_LED_G, OUTPUT);
  pinMode(PIN_LED_B, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  setRGB(0, 0, 0);

  dht.setup(PIN_DHT, DHTesp::DHT22);
  servo.attach(PIN_SERVO);
  servo.write(0);

  analogReadResolution(12);   // 0..4095

  conectarWiFi();
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(callbackMQTT);

  setupTFLite();
  Serial.println("=== AEGIS online ===");
}

// ---------------------------------------------------------------------
void loop() {
  if (!mqtt.connected()) conectarMQTT();
  mqtt.loop();

  if (millis() - ultimaLeitura < INTERVALO) return;
  ultimaLeitura = millis();

  // --- leitura dos sensores ---
  TempAndHumidity d = dht.getTempAndHumidity();
  float temp = d.temperature;
  float umid = d.humidity;
  if (isnan(temp)) temp = 22.0;   // fallback se o DHT falhar
  if (isnan(umid)) umid = 45.0;

  // mapeia os analogicos (0..4095) para as faixas fisicas
  float pres = 75.0  + (analogRead(PIN_PRESSAO) / 4095.0) * (108.0 - 75.0);
  float co2  = 350.0 + (analogRead(PIN_CO2)     / 4095.0) * (5000.0 - 350.0);
  float rad  = 0.05  + (analogRead(PIN_RAD)     / 4095.0) * (2.0 - 0.05);

  // --- inferencia local (TinyML) ---
  float confianca;
  int estado = classificar(temp, umid, pres, co2, rad, confianca);

  // --- atuacao + publicacao ---
  atuar(estado, confianca);
  int anguloAtual = modoManual ? servoManual
                   : (estado == 1 || estado == 3) ? 90 : 0;
  publicar(temp, umid, pres, co2, rad, estado, confianca, anguloAtual);

  Serial.printf("T=%.1f H=%.0f P=%.1f CO2=%.0f R=%.2f -> %s (%.0f%%)\n",
                temp, umid, pres, co2, rad, CLASSES[estado], confianca * 100);
}
