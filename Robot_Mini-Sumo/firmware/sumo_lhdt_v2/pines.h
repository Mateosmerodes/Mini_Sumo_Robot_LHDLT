// pines.h — ESP32-S3-DevKitC-1 sobre la placa v2 básica (LHDT · Los Hombres de las Tabernas)
// Fuente única: hardware/pcb/scripts/design.py (diccionario GPIO). Si cambia allí, cambia aquí.
#pragma once

namespace pin {
// Motor izquierdo (módulo TB6612FNG U3, canales A y B en paralelo)
constexpr int MI_PWM = 11, MI_IN1 = 12, MI_IN2 = 13;
// Motor derecho (módulo TB6612FNG U4, canales A y B en paralelo)
constexpr int MD_PWM = 47, MD_IN1 = 21, MD_IN2 = 48;
// STBY de los dos módulos: 0 = motores apagados (R3 lo deja a 0 mientras arranca la ESP32)
constexpr int MOT_STBY = 14;
// Sensores de suelo QRE1113 analógicos (ADC1)
constexpr int LINEA_IZQ = 4, LINEA_DER = 1;
// Sensores de distancia VL53L0X (I2C) y su pin XSHUT
constexpr int I2C_SDA = 39, I2C_SCL = 40;
constexpr int XSHUT_IZQ = 5, XSHUT_DER = 2;
// Módulo de arranque ST4RT: S (START) y K (KILL), con pull-down de 100 k en la placa
constexpr int ST_START = 17, ST_KILL = 18;
// Batería: divisor 100 k / 33 k (ADC1)
constexpr int VBAT_SENSE = 10;
}  // namespace pin
