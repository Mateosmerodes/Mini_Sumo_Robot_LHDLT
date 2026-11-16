# 2D finite-difference resistance of a net's copper (F.Cu+B.Cu), using KiCad's own filled zones/tracks/pads
import pcbnew, sys, numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl
pcbfile,NET,src=sys.argv[1],sys.argv[2],sys.argv[3]; sinks=sys.argv[4].split(','); oz=float(sys.argv[5]); Iper=float(sys.argv[6])
h=0.1 # mm grid
b=pcbnew.LoadBoard(pcbfile)
bb=b.GetBoardEdgesBoundingBox(); X0,Y0=bb.GetX()/1e6,bb.GetY()/1e6; nx=int(bb.GetWidth()/1e6/h)+1; ny=int(bb.GetHeight()/1e6/h)+1
xs=X0+np.arange(nx)*h; ys=Y0+np.arange(ny)*h
from matplotlib.path import Path
masks={}
def poly_mask(pts):
    p=Path(pts); x0,y0=pts.min(0); x1,y1=pts.max(0)
    i0,i1=max(0,int((x0-X0)/h)-1),min(nx,int((x1-X0)/h)+2); j0,j1=max(0,int((y0-Y0)/h)-1),min(ny,int((y1-Y0)/h)+2)
    gx,gy=np.meshgrid(xs[i0:i1],ys[j0:j1]); m=p.contains_points(np.c_[gx.ravel(),gy.ravel()]).reshape(gy.shape)
    return (j0,j1,i0,i1,m)
def add_shape(M,sps):
    for i in range(sps.OutlineCount()):
        o=sps.Outline(i); pts=np.array([(o.CPoint(k).x/1e6,o.CPoint(k).y/1e6) for k in range(o.PointCount())])
        if len(pts)<3: continue
        j0,j1,i0,i1,m=poly_mask(pts); M[j0:j1,i0:i1]|=m
        for hI in range(sps.HoleCount(i)):
            ho=sps.Hole(i,hI); hp=np.array([(ho.CPoint(k).x/1e6,ho.CPoint(k).y/1e6) for k in range(ho.PointCount())])
            j0,j1,i0,i1,m=poly_mask(hp); M[j0:j1,i0:i1]&=~m
Ls={'F':pcbnew.F_Cu,'B':pcbnew.B_Cu}
for L,lid in Ls.items():
    M=np.zeros((ny,nx),bool)
    for z in b.Zones():
        if z.GetNetname()==NET and z.IsOnLayer(lid): add_shape(M,z.GetFilledPolysList(lid))
    for t in b.GetTracks():
        if t.GetNetname()==NET and (t.IsOnLayer(lid)):
            s=pcbnew.SHAPE_POLY_SET(); t.TransformShapeToPolygon(s,lid,0,10000,pcbnew.ERROR_INSIDE); add_shape(M,s)
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetname()==NET and p.IsOnLayer(lid):
                s=pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(s,lid,0,10000,pcbnew.ERROR_INSIDE); add_shape(M,s)
    masks[L]=M
idx=-np.ones((2,ny,nx),int); n=0
for k,L in enumerate('FB'):
    c=np.argwhere(masks[L]); idx[k][masks[L]]=np.arange(n,n+len(c)); n+=len(c)
t=oz*35e-6; g=t/1.72e-8  # sheet conductance (square)
rows=[];cols=[];vals=[]
def link(a,b_,gv):
    rows.extend([a,b_,a,b_]); cols.extend([a,b_,b_,a]); vals.extend([gv,gv,-gv,-gv])
for k in range(2):
    I=idx[k]
    a=I[:,:-1];c=I[:,1:]; m=(a>=0)&(c>=0)
    for x,y in zip(a[m],c[m]): link(x,y,g)
    a=I[:-1,:];c=I[1:,:]; m=(a>=0)&(c>=0)
    for x,y in zip(a[m],c[m]): link(x,y,g)
# vias and THT pads: connect layers (ideal) in their annulus area
def cells(obj,lid):
    s=pcbnew.SHAPE_POLY_SET(); obj.TransformShapeToPolygon(s,lid,0,10000,pcbnew.ERROR_INSIDE); M=np.zeros((ny,nx),bool); add_shape(M,s); return M
for t_ in b.GetTracks():
    if t_.GetClass()=='PCB_VIA' and t_.GetNetname()==NET:
        M=cells(t_,pcbnew.F_Cu); fi=idx[0][M]; bi=idx[1][M]; 
        for x,y in zip(fi,bi):
            if x>=0 and y>=0: link(x,y,1e3)
def padcells(ref):
    r,num=ref.split('.'); f=b.FindFootprintByReference(r)
    for p in f.Pads():
        if p.GetNumber()==num:
            out=[]
            for k,lid in enumerate((pcbnew.F_Cu,pcbnew.B_Cu)):
                if p.IsOnLayer(lid): M=cells(p,lid); out+=list(idx[k][M][idx[k][M]>=0])
            return out
G=sp.coo_matrix((vals,(rows,cols)),shape=(n,n)).tocsr()
srcc=padcells(src); Ib=np.zeros(n)
# tie source cells to ground node (Dirichlet 0): add big conductance to ground
G=G+sp.diags(np.isin(np.arange(n),srcc)*1e3)
for s in sinks:
    cc=padcells(s); Ib[cc]-=Iper/len(cc)
V=spl.spsolve(G.tocsc(),Ib)
for s in sinks: print(s,'drop mV',round(-V[padcells(s)].mean()*1000,1))
# max current density
J=np.zeros((2,ny,nx))
for k in range(2):
    Vk=np.full((ny,nx),np.nan); m=idx[k]>=0; Vk[m]=V[idx[k][m]]
    gx=np.abs(np.diff(Vk,axis=1))/ (h*1e-3) ; gy=np.abs(np.diff(Vk,axis=0))/(h*1e-3)
    jx=np.nan_to_num(gx)/1.72e-8/1e6; jy=np.nan_to_num(gy)/1.72e-8/1e6  # A/mm2
    Jk=np.zeros((ny,nx)); Jk[:,:-1]=np.maximum(Jk[:,:-1],jx); Jk[:-1,:]=np.maximum(Jk[:-1,:],jy); J[k]=Jk
P=sum(np.nansum(J[k]**2)*1.72e-8*1e12*(h*1e-3)**2*t for k in range(2))
print('total loss W ~',round(P,3))
for k,L in enumerate('FB'):
    flat=np.argsort(J[k].ravel())[::-1][:400]
    pts=[(round(X0+(f%nx)*h,1),round(Y0+(f//nx)*h,1),round(J[k].ravel()[f])) for f in flat]
    # cluster
    seen=[]
    for p in pts:
        if all(abs(p[0]-q[0])>1.5 or abs(p[1]-q[1])>1.5 for q in seen): seen.append(p)
    print(L,'hotspots (x,y,A/mm2):',seen[:8])
np.save(sys.argv[7] if len(sys.argv)>7 else '/tmp/claude-0/rev/J.npy',J)
