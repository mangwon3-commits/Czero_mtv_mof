"""수소결합 개수 — g(2.82) 는 대리 지표이고 이것이 주장 자체입니다.
기준: Luzar–Chandler 기하  R(O–O) < 3.5 Å  그리고  각 H–O···O < 30°
⚠️ 등록된 판정 기준이 아닙니다. **서술용**입니다."""
import numpy as np, sys, os
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
# 09-06: 고정 파일명(seed.txt / main_now.txt / ctl_now.txt)을 실제 경로로 바꿉니다.
# 그 판은 실행 중 스냅샷 사본을 전제해 **완주 뒤에는 못 돌았습니다.**
R = 'hvap/Restart/System_0/restart_Box_1.1.1_298.150000_100000'
JOBS = [('씨앗 (공통 출발)',        'tb1_seed/restart_compressed'),
        ('본 실행 (현행 힘장, 완주)', f'tb1_runs_n1000/{R}'),
        ('대조 (수정 힘장, 완주)',   f'tb1_runs_ffctl/{R}')]
if len(sys.argv) > 1:
    JOBS = [(a, a) for a in sys.argv[1:]]
print(f"  {'배치':<28} {'분자당 수소결합':>14}   (액체물 3.5~3.6)")
for lab, p in JOBS:
    if not os.path.exists(p):
        print(f'  {lab:<28} {"— 파일 없음":>14}   {p}');  continue
    v, n, L = hb(p)
    print(f'  {lab:<28} {v:>14.2f}   (분자 {n}, L {L:.3f})')
