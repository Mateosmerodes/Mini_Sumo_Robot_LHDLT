// hardware_robot.h — acceso al hardware de la placa base v1.2 (motores, sensores, batería).
#pragma once
#include <Arduino.h>

#include "estrategia.h"

namespace hw {
void iniciar_motores();
// Velocidades −1 … 1 por lado (los dos motores de cada lado reciben lo mismo).
void mover(float izq, float der);
void frenar();          // IN1 = IN2 = 1 en los cuatro (freno, decaimiento lento)
void rueda_libre();     // IN1 = IN2 = 0
void drivers(bool habilitar);   // DRV_EN (U3 lo combina con KILL del módulo)
bool fallo_driver();            // nFAULT a 0
float corriente_motor_A(uint8_t m);   // 0..3, por IPROPI

void iniciar_linea();
void calibrar_linea(uint32_t duracion_ms);   // sobre negro, al encender
void leer_linea(bool blanco[N_LIN], uint16_t mv[N_LIN]);

// Devuelve el número de ToF que han respondido (0 … 6).
uint8_t iniciar_tof();
// No bloquea: actualiza las distancias de los sensores que tengan una medida nueva.
void leer_tof(uint16_t mm[N_TOF]);

float vbat_V();
bool start_alto();
bool boton();
}  // namespace hw
