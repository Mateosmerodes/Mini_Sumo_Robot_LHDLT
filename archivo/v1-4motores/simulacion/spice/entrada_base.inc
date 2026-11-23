* entrada_base.inc — batería, XT30, Q1, F1, condensadores de VBAT, cobre y los 4 drivers.
* Parámetros que fija cada escenario: VCELL (V batería), RINT, LW (inductancia de los cables),
* DUTY, y las fuentes de control F1..F4 / R1..R4 (definidas fuera).
.include modelos.lib
* Batería 2S (fuente + resistencia interna) y cables
Vbat bat_p 0 {VCELL}
Rint bat_p b1 {RINT}
Lw b1 b2 {LW}
* enchufe: el XT30 se conecta en t = TPLUG (interruptor que cierra en 1 µs)
Splug b2 j1p plug 0 SWPLUG
.model SWPLUG sw(vt=0.5 vh=0 ron=2.4m roff=1e9)
Vplug plug 0 PULSE(0 1 {TPLUG} 1u 1u 10 20)
* Q1 (protección de polaridad, D = batería, S = carga, G a GND por R1)
M1 j1p q1g vrev AOD4185
R1 q1g 0 10k
* F1: Littelfuse 15 A, ~5 mΩ en frío (supuesto)
Rf1 vrev vbat 5m
* condensadores de VBAT con su capacidad real a 8 V (el cerámico pierde capacidad con la tensión)
* C1, C2: 22 µF 25 V 1206 -> 13 µF; C4, C5: 10 µF 25 V 1206 -> 7 µF; C6: 100 nF
C1 vbat c1e 13u
Rc1 c1e 0 5m
C2 vbat c2e 13u
Rc2 c2e 0 5m
C45 vbat c45e 14u
Rc45 c45e 0 3m
C6 vbat 0 100n
* resto de la placa (buck + ESP32 + sensores): potencia constante 3,6 W
Belec vbat 0 I = V(vbat)>4.5 ? 3.6/V(vbat) : V(vbat)*0.18
* cobre de VBAT y GND (ajustado a la solución de diferencias finitas de cobre.py, 4 x 2,44 A)
Rvc vbat vbus 3.0m
Rgc 0 gbus 0.8m
Rv5 vbus vm5 3.1m
Rv6 vbus vm6 7.0m
Rv7 vbus vm7 8.8m
Rv8 vbus vm8 8.7m
Rg5 gbus g5 0.1m
Rg6 gbus g6 11.3m
Rg7 gbus g7 13.6m
Rg8 gbus g8 13.2m
* condensadores de cada driver: 10 µF 25 V 1206 (-> 7 µF) + 100 nF
Cm5 vm5 g5 7u
Cm6 vm6 g6 7u
Cm7 vm7 g7 7u
Cm8 vm8 g8 7u
Cn5 vm5 g5 100n
Cn6 vm6 g6 100n
Cn7 vm7 g7 100n
Cn8 vm8 g8 100n
X5 vm5 g5 f1 r1 DRVMOT params: LOCK={LOCK}
X6 vm6 g6 f2 r2 DRVMOT params: LOCK={LOCK}
X7 vm7 g7 f3 r3 DRVMOT params: LOCK={LOCK}
X8 vm8 g8 f4 r4 DRVMOT params: LOCK={LOCK}
