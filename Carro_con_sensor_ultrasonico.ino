#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "INFINITUMA09E_2.4";
const char* password = "YxMC9dtMRz";

WebServer server(80);

// Pines del puente H
const int ENA = 7;
const int IN1 = 6;
const int IN2 = 5;
const int ENB = 2;
const int IN3 = 4;
const int IN4 = 3;

// Pines del sensor ultrasónico
const int TRIG = 20;
const int ECHO = 1;

long distancia;

void medirDistancia() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duracion = pulseIn(ECHO, HIGH);
  distancia = duracion * 0.034 / 2;  // Fórmula en cm
}

void detenerMotores() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void setup() {
  Serial.begin(115200);

  // Configuración de pines
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);

  // Conexión WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConexión WiFi establecida");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());

  // Configurar rutas del servidor
  server.on("/adelante", []() {
    medirDistancia();
    if (distancia < 30) {
      detenerMotores();
      server.send(200, "text/plain", "Obstáculo detectado: motores detenidos");
    } else {
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      analogWrite(ENA, 200);
      analogWrite(ENB, 200);
      server.send(200, "text/plain", "Motores avanzando");
    }
  });

  server.on("/atras", []() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 200);
    analogWrite(ENB, 200);
    server.send(200, "text/plain", "Motores retrocediendo");
  });

  server.on("/girar_derecha", []() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, 200);
    analogWrite(ENB, 200);
    server.send(200, "text/plain", "Giro a la derecha");
  });

  server.on("/girar_izquierda", []() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 200);
    analogWrite(ENB, 200);
    server.send(200, "text/plain", "Giro a la izquierda");
  });

  server.on("/detener", []() {
    detenerMotores();
    server.send(200, "text/plain", "Motores detenidos");
  });

  server.begin();
  Serial.println("Servidor iniciado");
}

void loop() {
  server.handleClient();
}
