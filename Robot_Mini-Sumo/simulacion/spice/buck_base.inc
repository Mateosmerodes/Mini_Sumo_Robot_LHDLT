* buck_base.inc — U2 + L1 + C8/C9/C10 + D1 + LDO de la DevKit + carga del raíl de 3,3 V
* Parámetros: TOFF (t_OFF mínimo). Fuentes externas: VBAT (nodo vbat) y la carga Iload (nodo v33).
.include buck_tps563201.lib
R5 vbat en 100k
R6 en 0 51k
XU2 vbat sw fb en 0 TPS563201 params: TOFFMIN={TOFF}
* L1: SRN4018-3R3M, 3,3 µH, DCR ~40 mΩ (supuesto)
L1 sw l1b 3.3u
Rl1 l1b v5 40m
R7 v5 fb 59k
R8 fb 0 10k
* C8, C9, C10: 22 µF 10 V 1206 -> ~12 µF a 5,3 V
C8 v5 c8e 36u
Rc8 c8e 0 1.5m
* D1: SS34 (V_F ≈ 0,45 V a 0,5 A)
D1 v5 v5e SS34
.model SS34 D(Is=5u N=1.1 Rs=60m Cjo=300p)
* C11 10 µF 10 V 0805 (-> 6 µF) + condensadores de la propia DevKit (supuesto 10 µF)
C11 v5e 0 16u
* LDO de la DevKit: modelo de un AMS1117 (caída 1,0 V + 0,4 Ω·I), el caso más desfavorable de los clones
Bldo n3x 0 V = min(3.3, max(0, V(v5e) - 1.0 - 0.4*I(Vldo)))
Rldo n3x n3y 5m
Vldo n3y v33 0
Bldin v5e 0 I = V(v5e)>0.3 ? I(Vldo) + 5m : 0
* C13 22 µF 10 V (-> 18 µF a 3,3 V) + C14 + DevKit (supuesto 10 µF)
C13 v33 0 28u
