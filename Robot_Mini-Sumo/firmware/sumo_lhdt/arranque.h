// arranque.h — lógica de arranque/parada con el módulo ST4RT (sin dependencias de Arduino).
//
// Comportamiento de referencia: start module de p1r.se / startmodule.com (código abierto,
// github.com/p1rse/robot-sumo-start-module), con el que Sobotz anuncia que el ST4RT es compatible:
//   - Encendido ("power on"): START = 0, KILL = 1.
//   - Orden de inicio del juez (RC5, dirección 0x07, comando = id_dohyo + 1): START = 1, KILL = 1.
//   - Orden de parada (dirección 0x07, comando = id_dohyo): START = 0, KILL = 0. El módulo se queda
//     parado hasta que se le quita la alimentación.
//   - El módulo guarda su estado en memoria no volátil: si el robot se reinicia en pleno combate,
//     al volver la alimentación START vuelve a 1 sin nueva orden.
// ⚠️ Sin confirmar en el ST4RT real hasta recibirlo (ver docs/06-Modulo-arranque-ST4RT.md).
//
// Este firmware replica esa máquina de estados a partir de START:
//   ESPERA  --START=1-->  COMBATE  --START=0-->  PARADO (definitivo hasta reiniciar)
// Si START ya está a 1 en la primera lectura tras arrancar el ESP32, se entra en COMBATE de inmediato
// (el módulo estaba en combate y el ESP32 se ha reiniciado: hay que seguir luchando).
#pragma once
#include <stdint.h>

enum class EstadoArranque : uint8_t { ESPERA, COMBATE, PARADO };

class Arranque {
 public:
  explicit Arranque(uint8_t muestras = 2) : n_(muestras ? muestras : 1) {}

  // Llamar en cada vuelta del bucle con el nivel leído en START.
  // Devuelve true si el estado ha cambiado en esta llamada.
  bool actualizar(bool start_alto, uint32_t t_ms) {
    if (primera_) {
      primera_ = false;
      nivel_ = start_alto;
      cuenta_ = n_;
      if (start_alto) {  // reinicio en pleno combate
        reanudado_ = true;
        return cambiar(EstadoArranque::COMBATE, t_ms);
      }
      return false;
    }
    if (start_alto == nivel_) {
      if (cuenta_ < n_) cuenta_++;
    } else {
      nivel_ = start_alto;
      cuenta_ = 1;
    }
    if (cuenta_ < n_) return false;
    switch (estado_) {
      case EstadoArranque::ESPERA:
        if (nivel_) return cambiar(EstadoArranque::COMBATE, t_ms);
        break;
      case EstadoArranque::COMBATE:
        if (!nivel_) return cambiar(EstadoArranque::PARADO, t_ms);
        break;
      case EstadoArranque::PARADO:
        break;  // no se vuelve a arrancar sin reiniciar (igual que el módulo)
    }
    return false;
  }

  EstadoArranque estado() const { return estado_; }
  uint32_t t_cambio_ms() const { return t_cambio_; }
  bool reanudado_tras_reinicio() const { return reanudado_; }

 private:
  bool cambiar(EstadoArranque e, uint32_t t) {
    estado_ = e;
    t_cambio_ = t;
    return true;
  }
  uint8_t n_;
  bool primera_ = true;
  bool nivel_ = false;
  uint8_t cuenta_ = 0;
  bool reanudado_ = false;
  EstadoArranque estado_ = EstadoArranque::ESPERA;
  uint32_t t_cambio_ = 0;
};
