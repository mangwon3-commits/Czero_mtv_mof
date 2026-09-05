"""두 계산이 갈린 이유 — 축 둘레 방위각(dihedral)이 최적화 안 됐습니다."""
import numpy as np
R=0.0083144626; KC=1389.3546/R
site=[('Ow',0.0,[0,0,0]),('Hw',+0.241,[0.75695,0,0.58588]),('Hw',+0.241,[-0.75695,0,0.58588]),
      ('Lw',-0.241,[0,0.57154,-0.40415]),('Lw',-0.241,[0,-0.57154,-0.40415])]
P=np.array([s[2] for s in site]); Q=np.array([s[1] for s in site]); T=[s[0] for s in site]
PAR={('Ow','Ow'):(89.633,3.097)}   # 수정 힘장: Hw/Lw LJ 없음
def lj(t1,t2,r):
    k=PAR.get((t1,t2)) or PAR.get((t2,t1))
    if k is None: return 0.0
    e,s=k; s6=(s/r)**6; return 4*e*(s6*s6-s6)
def rot(a,b):
    a=a/np.linalg.norm(a); b=b/np.linalg.norm(b); v=np.cross(a,b); c=a@b
    if np.linalg.norm(v)<1e-12: return np.eye(3) if c>0 else -np.eye(3)
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+K+K@K/(1+c)
def Rz(t):
    c,s=np.cos(t),np.sin(t); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
z=np.array([0,0,1.0])
Rd=rot(P[1],z); Ra0=rot(P[3],-z)
best=(9e9,None,None); rows=[]
for phi in np.arange(0,360,5)*np.pi/180:
    Ra=Rz(phi)@Ra0
    for OO in np.arange(2.55,3.01,0.01):
        A=(Rd@P.T).T; B=(Ra@P.T).T+np.array([0,0,OO])
        E=0.0
        for i in range(5):
            for j in range(5):
                r=np.linalg.norm(A[i]-B[j]); E+=lj(T[i],T[j],r)*R+KC*Q[i]*Q[j]/r*R
        if E<best[0]: best=(E,OO,phi*180/np.pi)
        if abs(phi)<1e-9: rows.append((OO,E))
print('  === 방위각(축 둘레 회전)을 최적화하면 ===')
print(f'  최소 **{best[0]:.2f} kJ/mol**  @  O–O **{best[1]:.2f} Å**,  방위각 {best[2]:.0f}°')
print()
print('  방위각별 최소(각 φ 에서 O–O 최적화):')
for phi in range(0,360,30):
    Ra=Rz(phi*np.pi/180)@Ra0; b=(9e9,None)
    for OO in np.arange(2.55,3.01,0.01):
        A=(Rd@P.T).T; B=(Ra@P.T).T+np.array([0,0,OO]); E=0.0
        for i in range(5):
            for j in range(5):
                r=np.linalg.norm(A[i]-B[j]); E+=lj(T[i],T[j],r)*R+KC*Q[i]*Q[j]/r*R
        if E<b[0]: b=(E,OO)
    print(f'    φ={phi:>3}°   {b[0]:>8.2f} kJ/mol  @ O–O {b[1]:.2f} Å')
