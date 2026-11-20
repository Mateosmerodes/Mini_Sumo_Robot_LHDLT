// estrategia.h — decisiones de combate (sin dependencias de Arduino, se prueba en el PC).
//
// Prioridades, de mayor a menor:
//   1. Borde: si un sensor de línea ve blanco, alejarse del borde (retroceder y girar, o avanzar).
//   2. Ataque: si algún ToF ve al rival, orientarse hacia él y empujar (a fondo si está cerca o hay
//      contacto por corriente).
//   3. Búsqueda: girar hacia el último lado donde se vio al rival y, si no aparece, avanzar un tramo.
// Nunca se queda quieto en COMBATE (regla de los 5 s, art. 14).
// Nota: el reglamento prohíbe girar sobre sí mismo "como forma de ataque"; aquí el giro en el sitio se
// usa solo para buscar y orientarse, nunca como ataque. Confirmar con el juez si hay dudas.
#pragma once
#include <stdint.h>

#include <initializer_list>

#include "config.h"

enum Tof : uint8_t { TOF_L = 0, TOF_FL, TOF_F, TOF_FR, TOF_R, TOF_B, N_TOF };
enum Linea : uint8_t { LIN_FL = 0, LIN_FR, LIN_RL, LIN_RR, N_LIN };

struct Percepcion {
  bool blanco[N_LIN] = {false, false, false, false};
  uint16_t tof_mm[N_TOF] = {0, 0, 0, 0, 0, 0};  // 0 = sin lectura válida
  bool contacto = false;                         // corriente de empuje alta
};

struct Orden {
  float izq = 0, der = 0;  // -1 … 1
  bool freno = false;
  bool a_fondo = false;    // empuje a potencia máxima: no se aplica la compensación de batería
};

enum class Modo : uint8_t { BUSCAR, ATACAR, BORDE_ATRAS, BORDE_GIRO, BORDE_ADELANTE };

class Estrategia {
 public:
  void reiniciar(uint32_t t) {
    modo_ = Modo::BUSCAR;
    t_modo_ = t;
    giro_izq_ = true;
  }

  static bool valido(uint16_t mm) { return mm >= cfg::TOF_MIN_MM && mm <= cfg::TOF_MAX_MM; }

  Orden decidir(const Percepcion& p, uint32_t t) {
    // ---------- 1. borde (siempre primero)
    const bool bf = p.blanco[LIN_FL] || p.blanco[LIN_FR];
    const bool br = p.blanco[LIN_RL] || p.blanco[LIN_RR];
    if (bf && modo_ != Modo::BORDE_ATRAS && modo_ != Modo::BORDE_GIRO) {
      // girar luego hacia el lado contrario al sensor que ha visto el borde
      giro_izq_ = p.blanco[LIN_FR] && !p.blanco[LIN_FL];
      cambiar(Modo::BORDE_ATRAS, t);
    } else if (br && !bf && modo_ != Modo::BORDE_ADELANTE) {
      cambiar(Modo::BORDE_ADELANTE, t);
    }
    switch (modo_) {
      case Modo::BORDE_ATRAS:
        if (t - t_modo_ < cfg::T_RETROCESO_BORDE_MS) return {-cfg::POT_CRUCERO, -cfg::POT_CRUCERO, false};
        cambiar(Modo::BORDE_GIRO, t);
        [[fallthrough]];
      case Modo::BORDE_GIRO:
        if (t - t_modo_ < cfg::T_GIRO_BORDE_MS) return giro(cfg::POT_CRUCERO);
        cambiar(Modo::BUSCAR, t);
        break;
      case Modo::BORDE_ADELANTE:
        if (br || t - t_modo_ < cfg::T_RETROCESO_BORDE_MS) return {cfg::POT_CRUCERO, cfg::POT_CRUCERO, false};
        cambiar(Modo::BUSCAR, t);
        break;
      default:
        break;
    }

    // ---------- 2. ataque
    const bool vL = valido(p.tof_mm[TOF_L]), vFL = valido(p.tof_mm[TOF_FL]), vF = valido(p.tof_mm[TOF_F]);
    const bool vFR = valido(p.tof_mm[TOF_FR]), vR = valido(p.tof_mm[TOF_R]), vB = valido(p.tof_mm[TOF_B]);
    if (vFL || vF || vFR) {
      cambiar(Modo::ATACAR, t);
      // error de orientación: −1 (rival a la izquierda) … +1 (a la derecha)
      float e = 0;
      if (vFL && !vFR) e = vF ? -0.35f : -1.0f;
      else if (vFR && !vFL) e = vF ? 0.35f : 1.0f;
      uint16_t d = 0xFFFF;
      for (uint8_t i : {TOF_FL, TOF_F, TOF_FR})
        if (valido(p.tof_mm[i]) && p.tof_mm[i] < d) d = p.tof_mm[i];
      const bool fondo = p.contacto || d <= cfg::TOF_CERCA_MM;
      const float base = fondo ? cfg::POT_ATAQUE : cfg::POT_CRUCERO;
      const float g = cfg::GANANCIA_GIRO * e;
      if (e < 0) giro_izq_ = true;
      if (e > 0) giro_izq_ = false;
      return {limitar(base + g * base), limitar(base - g * base), false, fondo};
    }
    if (vL || vR || vB) {  // rival a un lado o detrás: girar hacia él en el sitio
      cambiar(Modo::BUSCAR, t);
      giro_izq_ = vL || (vB && giro_izq_);
      return giro(cfg::POT_CRUCERO);
    }

    // ---------- 3. búsqueda
    if (modo_ != Modo::BUSCAR) cambiar(Modo::BUSCAR, t);
    const uint32_t ciclo = cfg::T_BUSQUEDA_GIRO_MS + cfg::T_BUSQUEDA_AVANCE_MS;
    const uint32_t fase = (t - t_modo_) % ciclo;
    if (fase < cfg::T_BUSQUEDA_GIRO_MS) return giro(cfg::POT_BUSQUEDA);
    return {cfg::POT_BUSQUEDA, cfg::POT_BUSQUEDA, false};
  }

  Modo modo() const { return modo_; }

 private:
  Orden giro(float v) const { return giro_izq_ ? Orden{-v, v, false} : Orden{v, -v, false}; }
  static float limitar(float v) { return v > 1 ? 1 : (v < -1 ? -1 : v); }
  void cambiar(Modo m, uint32_t t) {
    if (m != modo_) {
      modo_ = m;
      t_modo_ = t;
    }
  }
  Modo modo_ = Modo::BUSCAR;
  uint32_t t_modo_ = 0;
  bool giro_izq_ = true;
};
