import pcbnew, sys
f=sys.argv[1]; b=pcbnew.LoadBoard(f)
band=eval(sys.argv[2])  # polygon pts for B.Cu VBAT zone
net=b.FindNet('VBAT')
# remove GND stitch inside band
rm=[]
for t in b.GetTracks():
    if t.GetNetname()=='GND':
        s,e=t.GetStart(),t.GetEnd()
        for x,y in eval(sys.argv[3]):
            if (abs(s.x/1e6-x)<0.05 and abs(s.y/1e6-y)<0.05) or (abs(e.x/1e6-x)<0.05 and abs(e.y/1e6-y)<0.05): rm.append(t);break
seen=[]
for t in rm:
    if not any(t is s for s in seen): seen.append(t); b.Remove(t)
z=pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(net); z.SetZoneName('VBAT_puente_B'); z.SetAssignedPriority(3)
z.SetLocalClearance(200000); z.SetMinThickness(200000); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
o=z.Outline(); o.NewOutline()
for x,y in band: o.Append(int(x*1e6),int(y*1e6))
b.Add(z)
for x,y in eval(sys.argv[4]):
    v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(int(x*1e6),int(y*1e6))); v.SetDrill(400000); v.SetWidth(800000); v.SetNet(net); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v)
b.Save(f); b=pcbnew.LoadBoard(f); b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(f)
