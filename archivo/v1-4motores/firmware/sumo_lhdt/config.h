// config.h — parámetros ajustables. Los valores marcados "A AJUSTAR" son hipótesis hasta probar
// el robot en un dohyo real; no son datos medidos.
#pragma once
#include <stdint.h>

namespace cfg {
// ---------------------------------------------------------------- arranque
// Muestras consecutivas iguales de START para aceptar un cambio (filtro de ruido).
// El bucle va a ≥ 1 kHz, así que 2 muestras ≈ 1–2 ms de retardo: "sin retraso" a efectos del juez.
constexpr uint8_t ARRANQUE_MUESTRAS = 2;
// Al parar: tiempo de freno activo (IN1 = IN2 = 1) antes de dormir los drivers.
// Con la v1.2 el KILL del módulo duerme los drivers por hardware en el mismo instante, así que este
// freno solo actúa si el módulo baja START antes que KILL o si no hay KILL (JP1 cerrado).
constexpr uint32_t T_FRENO_PARADA_MS = 300;

// ---------------------------------------------------------------- motores
constexpr uint32_t PWM_HZ = 20000;  // fuera del rango audible
constexpr uint8_t PWM_BITS = 10;
// Signo de cada motor (1 o -1). Los del lado derecho van montados en espejo. A AJUSTAR en la
// primera prueba con las ruedas en el aire: todos deben girar "hacia delante" con avanzar(0,5).
constexpr int8_t SIGNO_M[4] = {1, 1, -1, -1};
// Potencia máxima por defecto en marcha (fracción de 1). Los motores de 6 V van a 7,4–8,4 V.
// v1.2: 0,65 (antes 0,75). Con 0,75 y la batería llena el robot no frena antes de sacar las ruedas
// delanteras si el agarre es μ = 0,6 (hardware/calculos, apartado "borde").
constexpr float POT_CRUCERO = 0.65f;
constexpr float POT_ATAQUE = 1.0f;
constexpr float POT_BUSQUEDA = 0.45f;
// Compensación de batería: búsqueda y crucero se escalan a VBAT_REFERENCIA_V / VBAT, para ir igual de
// rápido con la batería llena (8,4 V) que a 7,4 V. El ataque a fondo (rival a < 15 cm) no se escala.
constexpr float VBAT_REFERENCIA_V = 7.4f;

// ---------------------------------------------------------------- sensores de línea
// QRE1113: más luz reflejada (blanco) = tensión de salida MÁS BAJA.
// Umbral = FACTOR × lectura media sobre negro tomada al encender (el robot se enciende sobre el dohyo).
constexpr float FACTOR_UMBRAL_BLANCO = 0.55f;  // A AJUSTAR
constexpr uint16_t UMBRAL_POR_DEFECTO_MV = 1500;  // si la calibración no es válida. A AJUSTAR
constexpr uint32_t T_CALIBRACION_MS = 200;

// ---------------------------------------------------------------- sensores de rival (VL53L0X)
constexpr uint32_t TOF_PRESUPUESTO_US = 20000;  // 20 ms por medida (mínimo práctico ~20 ms)
constexpr uint16_t TOF_MAX_MM = 650;            // dohyo de 77 cm: más lejos es público o ruido
constexpr uint16_t TOF_MIN_MM = 15;
constexpr uint16_t TOF_CERCA_MM = 150;          // a esta distancia se empuja a fondo

// ---------------------------------------------------------------- estrategia (tiempos A AJUSTAR)
constexpr uint32_t T_RETROCESO_BORDE_MS = 180;
constexpr uint32_t T_GIRO_BORDE_MS = 220;
constexpr uint32_t T_BUSQUEDA_GIRO_MS = 1500;   // girando sin ver nada → avanzar un tramo
constexpr uint32_t T_BUSQUEDA_AVANCE_MS = 350;
constexpr float GANANCIA_GIRO = 0.6f;

// ---------------------------------------------------------------- batería (2S)
constexpr float DIVISOR_VBAT = 133.0f / 33.0f;
constexpr float VBAT_AVISO_V = 6.8f;    // 3,4 V/celda: avisar
constexpr float VBAT_LIMITE_V = 6.4f;   // 3,2 V/celda: limitar potencia al 50 %
// IPROPI: A_IPROPI · R_IPROPI = 455 µA/A · 1,5 kΩ = 0,6825 V/A
constexpr float IPROPI_V_POR_A = 455e-6f * 1500.0f;
constexpr float I_CONTACTO_A = 1.4f;    // corriente media por motor que indica empuje. A AJUSTAR
}  // namespace cfg
