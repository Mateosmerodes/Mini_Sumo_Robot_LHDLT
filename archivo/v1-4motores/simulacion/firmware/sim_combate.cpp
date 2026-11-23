// sim_combate.cpp — simulación en el PC de la lógica del firmware sobre un dohyo virtual.
//
// Usa SIN CAMBIOS arranque.h, estrategia.h y config.h del firmware y reproduce el loop() de
// principal.cpp (compensación de batería, freno al parar, KILL por hardware con U3).
// El robot, los sensores y el módulo ST4RT son modelos simplificados (ver docs/14-Simulaciones.md):
//   - cinemática diferencial, velocidad en vacío 0,97 m/s a 7,4 V, motor de primer orden (30 ms),
//     aceleración y frenada limitadas por la adherencia (μ·g);
//   - sensores de línea en su posición real (geometria.py), blanco si están en la franja de 25 mm;
//   - 6 ToF en su posición real, haz de ±12,5°, medida nueva cada 20 ms, ruido ±10 mm;
//   - rival: caja de 100 × 100 mm, quieta o dando vueltas. No se simula el empuje entre robots.
// Compilar: g++ -O2 -std=c++17 -I ../../firmware/sumo_lhdt sim_combate.cpp -o sim_combate
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <random>
#include <string>
#include <vector>

#include "arranque.h"
#include "config.h"
#include "estrategia.h"

namespace {
constexpr double PI = 3.14159265358979;
constexpr double R_DOHYO = 0.385, FRANJA = 0.025, VIA = 0.087;  // m
constexpr double V0_7V4 = 0.97;                                 // m/s en vacío a 7,4 V
constexpr double TAU_MOTOR = 0.030, A_RUEDA_LIBRE = 2.0;        // s, m/s² (reductora, supuesto)

struct P2 { double x, y; };
// posiciones en el robot (m): x a la izquierda, y hacia delante, origen en el centro (50, 50 mm)
const P2 LIN[4] = {{0.033, 0.028}, {-0.033, 0.028}, {0.025, -0.0443}, {-0.025, -0.0443}};  // FL FR RL RR
const P2 RUEDAS[4] = {{0.0435, 0.003}, {-0.0435, 0.003}, {0.0435, -0.031}, {-0.0435, -0.031}};
struct TofPos { P2 p; double ang; };  // ang: 0 = delante, +90° = izquierda
const TofPos TOFS[6] = {{{0.047, 0.014}, PI / 2}, {{0.025, 0.023}, 0}, {{0, 0.023}, 0},
                        {{-0.025, 0.023}, 0}, {{-0.047, 0.014}, -PI / 2}, {{0, -0.046}, PI}};

struct Robot {
  double x = 0, y = 0, th = 0, vl = 0, vr = 0;
};
// Rumbo th: el robot mira hacia (−sin th, cos th); su izquierda es (−cos th, −sin th).
P2 aMundo(const Robot& r, P2 q) {
  double c = std::cos(r.th), s = std::sin(r.th);
  P2 f = {-s, c}, l = {-c, -s};
  return {r.x + q.y * f.x + q.x * l.x, r.y + q.y * f.y + q.x * l.y};
}

struct Rival { double x, y, th; double vel, radio_giro; bool activo; };

bool dentroCaja(const Rival& o, P2 p) {
  double c = std::cos(-o.th), s = std::sin(-o.th);
  double dx = p.x - o.x, dy = p.y - o.y;
  double lx = dx * c - dy * s, ly = dx * s + dy * c;
  return std::fabs(lx) <= 0.05 && std::fabs(ly) <= 0.05;
}

// distancia de un ToF al rival (mm) o 0 si no lo ve
uint16_t medirTof(const Robot& r, const TofPos& tp, const Rival& o, std::mt19937& g) {
  if (!o.activo) return 0;
  P2 p = aMundo(r, tp.p);
  double best = 1e9;
  for (double da : {-0.218, -0.11, 0.0, 0.11, 0.218}) {  // haz de ±12,5°
    double a = r.th + tp.ang + da;
    P2 d = {-std::sin(a), std::cos(a)};
    for (double s = 0.005; s < 1.2; s += 0.004) {
      P2 q = {p.x + d.x * s, p.y + d.y * s};
      if (dentroCaja(o, q)) { best = std::min(best, s); break; }
    }
  }
  if (best > 1.2) return 0;  // el VL53L0X no ve nada a su alcance: la librería da 8190 -> 0
  std::uniform_real_distribution<double> ruido(-0.010, 0.010);
  double mm = (best + ruido(g)) * 1000;
  return (uint16_t)std::max(0.0, mm);
}

struct Escenario {
  double mu = 0.8, vbat = 7.8;
  double t_start = 1.0, t_stop = 1e9;  // s
  int glitch_ms = 0;                   // ancho de pulsos falsos en START (0 = ninguno)
  double t_reinicio = -1;              // reinicio del ESP32 en pleno combate (s)
  Rival rival{0, 0, 0, 0, 0, false};
  double dur = 30;
  double esquiva_m = 0;  // el rival se aparta (desaparece) cuando el robot está a esta distancia
  unsigned semilla = 1;
  FILE* log = nullptr;
};

struct Resultado {
  bool fuera = false; double t_fuera = 0;
  double t_primer_mov = -1;  // s desde START hasta la primera orden != 0
  double t_contacto = -1;
  double max_quieto = 0;     // máximo tiempo seguido sin moverse en COMBATE (s)
  double d_parada = 0;       // m recorridos desde la orden de parada
  double v_max = 0;
  int arranques_falsos = 0;
};

Resultado simular(const Escenario& e, Robot rb) {
  std::mt19937 g(e.semilla);
  Arranque arr(cfg::ARRANQUE_MUESTRAS);
  Estrategia est;
  Percepcion per;
  Resultado res;
  Rival o = e.rival;
  uint32_t t_parada = 0;
  double quieto = 0, x_stop = 0, y_stop = 0;
  bool parado_reg = false;
  uint16_t tof_mm[6] = {};
  int fase_tof[6];
  for (int i = 0; i < 6; i++) fase_tof[i] = i * 3;
  bool en_setup = true;
  uint32_t fin_setup = 300;  // ms de setup() (ToF + calibración), supuesto
  const double vmax = V0_7V4 * e.vbat / 7.4;
  std::uniform_int_distribution<int> gl(0, 999);
  int glitch_rest = 0;
  uint32_t ult_glitch = 0;
  for (uint32_t ms = 0; ms < (uint32_t)(e.dur * 1000); ms++) {
    const double t = ms / 1000.0;
    // ---------------- módulo ST4RT (comportamiento de referencia del start module de p1r.se)
    bool start = t >= e.t_start && t < e.t_stop;
    bool kill = !(t >= e.t_stop);
    if (e.glitch_ms > 0 && t < e.t_start) {  // pulsos falsos de ruido antes de la salida
      if (glitch_rest == 0 && ms - ult_glitch > 10 && gl(g) < 5) { glitch_rest = e.glitch_ms; ult_glitch = ms + e.glitch_ms; }
      if (glitch_rest > 0) { start = true; glitch_rest--; }
    }
    // ---------------- reinicio del ESP32 en pleno combate
    if (e.t_reinicio > 0 && ms == (uint32_t)(e.t_reinicio * 1000)) {
      arr = Arranque(cfg::ARRANQUE_MUESTRAS);
      en_setup = true;
      fin_setup = ms + 300;
    }
    bool drv_en = false;
    float izq = 0, der = 0;
    bool freno = false;
    if (en_setup) {
      if (ms >= fin_setup || (fin_setup == 300 && ms == 0)) {
        // setup(): la primera lectura de START decide si se reanuda el combate
        if (ms == 0 || ms == fin_setup) arr.actualizar(start, ms);
        if (ms >= fin_setup) { en_setup = false; est.reiniciar(ms); }
      }
    } else {
      drv_en = true;
      const bool cambio = arr.actualizar(start, ms);
      // percepción
      for (int i = 0; i < 4; i++) {
        P2 p = aMundo(rb, LIN[i]);
        per.blanco[i] = std::hypot(p.x, p.y) > R_DOHYO - FRANJA;
      }
      for (int i = 0; i < 6; i++)
        if ((ms + fase_tof[i]) % (cfg::TOF_PRESUPUESTO_US / 1000) == 0) tof_mm[i] = medirTof(rb, TOFS[i], o, g);
      for (int i = 0; i < 6; i++) per.tof_mm[i] = tof_mm[i];
      switch (arr.estado()) {
        case EstadoArranque::ESPERA: break;
        case EstadoArranque::COMBATE: {
          if (cambio) est.reiniciar(ms);
          // corriente leída: el firmware no corrige por el ciclo de trabajo (ver 09_ipropi.png)
          per.contacto = false;
          Orden ord = est.decidir(per, ms);
          float k = 1.0f;
          if (e.vbat > cfg::VBAT_REFERENCIA_V && !ord.a_fondo) k = cfg::VBAT_REFERENCIA_V / e.vbat;
          if (e.vbat < cfg::VBAT_LIMITE_V) k = 0.5f;
          izq = ord.izq * k; der = ord.der * k; freno = ord.freno;
          if (res.t_primer_mov < 0 && (izq != 0 || der != 0)) res.t_primer_mov = t - e.t_start;
          break;
        }
        case EstadoArranque::PARADO:
          if (cambio) t_parada = ms;
          if (ms - t_parada < cfg::T_FRENO_PARADA_MS) freno = true;
          else drv_en = false;
          break;
      }
      if (arr.estado() == EstadoArranque::COMBATE && t < e.t_start) res.arranques_falsos = 1;
    }
    // ---------------- U3: nSLEEP = DRV_EN AND KILL
    const bool nsleep = drv_en && kill;
    // ---------------- motores y adherencia
    const double amax = e.mu * 9.81, dt = 0.001;
    for (int lado = 0; lado < 2; lado++) {
      double& v = lado == 0 ? rb.vl : rb.vr;
      double cmd = lado == 0 ? izq : der;
      double a;
      if (!nsleep || (!freno && cmd == 0 && arr.estado() != EstadoArranque::COMBATE)) {
        a = -std::copysign(std::min(A_RUEDA_LIBRE, std::fabs(v) / dt), v);  // rueda libre
      } else if (freno) {
        a = -v / TAU_MOTOR;
      } else {
        a = (cmd * vmax - v) / TAU_MOTOR;
      }
      a = std::max(-amax, std::min(amax, a));
      v += a * dt;
    }
    const double v = (rb.vl + rb.vr) / 2, w = (rb.vr - rb.vl) / VIA;
    rb.x += -std::sin(rb.th) * v * dt;
    rb.y += std::cos(rb.th) * v * dt;
    rb.th += w * dt;
    res.v_max = std::max(res.v_max, std::fabs(v));
    // rival
    if (o.activo && o.vel > 0) {
      o.th += o.vel / o.radio_giro * dt;
      o.x += -std::sin(o.th) * o.vel * dt; o.y += std::cos(o.th) * o.vel * dt;
    }
    if (o.activo && res.t_contacto < 0) {
      P2 frente = aMundo(rb, {0, 0.05});
      if (dentroCaja(o, frente) || std::hypot(rb.x - o.x, rb.y - o.y) < 0.105) res.t_contacto = t - e.t_start;
    }
    if (o.activo && e.esquiva_m > 0 && std::hypot(rb.x - o.x, rb.y - o.y) < e.esquiva_m) o.activo = false;
    // ¿fuera?
    for (auto q : RUEDAS) {
      P2 p = aMundo(rb, q);
      if (std::hypot(p.x, p.y) > R_DOHYO && !res.fuera) { res.fuera = true; res.t_fuera = t; }
    }
    if (arr.estado() == EstadoArranque::COMBATE) {
      if (std::fabs(rb.vl) + std::fabs(rb.vr) < 0.02) quieto += dt; else quieto = 0;
      res.max_quieto = std::max(res.max_quieto, quieto);
    }
    if (t >= e.t_stop && !parado_reg) { parado_reg = true; x_stop = rb.x; y_stop = rb.y; }
    if (parado_reg) res.d_parada = std::hypot(rb.x - x_stop, rb.y - y_stop);
    if (e.log && ms % 5 == 0)
      std::fprintf(e.log, "%.3f,%.4f,%.4f,%.4f,%d,%d,%d,%d,%.3f,%.3f,%d,%.4f,%.4f\n", t, rb.x, rb.y, rb.th, (int)start, (int)kill,
                   (int)arr.estado(), (int)est.modo(), izq, der, (int)nsleep, o.x, o.y);
    if (res.fuera) break;
  }
  return res;
}
}  // namespace

int main(int argc, char** argv) {
  const std::string out = argc > 1 ? argv[1] : ".";
  std::mt19937 g(42);
  std::uniform_real_distribution<double> U(0, 1);
  std::printf("{\n");
  // ---------------- 1. arranque, ruido en START, parada y reinicio
  {
    Escenario e; e.t_start = 1.0; e.t_stop = 1.6; e.dur = 2.5;
    e.log = std::fopen((out + "/fw_arranque_parada.csv").c_str(), "w");
    e.rival = {0, 0.30, 0, 0, 1, true};  // rival delante: el robot va recto hacia él y se le para antes de llegar
    Robot r; r.y = -0.25;
    Resultado a = simular(e, r);
    r.y = -0.1;
    std::fclose(e.log);
    std::printf(" \"arranque_parada\": {\"t_primer_mov_ms\": %.1f, \"d_parada_mm\": %.1f, \"v_max\": %.2f},\n",
                a.t_primer_mov * 1000, a.d_parada * 1000, a.v_max);
    int falsos1 = 0, falsos2 = 0;
    for (int s = 0; s < 200; s++) {
      Escenario e1; e1.t_start = 5; e1.dur = 5; e1.glitch_ms = 1; e1.semilla = s; falsos1 += simular(e1, r).arranques_falsos;
      Escenario e2 = e1; e2.glitch_ms = 2; falsos2 += simular(e2, r).arranques_falsos;
    }
    std::printf(" \"ruido_start\": {\"pulsos_1ms_arranques_falsos_de_200\": %d, \"pulsos_2ms_arranques_falsos_de_200\": %d},\n", falsos1, falsos2);
    Escenario e3; e3.t_start = 1.0; e3.t_reinicio = 2.0; e3.dur = 3.5;
    e3.log = std::fopen((out + "/fw_reinicio.csv").c_str(), "w");
    Resultado c = simular(e3, r);
    std::fclose(e3.log);
    std::printf(" \"reinicio_en_combate\": {\"sigue_dentro\": %s},\n", c.fuera ? "false" : "true");
  }
  // ---------------- 2. bordes: dohyo vacío, 60 s, salidas
  std::printf(" \"bordes_dohyo_vacio_60s\": [\n");
  bool primero = true;
  for (double mu : {0.6, 0.8, 1.0})
    for (double vb : {7.4, 8.4}) {
      int fuera = 0, n = 100; double quieto = 0;
      for (int s = 0; s < n; s++) {
        Escenario e; e.mu = mu; e.vbat = vb; e.dur = 61; e.semilla = s;
        Robot r; double a = U(g) * 2 * PI, rr = 0.25 * std::sqrt(U(g)); r.x = rr * std::cos(a); r.y = rr * std::sin(a); r.th = U(g) * 2 * PI;
        if (s == 3 && mu == 0.6 && vb == 8.4) e.log = std::fopen((out + "/fw_bordes.csv").c_str(), "w");
        Resultado q = simular(e, r);
        if (e.log) std::fclose(e.log);
        fuera += q.fuera; quieto = std::max(quieto, q.max_quieto);
      }
      std::printf("%s  {\"mu\": %.1f, \"vbat\": %.1f, \"salidas_de_100\": %d, \"max_quieto_s\": %.2f}", primero ? "" : ",\n", mu, vb, fuera, quieto);
      primero = false;
    }
  std::printf("\n ],\n");
  // ---------------- 3. rival quieto o en círculo: tiempo hasta el contacto y salidas
  std::printf(" \"rival\": [\n");
  primero = true;
  for (int tipo = 0; tipo < 3; tipo++)
    for (double mu : {0.6, 0.8}) {
      int fuera = 0, encontrado = 0, n = 200; std::vector<double> ts;
      for (int s = 0; s < n; s++) {
        Escenario e; e.mu = mu; e.vbat = 8.0; e.dur = 21; e.semilla = 1000 + s;
        // salida reglamentaria: cada robot en su mitad, mirando hacia donde quiera
        Robot r; r.x = (U(g) - 0.5) * 0.3; r.y = -0.10 - 0.15 * U(g); r.th = U(g) * 2 * PI;
        if (tipo == 0) e.rival = {(U(g) - 0.5) * 0.3, 0.10 + 0.15 * U(g), U(g) * 2 * PI, 0, 1, true};
        if (tipo == 1) e.rival = {0.18, 0.0, 0, 0.3, 0.18, true};   // vueltas de r = 18 cm a 0,3 m/s
        if (tipo == 2) e.rival = {0.18, 0.0, 0, 0.6, 0.18, true};   // a 0,6 m/s
        if (s == 5 && mu == 0.8) e.log = std::fopen((out + "/fw_rival_" + std::to_string(tipo) + ".csv").c_str(), "w");
        Resultado q = simular(e, r);
        if (e.log) std::fclose(e.log);
        fuera += q.fuera;
        if (q.t_contacto >= 0) { encontrado++; ts.push_back(q.t_contacto); }
      }
      std::sort(ts.begin(), ts.end());
      double med = ts.empty() ? -1 : ts[ts.size() / 2], p90 = ts.empty() ? -1 : ts[(size_t)(ts.size() * 0.9)];
      std::printf("%s  {\"rival\": \"%s\", \"mu\": %.1f, \"contacto_de_200\": %d, \"t_contacto_mediana_s\": %.2f, \"t_contacto_p90_s\": %.2f, \"salidas_de_200\": %d}",
                  primero ? "" : ",\n", tipo == 0 ? "quieto" : (tipo == 1 ? "circulo_0,3m/s" : "circulo_0,6m/s"), mu, encontrado, med, p90, fuera);
      primero = false;
    }
  std::printf("\n ],\n");
  // ---------------- 4. el rival esquiva en el último momento junto al borde
  std::printf(" \"esquiva_junto_al_borde\": [\n");
  primero = true;
  for (double mu : {0.6, 0.8, 1.0})
    for (double vb : {7.4, 8.4}) {
      int fuera = 0, n = 200;
      for (int s = 0; s < n; s++) {
        Escenario e; e.mu = mu; e.vbat = vb; e.dur = 8; e.semilla = 5000 + s; e.esquiva_m = 0.11 + 0.10 * U(g);
        double a = U(g) * 2 * PI;
        e.rival = {0.31 * std::cos(a), 0.31 * std::sin(a), a, 0, 1, true};
        Robot r; r.x = -0.10 * std::cos(a); r.y = -0.10 * std::sin(a); r.th = a - PI / 2 + (U(g) - 0.5) * 0.6;
        if (s == 2 && mu == 0.6 && vb == 8.4) e.log = std::fopen((out + "/fw_esquiva.csv").c_str(), "w");
        Resultado q = simular(e, r);
        if (e.log) std::fclose(e.log);
        fuera += q.fuera;
      }
      std::printf("%s  {\"mu\": %.1f, \"vbat\": %.1f, \"salidas_de_200\": %d}", primero ? "" : ",\n", mu, vb, fuera);
      primero = false;
    }
  std::printf("\n ]\n}\n");
}
