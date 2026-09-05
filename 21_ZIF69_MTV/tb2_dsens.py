"""D 가 가중에 얼마나 민감한가 — 빠진 정전기 가중의 영향 범위를 본다."""
import numpy as np, sys
from ase.io import read
from scipy.spatial import cKDTree
CIF=sys.argv[1]; NS=int(sys.argv[2]); RC=12.0; RT=0.0083144626*298.15
FF='/home/skyjun/RASPA/simulations/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def'
ent=[]
for ln in open(FF,encoding='utf-8'):
    s=ln.strip()
    if s.startswith('# general mixing rule'): break
    if s.startswith('#') or not s: continue
    t=s.split()
    if len(t)>=3 and t[1]=='lennard-jones': ent.append((t[0],float(t[2]),float(t[3])))
    elif len(t)>=2 and t[1]=='none': ent.append((t[0],0.0,0.0))
def par(n):
    h=(0.0,0.0)
    for a,e,s in ent:
        if n.startswith(a.rstrip('_')): h=(e,s)
    return h
at=read(CIF); labels=[]
for ln in open(CIF,encoding='utf-8'):
    t=ln.split()
    if len(t)==8 and t[2]=='1': labels.append(t[1])
eps=np.array([par(l)[0] for l in labels]); sig=np.array([par(l)[1] for l in labels])
cell=np.array(at.get_cell()); P=at.get_positions()
F=np.vstack([P+i*cell[0]+j*cell[1]+k*cell[2] for i in(-1,0,1) for j in(-1,0,1) for k in(-1,0,1)])
Ef=np.tile(eps,27); Sf=np.tile(sig,27); tree=cKDTree(F)
EH,SH=22.1417,2.57113; EO,SO=89.633,3.097
def lj(e,s,r2):
    s6=(s*s/r2)**3; sc=(s/RC)**6
    return 4*e*(s6*s6-s6)-4*e*(sc*sc-sc)
SITE=np.array([[0,0,0],[0.75695,0,0.58588],[-0.75695,0,0.58588]])
rng=np.random.default_rng(1); dUs=[];Uos=[]
for _ in range(NS):
    p=rng.random(3)@cell; q=rng.normal(size=4); q/=np.linalg.norm(q); w,x,y,z=q
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    S3=(R@SITE.T).T+p
    idx=tree.query_ball_point(S3[0],RC+1.2)
    if not idx: continue
    idx=np.array(idx); d=F[idx]-S3[0]; r2=(d*d).sum(1); m=r2<RC*RC
    if not m.any(): continue
    Uo=lj(np.sqrt(EO*Ef[idx][m]),(SO+Sf[idx][m])/2,r2[m]).sum()
    dU=0.0
    for h in (1,2):
        d=F[idx]-S3[h]; rh=(d*d).sum(1); mh=rh<RC*RC
        if mh.any(): dU+=lj(np.sqrt(EH*Ef[idx][mh]),(SH+Sf[idx][mh])/2,rh[mh]).sum()
    Uos.append(Uo); dUs.append(dU)
dU=np.array(dUs)*0.0083144626; Uo=np.array(Uos)*0.0083144626
ok=Uo<0; d=dU[ok]; u=Uo[ok]
print(f'  {CIF.split("/")[-1]}  표본 {len(dU):,}  삽입가능 {ok.sum():,}')
print(f"  {'가중':<28} {'유효표본':>9} {'<ΔU>_w':>9} {'**D**':>9}")
def rep(lab,w):
    w=w/w.sum(); neff=1/ (w**2).sum()
    print(f'  {lab:<28} {neff:>9.0f} {(w*d).sum():>9.3f} {(w*np.exp(-d/RT)).sum():>9.2f}')
rep('균등 (정전기 무시 극단)', np.ones_like(u))
rep('exp(-U_LJ/RT)  [현행 추정]', np.exp(-u/RT))
rep('exp(-2U_LJ/RT) [더 날카롭게]', np.exp(-2*u/RT))
rep('exp(-U_LJ/2RT) [더 무디게]', np.exp(-u/(2*RT)))
