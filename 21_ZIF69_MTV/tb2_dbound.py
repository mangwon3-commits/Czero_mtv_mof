"""D 의 부호와 크기를 **골격 기하에서 직접** 잰다 (RASPA 없이).

[무엇을 답하나]
    `D = K_H(현행)/K_H(수정)` 의 **부호**를, 논증이 아니라 계산으로.
    데스크탑은 *"액체에서 Hw 항이 반발(+18.06)이니 D<1"* 로, 저는
    *"Jensen 분산항이 D 를 올린다"* 로 다퉜는데, **둘 다 골격 안을 안 봤습니다.**

[한계 — 이건 (다)를 대신하지 않습니다]
    가중 w 에 **Ow–골격 LJ 만** 씁니다. 진짜 Widom 가중은 **정전기를 포함**하고,
    전하 골격 안의 물에서는 정전기가 지배적입니다. 그래서
        **부호와 자릿수**는 믿을 만하고,
        **값 자체는 측정이 아닙니다.**
    RASPA (다) 대조가 답입니다.

[상한]

    D = <exp(-b dU)>_w  <=  exp(-b * min dU)     (가중과 무관, Jensen 불필요)

dU = 삽입 물의 **Hw–골격 LJ 합** (현행 힘장에만 있는 항).
min dU 를 '삽입 가능한' 기하로 한정해 표집한다.
"""
import numpy as np, sys, re
from ase.io import read
from scipy.spatial import cKDTree

CIF = sys.argv[1]; NSAMP = int(sys.argv[2]) if len(sys.argv)>2 else 200000
RC = 12.0; RT = 0.0083144626*298.15
FF='/home/skyjun/RASPA/simulations/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def'
ent=[]
for ln in open(FF,encoding='utf-8'):
    s=ln.strip()
    if s.startswith('# general mixing rule'): break
    if s.startswith('#') or not s: continue
    t=s.split()
    if len(t)>=3 and t[1]=='lennard-jones': ent.append((t[0],float(t[2]),float(t[3])))
    elif len(t)>=2 and t[1]=='none': ent.append((t[0],0.0,0.0))
def par(name):
    hit=(0.0,0.0)
    for n,e,s in ent:
        if name.startswith(n.rstrip('_')): hit=(e,s)
    return hit
at=read(CIF)
labels=[]
for ln in open(CIF,encoding='utf-8'):
    t=ln.split()
    if len(t)==8 and t[2]=='1': labels.append(t[1])
assert len(labels)==len(at), (len(labels),len(at))
EPS_H, SIG_H = 22.1417, 2.57113
EPS_O, SIG_O = 89.633, 3.097
eps=np.array([par(l)[0] for l in labels]); sig=np.array([par(l)[1] for l in labels])
# 3x3x3 이미지
cell=np.array(at.get_cell()); P=at.get_positions()
imgs=[]; E=[]; S=[]
for i in (-1,0,1):
    for j in (-1,0,1):
        for k in (-1,0,1):
            imgs.append(P + i*cell[0] + j*cell[1] + k*cell[2]); E.append(eps); S.append(sig)
F=np.vstack(imgs); Ef=np.concatenate(E); Sf=np.concatenate(S)
tree=cKDTree(F)
def lj(eps,sig,r2):
    s6=(sig*sig/r2)**3
    sc=(sig/RC)**6
    return 4*eps*(s6*s6-s6) - 4*eps*(sc*sc-sc)
# TIP5P 기하 (water.def)
SITE=np.array([[0,0,0],[0.75695,0,0.58588],[-0.75695,0,0.58588]])   # Ow, Hw, Hw
rng=np.random.default_rng(0)
dUs=[]; Uos=[]
for _ in range(NSAMP):
    p = rng.random(3) @ cell
    q = rng.normal(size=4); q/=np.linalg.norm(q)
    w,x,y,z=q
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    S3=(R@SITE.T).T + p
    idx=tree.query_ball_point(S3[0], RC+1.2)
    if not idx: continue
    idx=np.array(idx); d=F[idx]-S3[0]; r2=(d*d).sum(1); m=r2<RC*RC
    if not m.any(): continue
    Uo=lj(np.sqrt(EPS_O*Ef[idx][m]),(SIG_O+Sf[idx][m])/2, r2[m]).sum()
    dU=0.0
    for h in (1,2):
        d=F[idx]-S3[h]; r2h=(d*d).sum(1); mh=r2h<RC*RC
        if mh.any():
            dU+=lj(np.sqrt(EPS_H*Ef[idx][mh]),(SIG_H+Sf[idx][mh])/2, r2h[mh]).sum()
    Uos.append(Uo); dUs.append(dU)
dUs=np.array(dUs)*0.0083144626; Uos=np.array(Uos)*0.0083144626
ok = Uos < 0    # 골격이 Ow 를 끌어당기는 자리 = 삽입 가능
print(f'  구조 {CIF.split("/")[-1]}   표본 {len(dUs):,}   그중 Ow-LJ<0 인 자리 **{ok.sum():,}**')
w=np.exp(-Uos[ok]/RT); w/=w.sum()
d=dUs[ok]
print(f'  ΔU (Hw–골격 LJ) [kJ/mol]  최소 **{d.min():.3f}**  중앙 {np.median(d):.3f}  최대 {d.max():.1f}')
print(f'  Widom 가중 평균 <ΔU>_w = **{(w*d).sum():.3f}**   σ_w = **{np.sqrt((w*(d-(w*d).sum())**2).sum()):.3f}**')
print(f'  가중 D = <exp(-ΔU/RT)>_w = **{(w*np.exp(-d/RT)).sum():.3f}**')
print(f'  상한   D <= exp(-ΔU_min/RT) = **{np.exp(-d.min()/RT):.2f}**')
