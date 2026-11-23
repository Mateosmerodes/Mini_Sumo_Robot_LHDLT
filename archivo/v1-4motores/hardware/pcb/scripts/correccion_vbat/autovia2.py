import pcbnew, sys, math
f=sys.argv[1]; b=pcbnew.LoadBoard(f); x0,y0,x1,y1=[float(v) for v in sys.argv[2].split(',')]; layB=sys.argv[3] if len(sys.argv)>3 else 'B'
NETN=sys.argv[4] if len(sys.argv)>4 else 'VBAT'; MAXN=int(sys.argv[5]) if len(sys.argv)>5 else 999; net=b.FindNet(NETN)
zf=[z for z in b.Zones() if z.GetNetname()==NETN and z.IsOnLayer(pcbnew.F_Cu)]
zb=[z for z in b.Zones() if z.GetNetname()==NETN and z.IsOnLayer(pcbnew.B_Cu)]
def ok(zs,L,x,y,r):
    for k in range(13):
        a=2*math.pi*k/12; rr=r if k<12 else 0
        p=pcbnew.VECTOR2I(int((x+rr*math.cos(a))*1e6),int((y+rr*math.sin(a))*1e6))
        if not any(z.HitTestFilledArea(L,p) for z in zs): return False
    return True
existing=[(t.GetPosition().x/1e6,t.GetPosition().y/1e6) for t in b.GetTracks() if t.GetClass()=='PCB_VIA']
placed=[]
y=y0
while y<=y1:
    x=x0
    while x<=x1:
        if ok(zf,pcbnew.F_Cu,x,y,0.45) and ok(zb,pcbnew.B_Cu,x,y,0.45) and all(math.hypot(x-a,y-c)>1.3 for a,c in placed+existing):
            placed.append((x,y))
            if len(placed)>=MAXN: break
        x+=0.25
    y+=0.25
for x,y in placed:
    v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(x*1e6),int(y*1e6))); v.SetDrill(400000); v.SetWidth(800000); v.SetNet(net); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v)
print('vias',len(placed),placed)
b.Save(f); b=pcbnew.LoadBoard(f); b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(f)
