// sumo_lhdt_v2.ino — firmware básico del robot mini-sumo v2 (LHDT · Los Hombres de las Tabernas)
//
// Placa: ESP32-S3-DevKitC-1 + 2 × TB6612FNG + 2 × VL53L0X + 2 × QRE1113 + módulo de arranque ST4RT.
// Compilar con Arduino IDE o arduino-cli, core "esp32" 3.x y la librería "VL53L0X" de Pololu.
// Placa en el IDE: "ESP32S3 Dev Module".
//
// Estrategia sencilla:
//   1. Espera la orden de inicio del módulo de arranque (pin S a 1).
//   2. Si un sensor de suelo ve blanco: marcha atrás y giro hacia dentro.
//   3. Si los dos sensores de distancia ven al rival: a por él a fondo.
//      Si solo lo ve uno: gira hacia ese lado.
//   4. Si no ve nada: gira sobre sí mismo buscando.
//   5. Con la orden de parada (S a 0 o K a 0): frena y apaga los motores hasta reiniciar.
//
// ⚠️ Los valores marcados "A AJUSTAR" son hipótesis: no se ha probado en un robot real.
#include <Wire.h>
#include <VL53L0X.h>

#include "arranque.h"
#include "pines.h"

// ------------------------------------------------------------------ ajustes
const uint32_t PWM_HZ = 20000;        // fuera del rango audible
const uint8_t PWM_BITS = 10;          // 0..1023
const int PWM_MAX = (1 << PWM_BITS) - 1;
// Signo de cada motor (1 o -1). A AJUSTAR con las ruedas en el aire: con avanzar() las dos deben ir hacia delante.
const int SIGNO_IZQ = 1, SIGNO_DER = -1;
// Los motores son de 6 V y la batería da hasta 8,4 V: se limita la potencia para no pasarse.
const float POT_ATAQUE = 0.85f;       // A AJUSTAR
const float POT_GIRO = 0.45f;         // A AJUSTAR
const float POT_BUSQUEDA = 0.40f;     // A AJUSTAR
const uint16_t TOF_MAX_MM = 600;      // más lejos es fuera del dohyo (77 cm de diámetro)
const uint32_t T_ATRAS_MS = 200;      // A AJUSTAR
const uint32_t T_GIRO_MS = 250;       // A AJUSTAR
const uint32_t T_FRENO_MS = 300;
const float FACTOR_BLANCO = 0.55f;    // umbral = 0,55 × lectura sobre negro al encender. A AJUSTAR
const float DIVISOR_VBAT = 133.0f / 33.0f;

VL53L0X tof_izq, tof_der;
Arranque arranque(2);
uint16_t umbral_izq_mv = 1500, umbral_der_mv = 1500;

// ------------------------------------------------------------------ motores
void motor(int pin_pwm, int pin_in1, int pin_in2, float v) {
  v = constrain(v, -1.0f, 1.0f);
  digitalWrite(pin_in1, v > 0 ? HIGH : LOW);
  digitalWrite(pin_in2, v < 0 ? HIGH : LOW);
  ledcWrite(pin_pwm, (uint32_t)(fabsf(v) * PWM_MAX));
}

void mover(float izq, float der) {
  motor(pin::MI_PWM, pin::MI_IN1, pin::MI_IN2, SIGNO_IZQ * izq);
  motor(pin::MD_PWM, pin::MD_IN1, pin::MD_IN2, SIGNO_DER * der);
}

void frenar() {  // TB6612: IN1 = IN2 = 1 con PWM a 1 -> cortocircuito del motor = freno
  digitalWrite(pin::MI_IN1, HIGH); digitalWrite(pin::MI_IN2, HIGH);
  digitalWrite(pin::MD_IN1, HIGH); digitalWrite(pin::MD_IN2, HIGH);
  ledcWrite(pin::MI_PWM, PWM_MAX);
  ledcWrite(pin::MD_PWM, PWM_MAX);
}

// ------------------------------------------------------------------ sensores
uint16_t leer_mv(int pin) { return analogReadMilliVolts(pin); }

// QRE1113: el blanco refleja más luz -> tensión MÁS BAJA que sobre negro
bool blanco_izq() { return leer_mv(pin::LINEA_IZQ) < umbral_izq_mv; }
bool blanco_der() { return leer_mv(pin::LINEA_DER) < umbral_der_mv; }

float vbat() { return leer_mv(pin::VBAT_SENSE) * DIVISOR_VBAT / 1000.0f; }

bool iniciar_tof(VL53L0X &s, int xshut, uint8_t direccion) {
  digitalWrite(xshut, HIGH);
  delay(10);
  s.setTimeout(50);
  if (!s.init()) return false;
  s.setAddress(direccion);  // los dos salen de fábrica con 0x29: se cambia uno
  s.setMeasurementTimingBudget(20000);
  s.startContinuous();
  return true;
}

uint16_t distancia(VL53L0X &s) {
  uint16_t d = s.readRangeContinuousMillimeters();
  return (s.timeoutOccurred() || d > TOF_MAX_MM) ? 0 : d;  // 0 = no ve nada
}

void calibrar_suelo() {  // el robot se enciende sobre el negro del dohyo
  uint32_t si = 0, sd = 0;
  for (int i = 0; i < 32; i++) { si += leer_mv(pin::LINEA_IZQ); sd += leer_mv(pin::LINEA_DER); delay(5); }
  umbral_izq_mv = FACTOR_BLANCO * si / 32;
  umbral_der_mv = FACTOR_BLANCO * sd / 32;
}

// ------------------------------------------------------------------ arranque
void setup() {
  Serial.begin(115200);
  pinMode(pin::MOT_STBY, OUTPUT);
  digitalWrite(pin::MOT_STBY, LOW);
  const int salidas[] = {pin::MI_IN1, pin::MI_IN2, pin::MD_IN1, pin::MD_IN2};
  for (int p : salidas) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  ledcAttach(pin::MI_PWM, PWM_HZ, PWM_BITS);
  ledcAttach(pin::MD_PWM, PWM_HZ, PWM_BITS);
  pinMode(pin::ST_START, INPUT);
  pinMode(pin::ST_KILL, INPUT);
  analogSetAttenuation(ADC_11db);

  pinMode(pin::XSHUT_IZQ, OUTPUT); digitalWrite(pin::XSHUT_IZQ, LOW);
  pinMode(pin::XSHUT_DER, OUTPUT); digitalWrite(pin::XSHUT_DER, LOW);
  Wire.begin(pin::I2C_SDA, pin::I2C_SCL, 400000);
  delay(10);
  bool ok_i = iniciar_tof(tof_izq, pin::XSHUT_IZQ, 0x30);
  bool ok_d = iniciar_tof(tof_der, pin::XSHUT_DER, 0x31);
  Serial.printf("ToF izq %s, der %s\n", ok_i ? "OK" : "FALLO", ok_d ? "OK" : "FALLO");

  calibrar_suelo();
  Serial.printf("Umbral suelo izq %u mV, der %u mV. Bateria %.2f V\n", umbral_izq_mv, umbral_der_mv, vbat());
}

// ------------------------------------------------------------------ bucle
enum class Maniobra { NINGUNA, ATRAS, GIRO };
Maniobra maniobra = Maniobra::NINGUNA;
uint32_t t_maniobra = 0;
int giro_signo = 1;  // 1 = girar a la derecha

void loop() {
  uint32_t ahora = millis();
  // El módulo: S = 1 combate. K = 0 parar ya (si K no está conectado, el pull-down lo deja a 0;
  // por eso K solo se tiene en cuenta una vez empezado el combate).
  bool start = digitalRead(pin::ST_START);
  arranque.actualizar(start, ahora);
  EstadoArranque e = arranque.estado();
  if (e == EstadoArranque::COMBATE && !digitalRead(pin::ST_KILL) && ahora - arranque.t_cambio_ms() > 50) {
    // KILL a 0 en pleno combate: se trata como parada (sin confirmar si el ST4RT usa K así)
    e = EstadoArranque::PARADO;
  }

  if (e != EstadoArranque::COMBATE) {
    static uint32_t t_parada = 0;
    if (e == EstadoArranque::PARADO) {
      if (!t_parada) t_parada = ahora;
      if (ahora - t_parada < T_FRENO_MS) { digitalWrite(pin::MOT_STBY, HIGH); frenar(); return; }
    }
    mover(0, 0);
    digitalWrite(pin::MOT_STBY, LOW);
    return;
  }
  digitalWrite(pin::MOT_STBY, HIGH);

  // 1. Borde: tiene prioridad sobre todo
  bool bi = blanco_izq(), bd = blanco_der();
  if (bi || bd) {
    maniobra = Maniobra::ATRAS;
    t_maniobra = ahora;
    giro_signo = bi ? 1 : -1;  // blanco a la izquierda -> girar a la derecha
  }
  if (maniobra == Maniobra::ATRAS) {
    if (ahora - t_maniobra < T_ATRAS_MS) { mover(-POT_ATAQUE, -POT_ATAQUE); return; }
    maniobra = Maniobra::GIRO;
    t_maniobra = ahora;
  }
  if (maniobra == Maniobra::GIRO) {
    if (ahora - t_maniobra < T_GIRO_MS) { mover(giro_signo * POT_GIRO, -giro_signo * POT_GIRO); return; }
    maniobra = Maniobra::NINGUNA;
  }

  // 2. Rival
  uint16_t di = distancia(tof_izq), dd = distancia(tof_der);
  if (di && dd) {
    mover(POT_ATAQUE, POT_ATAQUE);
  } else if (di) {
    mover(POT_GIRO * 0.3f, POT_GIRO);  // está a la izquierda
  } else if (dd) {
    mover(POT_GIRO, POT_GIRO * 0.3f);  // está a la derecha
  } else {
    // 3. Búsqueda: girar sobre sí mismo
    mover(POT_BUSQUEDA, -POT_BUSQUEDA);
  }
}
