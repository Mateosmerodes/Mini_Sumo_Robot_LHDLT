import pcbnew, sys
f=sys.argv[1]; b=pcbnew.LoadBoard(f)
mm=lambda v:int(round(v*1e6)); V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y))
def r(p): return (round(p.x/1e6,2),round(p.y/1e6,2))
def find(net,a,c=None,via=False):
    out=[]
    for t in b.GetTracks():
        if t.GetNetname()!=net: continue
        if via:
            if t.GetClass()=='PCB_VIA' and r(t.GetPosition())==a: out.append(t)
        elif t.GetClass()!='PCB_VIA' and {r(t.GetStart()),r(t.GetEnd())}=={a,c}: out.append(t)
    assert len(out)==1,(net,a,c,len(out)); return out[0]
def track(net,a,c,w,L):
    t=pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(mm(w)); t.SetLayer(L); t.SetNet(b.FindNet(net)); b.Add(t); return t
def via(net,a,d=0.6,dr=0.3):
    v=pcbnew.PCB_VIA(b); v.SetPosition(V(*a)); v.SetWidth(mm(d)); v.SetDrill(mm(dr)); v.SetNet(b.FindNet(net)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v)
# 1) DRV_nSLEEP: bajar a B.Cu antes del canal bajo Q1
rm=[find('DRV_nSLEEP',(142.58,95.89),(140.18,93.49))]+[find('DRV_nSLEEP',a,c) for a,c in [((149.25,95.89),(142.58,95.89)),((149.82,95.32),(149.25,95.89))]]+[find('DRV_nSLEEP',(149.82,95.32),via=True)]
rm+=[find('Q1_G',a,c) for a,c in [((149.77,97.19),(145.17,97.19)),((145.17,97.19),(143.72,98.64)),((150.18,97.6),(149.77,97.19))]]
rm+=[find('GND',(151.85,97.6),(151.85,98.65)),find('GND',(151.85,98.65),via=True)]
for t in rm: b.Remove(t)
track('DRV_nSLEEP',(140.18,93.49),(141.3,94.61),0.2,pcbnew.F_Cu)
via('DRV_nSLEEP',(141.3,94.61))
track('DRV_nSLEEP',(141.3,94.61),(149.82,95.32),0.2,pcbnew.B_Cu)
# 2) R1 junto a la puerta de Q1; Q1_G corta
R1=b.FindFootprintByReference('R1'); R1.SetOrientationDegrees(180); R1.SetPosition(V(142.075,100.9))
pads={p.GetNumber():p for p in R1.Pads()}; print('R1 pads',{k:r(p.GetPosition()) for k,p in pads.items()})
p1=r(pads['1'].GetPosition()); p2=r(pads['2'].GetPosition())
track('Q1_G',(143.72,98.64),(143.72,99.9),0.3,pcbnew.F_Cu); track('Q1_G',(143.72,99.9),p1,0.3,pcbnew.F_Cu)
track('GND',p2,(p2[0],101.7),0.3,pcbnew.F_Cu); via('GND',(p2[0],101.7))
b.Save(f)
