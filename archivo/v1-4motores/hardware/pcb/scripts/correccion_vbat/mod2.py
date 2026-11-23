import pcbnew,sys
f=sys.argv[1]; b=pcbnew.LoadBoard(f)
for d in b.GetDrawings():
    if d.GetClass()=='PCB_TEXT':
        if d.GetText()=='BANCO': d.SetText('JP1')
        if d.GetText().startswith('Robot Mini-Sumo v1.2'): d.SetText('Mini-Sumo v1.2 · 2026')
b.Save(f)
