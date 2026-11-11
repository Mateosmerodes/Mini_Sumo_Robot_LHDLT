// hardware_robot.cpp — implementación para el core Arduino-ESP32 3.x (ESP-IDF 5.1).
#include "hardware_robot.h"

#include <VL53L0X.h>  // Pololu VL53L0X 1.3.x
#include <Wire.h>

#include "config.h"
#include "pines.h"

namespace hw {
namespace {
constexpr int IN1[4] = {pin::M1_IN1, pin::M2_IN1, pin::M3_IN1, pin::M4_IN1};
constexpr int IN2[4] = {pin::M1_IN2, pin::M2_IN2, pin::M3_IN2, pin::M4_IN2};
constexpr int ISENSE[4] = {pin::ISENSE_M1, pin::ISENSE_M2, pin::ISENSE_M3, pin::ISENSE_M4};
constexpr uint32_t PWM_MAX = (1u << cfg::PWM_BITS) - 1;

constexpr int LINE[N_LIN] = {pin::LINE_FL, pin::LINE_FR, pin::LINE_RL, pin::LINE_RR};
uint16_t umbral_mv[N_LIN] = {cfg::UMBRAL_POR_DEFECTO_MV, cfg::UMBRAL_POR_DEFECTO_MV,
                             cfg::UMBRAL_POR_DEFECTO_MV, cfg::UMBRAL_POR_DEFECTO_MV};

// Orden de los ToF = enum Tof: L, FL, F, FR, R, B
constexpr int XSHUT[N_TOF] = {pin::XSHUT_L, pin::XSHUT_FL, pin::XSHUT_F, pin::XSHUT_FR, pin::XSHUT_R, pin::XSHUT_B};
VL53L0X tof[N_TOF];
bool tof_ok[N_TOF] = {};

// Un motor: v en −1 … 1. Adelante: IN1 = 1, IN2 = PWM invertido (freno en el tiempo apagado,
// decaimiento lento: el par responde más lineal al ciclo de trabajo que con rueda libre).
void motor(uint8_t m, float v) {
  v *= cfg::SIGNO_M[m];
  if (v > 1) v = 1;
  if (v < -1) v = -1;
  const uint32_t off = (uint32_t)((1.0f - (v >= 0 ? v : -v)) * PWM_MAX + 0.5f);
  if (v >= 0) {
    ledcWrite(IN1[m], PWM_MAX);
    ledcWrite(IN2[m], off);
  } else {
    ledcWrite(IN1[m], off);
    ledcWrite(IN2[m], PWM_MAX);
  }
}
}  // namespace

void iniciar_motores() {
  pinMode(pin::DRV_EN, OUTPUT);
  digitalWrite(pin::DRV_EN, LOW);
  pinMode(pin::DRV_nFAULT, INPUT);  // pull-up externa R16
  for (uint8_t m = 0; m < 4; m++) {
    ledcAttach(IN1[m], cfg::PWM_HZ, cfg::PWM_BITS);
    ledcAttach(IN2[m], cfg::PWM_HZ, cfg::PWM_BITS);
    ledcWrite(IN1[m], 0);
    ledcWrite(IN2[m], 0);
  }
}

void mover(float izq, float der) {
  motor(0, izq);
  motor(1, izq);
  motor(2, der);
  motor(3, der);
}

void frenar() {
  for (uint8_t m = 0; m < 4; m++) {
    ledcWrite(IN1[m], PWM_MAX);
    ledcWrite(IN2[m], PWM_MAX);
  }
}

void rueda_libre() {
  for (uint8_t m = 0; m < 4; m++) {
    ledcWrite(IN1[m], 0);
    ledcWrite(IN2[m], 0);
  }
}

void drivers(bool habilitar) { digitalWrite(pin::DRV_EN, habilitar ? HIGH : LOW); }
bool fallo_driver() { return digitalRead(pin::DRV_nFAULT) == LOW; }

float corriente_motor_A(uint8_t m) {
  return analogReadMilliVolts(ISENSE[m]) / 1000.0f / cfg::IPROPI_V_POR_A;
}

void iniciar_linea() {
  analogReadResolution(12);
  for (int p : LINE) analogSetPinAttenuation(p, ADC_11db);
  for (int p : ISENSE) analogSetPinAttenuation(p, ADC_11db);
  analogSetPinAttenuation(pin::VBAT_SENSE, ADC_11db);
}

void calibrar_linea(uint32_t duracion_ms) {
  uint32_t suma[N_LIN] = {}, n = 0;
  const uint32_t t0 = millis();
  while (millis() - t0 < duracion_ms) {
    for (uint8_t i = 0; i < N_LIN; i++) suma[i] += analogReadMilliVolts(LINE[i]);
    n++;
    delay(2);
  }
  for (uint8_t i = 0; i < N_LIN; i++) {
    const uint32_t negro = n ? suma[i] / n : 0;
    // Validez: sobre negro la salida debe estar claramente alta. Si no, umbral por defecto.
    umbral_mv[i] = (negro > 800) ? (uint16_t)(negro * cfg::FACTOR_UMBRAL_BLANCO) : cfg::UMBRAL_POR_DEFECTO_MV;
  }
}

void leer_linea(bool blanco[N_LIN], uint16_t mv[N_LIN]) {
  for (uint8_t i = 0; i < N_LIN; i++) {
    mv[i] = analogReadMilliVolts(LINE[i]);
    blanco[i] = mv[i] < umbral_mv[i];
  }
}

uint8_t iniciar_tof() {
  Wire.begin(pin::I2C_SDA, pin::I2C_SCL, 400000);
  for (int p : XSHUT) {
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);  // todos apagados: todos arrancan en 0x29
  }
  delay(10);
  uint8_t n = 0;
  for (uint8_t i = 0; i < N_TOF; i++) {
    digitalWrite(XSHUT[i], HIGH);  // se enciende uno y se le da su dirección
    delay(3);
    tof[i].setTimeout(30);
    tof_ok[i] = tof[i].init();
    if (!tof_ok[i]) continue;
    tof[i].setAddress(0x30 + i);
    tof[i].setMeasurementTimingBudget(cfg::TOF_PRESUPUESTO_US);
    tof[i].startContinuous(0);
    n++;
  }
  return n;
}

void leer_tof(uint16_t mm[N_TOF]) {
  for (uint8_t i = 0; i < N_TOF; i++) {
    if (!tof_ok[i]) {
      mm[i] = 0;
      continue;
    }
    // Lectura no bloqueante: solo si el sensor tiene una medida nueva (bits 0–2 del estado).
    if ((tof[i].readReg(VL53L0X::RESULT_INTERRUPT_STATUS) & 0x07) == 0) continue;
    const uint16_t d = tof[i].readRangeContinuousMillimeters();
    mm[i] = (tof[i].timeoutOccurred() || d >= 8190) ? 0 : d;
  }
}

float vbat_V() { return analogReadMilliVolts(pin::VBAT_SENSE) / 1000.0f * cfg::DIVISOR_VBAT; }
bool start_alto() { return digitalRead(pin::ST_START) == HIGH; }
bool boton() { return digitalRead(pin::BTN_USER) == LOW; }
}  // namespace hw
