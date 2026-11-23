// pines.h — ESP32-S3-DevKitC-1 sobre la placa base v1.2 (HOMBRES DE LAS TABERNAS)
// Fuente única: hardware/pcb/scripts/design.py. Si cambia allí, cambia aquí.
#pragma once

namespace pin {
// Sensores de línea QRE1113 (ADC1)
constexpr int LINE_FL = 1, LINE_FR = 2, LINE_RL = 4, LINE_RR = 5;
// IPROPI de los DRV8874 (ADC1): V = I · 455 µA/A · 1,5 kΩ
constexpr int ISENSE_M1 = 6, ISENSE_M2 = 7, ISENSE_M3 = 8, ISENSE_M4 = 9;
// Batería: divisor 100 k / 33 k (ADC1)
constexpr int VBAT_SENSE = 10;
// Motores (modo PWM del DRV8874). M1 izq. del., M2 izq. tras., M3 der. del., M4 der. tras.
constexpr int M1_IN1 = 11, M1_IN2 = 12, M2_IN1 = 13, M2_IN2 = 14;
constexpr int M3_IN1 = 15, M3_IN2 = 16, M4_IN1 = 45, M4_IN2 = 46;  // 45/46: pines de arranque, a 0 al encender
// DRV_EN: el firmware habilita los drivers. En la v1.2 nSLEEP = DRV_EN AND KILL (U3), así que el
// módulo de arranque puede dormirlos aunque este pin esté a 1.
constexpr int DRV_EN = 21, DRV_nFAULT = 38;
// I2C de los VL53L0X y XSHUT de cada uno
constexpr int I2C_SDA = 39, I2C_SCL = 40;
constexpr int XSHUT_L = 41, XSHUT_FL = 42, XSHUT_F = 47, XSHUT_FR = 48, XSHUT_R = 3, XSHUT_B = 17;
// Módulo de arranque ST4RT: salida S (START) a través de R63 (1 k), con R65 (100 k) a GND
constexpr int ST_START = 18;
// Botón BOOT de la DevKit (en la propia DevKit; GPIO0 no tiene zócalo en la placa base)
constexpr int BTN_USER = 0;
}  // namespace pin
