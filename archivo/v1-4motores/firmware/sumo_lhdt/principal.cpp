// principal.cpp — setup() y loop() del firmware del robot mini-sumo de HOMBRES DE LAS TABERNAS (placa base v1.2)
//
// Placa: "ESP32S3 Dev Module" (core esp32 de Espressif 3.x). Librería: Pololu VL53L0X 1.3.x.
// Flujo:
//   1. Arranque del ESP32: motores en rueda libre, Wi-Fi y BT apagados, ToF y línea inicializados,
//      calibración de los sensores de línea sobre el negro del dohyo.
//   2. ESPERA: drivers despiertos (DRV_EN = 1) pero sin mover; se espera START del módulo ST4RT.
//      El robot no se mueve aunque el firmware falle: sin START no hay órdenes, y si el módulo da
//      orden de parada, KILL duerme los drivers por hardware (U3).
//   3. COMBATE: bucle a ~1 kHz → percepción → estrategia → motores. Arranca en el mismo ciclo en que
//      se detecta START (reglamento art. 5.5 y 8: "sin retraso").
//   4. PARADO: freno activo, drivers dormidos, se ignora todo hasta reiniciar (igual que el módulo).
// Ningún tiempo aquí está validado en pista: ver docs/07-Firmware.md, "Pruebas pendientes".
#include <Arduino.h>
#include <WiFi.h>

#include "arranque.h"
#include "config.h"
#include "estrategia.h"
#include "hardware_robot.h"
#include "pines.h"

static Arranque arranque(cfg::ARRANQUE_MUESTRAS);
static Estrategia estrategia;
static Percepcion per;
static uint16_t linea_mv[N_LIN];
static uint8_t n_tof = 0;
static uint32_t t_parada = 0;

static void telemetria(uint32_t t) {
  static uint32_t ultimo = 0;
  if (t - ultimo < 100) return;
  ultimo = t;
  Serial.printf("t=%lu est=%u modo=%u vbat=%.2f lin=%u,%u,%u,%u tof=%u,%u,%u,%u,%u,%u flt=%d\n",
                (unsigned long)t, (unsigned)arranque.estado(), (unsigned)estrategia.modo(), hw::vbat_V(),
                linea_mv[0], linea_mv[1], linea_mv[2], linea_mv[3], per.tof_mm[0], per.tof_mm[1],
                per.tof_mm[2], per.tof_mm[3], per.tof_mm[4], per.tof_mm[5], hw::fallo_driver());
}

void setup() {
  hw::iniciar_motores();  // lo primero: entradas de los drivers a 0 y DRV_EN a 0
  hw::rueda_libre();
  pinMode(pin::ST_START, INPUT);  // R65 (100 k) a GND en la placa
  pinMode(pin::BTN_USER, INPUT_PULLUP);
  WiFi.mode(WIFI_OFF);  // autónomo: sin radio en combate
  btStop();
  Serial.begin(115200);

  // Si el módulo ya da START (reinicio en pleno combate), no se pierde tiempo en calibrar.
  arranque.actualizar(hw::start_alto(), millis());
  hw::iniciar_linea();
  n_tof = hw::iniciar_tof();
  if (arranque.estado() == EstadoArranque::ESPERA) hw::calibrar_linea(cfg::T_CALIBRACION_MS);
  Serial.printf("LHDT v1.2: %u/6 ToF, reanudado=%d\n", n_tof, arranque.reanudado_tras_reinicio());
  hw::drivers(true);  // despiertos para arrancar sin retardo (t_wake del DRV8874 ≈ 1 ms)
  estrategia.reiniciar(millis());
}

void loop() {
  const uint32_t t = millis();
  const bool cambio = arranque.actualizar(hw::start_alto(), t);

  hw::leer_linea(per.blanco, linea_mv);
  hw::leer_tof(per.tof_mm);

  switch (arranque.estado()) {
    case EstadoArranque::ESPERA:
      hw::rueda_libre();
      break;

    case EstadoArranque::COMBATE: {
      if (cambio) estrategia.reiniciar(t);
      float i_media = 0;
      for (uint8_t m = 0; m < 4; m++) i_media += hw::corriente_motor_A(m);
      per.contacto = (i_media / 4) > cfg::I_CONTACTO_A;
      Orden o = estrategia.decidir(per, t);
      const float vbat = hw::vbat_V();
      float k = 1.0f;
      if (vbat > cfg::VBAT_REFERENCIA_V && !o.a_fondo) k = cfg::VBAT_REFERENCIA_V / vbat;
      if (vbat < cfg::VBAT_LIMITE_V) k = 0.5f;
      o.izq *= k;
      o.der *= k;
      if (o.freno) hw::frenar();
      else hw::mover(o.izq, o.der);
      break;
    }

    case EstadoArranque::PARADO:
      if (cambio) t_parada = t;
      if (t - t_parada < cfg::T_FRENO_PARADA_MS) {
        hw::frenar();
      } else {
        hw::rueda_libre();
        hw::drivers(false);
      }
      break;
  }
  telemetria(t);
}
