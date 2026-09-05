"""수소결합 개수 — g(2.82) 는 대리 지표이고 이것이 주장 자체입니다.
기준: Luzar–Chandler 기하  R(O–O) < 3.5 Å  그리고  각 H–O···O < 30°
⚠️ 등록된 판정 기준이 아닙니다. **서술용**입니다."""
import numpy as np, sys
def load(p):
    L=None; pos=[]
    for ln in open(p,errors='replace'):
        if ln.startswith('cell-lengths:'): L=float(ln.split()[1])
        elif ln.startswith('Adsorbate-atom-position:'):
            t=ln.split(); pos.append((int(t[1]),int(t[2]),float(t[3]),float(t[4]),float(t[5])))
    pos.sort(key=lambda t:(t[0],t[1])); n=max(q[0] for q in pos)+1
    X=np.array([[q[2],q[3],q[4]] for q in pos]).reshape(n,5,3)
    return L, X, n
def hb(path):
    L,X,n = load(path)
    O=X[:,0,:]; H=X[:,1:3,:]
    cnt=0
    for i in range(n):
        d=O-O[i]; d-=L*np.round(d/L); r2=(d*d).sum(1)
        cand=np.where((r2<3.5**2)&(r2>1e-6))[0]
        if len(cand)==0: continue
        for j in cand:
            v=O[j]-O[i]; v-=L*np.round(v/L); rv=np.linalg.norm(v)
            for h in range(2):                     # i 가 주개
                u=H[i,h]-O[i]; u-=L*np.round(u/L)
                ang=np.degrees(np.arccos(np.clip(u@v/(np.linalg.norm(u)*rv),-1,1)))
                if ang<30.0: cnt+=1
    return cnt/n, n, L
print(f"  {'배치':<28} {'분자당 수소결합':>14}   (액체물 3.5~3.6)")
for lab,p in (('씨앗 (공통 출발)','seed.txt'),
              ('본 실행 현재 (현행 힘장)','main_now.txt'),
              ('대조 현재 (수정 힘장)','ctl_now.txt')):
    v,n,L = hb(p)
    print(f'  {lab:<28} {v:>14.2f}   (분자 {n}, L {L:.3f})')
