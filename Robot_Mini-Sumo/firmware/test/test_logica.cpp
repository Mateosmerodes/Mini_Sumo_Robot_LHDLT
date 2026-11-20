// Pruebas en el PC de la lógica de arranque y de estrategia (no necesitan el robot).
//   g++ -std=c++17 -Wall -Wextra -I ../sumo_lhdt test_logica.cpp -o test_logica && ./test_logica
// Comprueban el comportamiento ESPERADO según docs/07-Firmware.md. No sustituyen a las pruebas
// con el módulo ST4RT real ni en el dohyo.
#include <cstdio>
#include <cstdlib>

#include "arranque.h"
#include "estrategia.h"

static int fallos = 0;
#define CHECK(c)                                                  \
  do {                                                            \
    if (!(c)) {                                                   \
      std::printf("FALLO %s:%d  %s\n", __FILE__, __LINE__, #c);   \
      fallos++;                                                   \
    }                                                             \
  } while (0)

static void arranque_normal() {
  Arranque a(2);
  CHECK(!a.actualizar(false, 0));
  CHECK(a.estado() == EstadoArranque::ESPERA);
  a.actualizar(false, 1);
  a.actualizar(true, 10);  // 1.ª muestra alta: aún no
  CHECK(a.estado() == EstadoArranque::ESPERA);
  CHECK(a.actualizar(true, 11));  // 2.ª: arranca
  CHECK(a.estado() == EstadoArranque::COMBATE);
  CHECK(a.t_cambio_ms() == 11);
  CHECK(!a.reanudado_tras_reinicio());
  a.actualizar(false, 500);
  CHECK(a.estado() == EstadoArranque::COMBATE);  // un pico aislado no para
  a.actualizar(true, 501);
  CHECK(a.estado() == EstadoArranque::COMBATE);
  a.actualizar(false, 600);
  CHECK(a.actualizar(false, 601));
  CHECK(a.estado() == EstadoArranque::PARADO);
  for (uint32_t t = 700; t < 800; t++) a.actualizar(true, t);  // no rearranca sin reiniciar
  CHECK(a.estado() == EstadoArranque::PARADO);
}

static void arranque_ruido() {
  Arranque a(2);
  a.actualizar(false, 0);
  for (uint32_t t = 1; t < 100; t++) a.actualizar(t % 2, t);  // alterna 0/1: nunca 2 iguales a 1
  CHECK(a.estado() == EstadoArranque::ESPERA);
}

static void arranque_reinicio_en_combate() {
  Arranque a(2);
  CHECK(a.actualizar(true, 5));  // primera lectura ya a 1: el módulo seguía en combate
  CHECK(a.estado() == EstadoArranque::COMBATE);
  CHECK(a.reanudado_tras_reinicio());
}

static Percepcion vacia() { return Percepcion{}; }

static void estrategia_busca_y_se_mueve() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  for (uint32_t t = 0; t < 6000; t += 10) {  // nunca quieto (regla de 5 s)
    Orden o = e.decidir(p, t);
    CHECK(o.izq != 0 || o.der != 0);
  }
}

static void estrategia_ataca_de_frente() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  p.tof_mm[TOF_F] = 300;
  Orden o = e.decidir(p, 10);
  CHECK(e.modo() == Modo::ATACAR);
  CHECK(o.izq > 0 && o.der > 0);
  CHECK(o.izq == o.der);
  p.tof_mm[TOF_F] = 100;  // cerca: a fondo
  o = e.decidir(p, 20);
  CHECK(o.izq == 1.0f && o.der == 1.0f && o.a_fondo);
}

static void estrategia_gira_hacia_el_rival() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  p.tof_mm[TOF_FL] = 300;  // a la izquierda: rueda derecha más rápida
  Orden o = e.decidir(p, 10);
  CHECK(o.der > o.izq);
  p = vacia();
  p.tof_mm[TOF_R] = 300;  // a la derecha (lateral): giro en el sitio a la derecha
  o = e.decidir(p, 20);
  CHECK(o.izq > 0 && o.der < 0);
  p = vacia();
  p.tof_mm[TOF_L] = 300;
  o = e.decidir(p, 30);
  CHECK(o.izq < 0 && o.der > 0);
}

static void estrategia_ignora_lejos() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  p.tof_mm[TOF_F] = 900;  // fuera del dohyo
  e.decidir(p, 10);
  CHECK(e.modo() == Modo::BUSCAR);
}

static void estrategia_borde_tiene_prioridad() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  p.tof_mm[TOF_F] = 100;
  p.blanco[LIN_FL] = true;
  Orden o = e.decidir(p, 10);
  CHECK(e.modo() == Modo::BORDE_ATRAS);
  CHECK(o.izq < 0 && o.der < 0);
  p.blanco[LIN_FL] = false;  // ya fuera del blanco: sigue la maniobra
  o = e.decidir(p, 10 + cfg::T_RETROCESO_BORDE_MS + 1);
  CHECK(e.modo() == Modo::BORDE_GIRO);
  CHECK(o.izq > 0 && o.der < 0);  // el borde estaba a la izquierda: gira a la derecha
  p.tof_mm[TOF_F] = 0;
  e.decidir(p, 10 + cfg::T_RETROCESO_BORDE_MS + cfg::T_GIRO_BORDE_MS + 5);
  CHECK(e.modo() == Modo::BUSCAR);
}

static void estrategia_borde_trasero() {
  Estrategia e;
  e.reiniciar(0);
  Percepcion p = vacia();
  p.blanco[LIN_RR] = true;
  Orden o = e.decidir(p, 10);
  CHECK(e.modo() == Modo::BORDE_ADELANTE);
  CHECK(o.izq > 0 && o.der > 0);
}

int main() {
  arranque_normal();
  arranque_ruido();
  arranque_reinicio_en_combate();
  estrategia_busca_y_se_mueve();
  estrategia_ataca_de_frente();
  estrategia_gira_hacia_el_rival();
  estrategia_ignora_lejos();
  estrategia_borde_tiene_prioridad();
  estrategia_borde_trasero();
  if (fallos) {
    std::printf("%d comprobaciones fallidas\n", fallos);
    return EXIT_FAILURE;
  }
  std::printf("OK: todas las comprobaciones de lógica pasan\n");
  return EXIT_SUCCESS;
}
