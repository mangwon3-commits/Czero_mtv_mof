import numpy as np
R=0.0083144626; KC=1389.3546/R   # K*A/e^2  (1389.35 kJ A/mol/e^2)
# water.def 그대로
site=[('Ow',0.0,[0,0,0]),
      ('Hw',+0.241,[ 0.75695,0, 0.58588]),
      ('Hw',+0.241,[-0.75695,0, 0.58588]),
      ('Lw',-0.241,[0, 0.57154,-0.40415]),
      ('Lw',-0.241,[0,-0.57154,-0.40415])]
P=np.array([s[2] for s in site]); Q=np.array([s[1] for s in site]); T=[s[0] for s in site]
def rot(a,b):  # a 를 b 로 보내는 회전
    a=a/np.linalg.norm(a); b=b/np.linalg.norm(b); v=np.cross(a,b); c=a@b
    if np.linalg.norm(v)<1e-12: return np.eye(3) if c>0 else -np.eye(3)
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+K+K@K/(1+c)
z=np.array([0,0,1.0])
Rd=rot(P[1],z)            # 주개: H1 을 +z 로
Ra=rot(P[3],-z)           # 받개: L1 을 -z 로
PAR={('Ow','Ow'):(89.633,3.097),('Ow','Hw'):(44.54915,2.83406),('Hw','Hw'):(22.14170,2.57113)}
def lj(t1,t2,r,useH):
    k=PAR.get((t1,t2)) or PAR.get((t2,t1))
    if k is None: return 0.0
    if not useH and ('Hw' in (t1,t2)): return 0.0
    e,s=k; s6=(s/r)**6; return 4*e*(s6*s6-s6)
print(f"{'O-O [Å]':>8} {'LJ(H 있음)':>12} {'LJ(H 없음)':>12} {'쿨롱':>10} {'합(있음)':>10} {'합(없음)':>10}   [kJ/mol]")
best=(9e9,None); bestN=(9e9,None)
for OO in np.arange(2.40,4.01,0.01):
    A=(Rd@P.T).T; B=(Ra@P.T).T+np.array([0,0,OO])
    lH=lC=lN=0.0
    for i in range(5):
        for j in range(5):
            r=np.linalg.norm(A[i]-B[j])
            lH+=lj(T[i],T[j],r,True); lN+=lj(T[i],T[j],r,False)
            lC+=KC*Q[i]*Q[j]/r
    a,b,c=lH*R,lN*R,lC*R
    if a+c<best[0]: best=(a+c,OO)
    if b+c<bestN[0]: bestN=(b+c,OO)
    if abs(OO-round(OO,1))<1e-9 or abs(OO-2.75)<1e-9:
        print(f"{OO:>8.2f} {a:>12.2f} {b:>12.2f} {c:>10.2f} {a+c:>10.2f} {b+c:>10.2f}")
print()
print(f"  최소 (Hw LJ 있음, 우리 설정): {best[0]:+.2f} kJ/mol at O-O {best[1]:.2f} Å")
print(f"  최소 (Hw LJ 없음, TIP5P 원본): {bestN[0]:+.2f} kJ/mol at O-O {bestN[1]:.2f} Å")
print(f"  참고: TIP5P 이합체 결합에너지 문헌 약 -6.8 kcal/mol = -28.5 kJ/mol, O-O 2.71 Å")
