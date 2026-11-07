# 종합자 독립 재계산 — R2 공격의 산술 근거 (문제 정본 c6ce7f25 수치만)
import math
try:
    from math import erf
    Phi=lambda x:0.5*(1+erf(x/math.sqrt(2)))
except Exception: pass
rand={'LP':[16,12,14,1.5],'MC':[16,12,8,1.5],'M1':[16,12,8,1.5]}
rss={k:math.sqrt(sum(v*v for v in vs)) for k,vs in rand.items()}
lin={k:sum(vs) for k,vs in rand.items()}
DA={'LP':(58,45,70),'MC':(48,35,60),'M1':(72,60,84)}; CD={'LP':88,'MC':75,'M1':97}
topo={'LP':(22,34),'MC':(80,110),'M1':(65,95)}
print("== 무작위 RSS/선형(전폭)", {k:(round(rss[k],2),lin[k]) for k in rss})
print("== N+1 Mack 마진(DA 중앙, 토포 평균/최대) · 전RSS · 선형")
for L in ['LP','MC','M1']:
    for T in topo[L]:
        mack=rss[L]+8+T; linr=lin[L]+8+T; arss=math.sqrt(rss[L]**2+25+9+T*T)
        print(f"  {L} T={T}: Mack {DA[L][0]-mack:+.1f} [{DA[L][1]-mack:+.1f},{DA[L][2]-mack:+.1f}] | 선형 {DA[L][0]-linr:+.1f} | 전RSS {DA[L][0]-arss:+.1f} | CD기준 Mack {CD[L]-mack:+.1f}")
print("== 현 세대 N Mack (LS 동일 가정)")
N={'LP':(70,64,76,20,30),'M1':(95,88,102,70,100)}
for L,(d,lo,hi,tm,tx) in N.items():
    for T in (tm,tx): print(f"  {L} T={T}: Mack {d-(rss[L]+8+T):+.1f}  선형 {d-(lin[L]+8+T):+.1f}  전RSS {d-math.sqrt(rss[L]**2+34+T*T):+.1f}")
print("== 차분 Δ마진 = ΔDA − ΔT (평균) · CI(반폭 RSS)")
for L,(d,lo,hi,tm,tx) in N.items():
    dDA=DA[L][0]-d; hw=math.sqrt(((DA[L][2]-DA[L][1])/2)**2+((hi-lo)/2)**2); dT=topo[L][0]-tm
    print(f"  {L}: ΔDA {dDA:+} ΔT {dT:+} → Δ {dDA-dT:+.1f}  CI ±{hw:.1f} → [{dDA-dT-hw:+.1f},{dDA-dT+hw:+.1f}]")
print("== 경제성: 0.1%=108억 · 1만원/장=72억 · D1 −0.4% 순다이 =", 0.4*1080, "억/년 · 손익분기 초과손실 =", 432/1080, "%p")
print("   C2 연간 = 3.5×72 =",3.5*72,"+ 결함 0.05~0.15% =",0.5*108,"~",1.5*108," → 합",252+54,"~",252+162, " | X1 = 6×72 =",6*72)
print("== T* (평탄화 문턱) = DA×1.2 − (RSS+8) [0.33NA] · 0.55NA: DA=(40~55)×0.64~0.74 ×1.32 − (RSS+8)")
for L in ['LP','MC','M1']:
    print(f"  {L} 0.33NA: {DA[L][0]*1.2-(rss[L]+8):.1f} (P1 없음 {DA[L][0]-(rss[L]+8):.1f})")
for L in ['LP','MC']:
    lo=40*0.64*1.32-(rss[L]+8); hi=55*0.74*1.32-(rss[L]+8); print(f"  {L} 0.55NA: {lo:.1f} ~ {hi:.1f}")
print("== 창 겹침(패턴 편차 포함) 대 표의 공통 DoF")
for L,(a,b,d) in {'LP':(115,95,15),'MC':(100,85,12),'M1':(125,110,20)}.items():
    ov=min(a,b) if d<=abs(a-b)/2 else (a+b)/2-d
    print(f"  {L}: 겹침 {ov} vs 표 {CD[L]} (차 {ov-CD[L]:+.1f})")
print("== 꼬리 확률(양쪽) k=3.09→", round(2*(1-Phi(3.09))*100,3),"% · k=3→",round(2*(1-Phi(3))*100,3),"% · k=2.5→",round(2*(1-Phi(2.5))*100,2),"% · k=1.96→",round(2*(1-Phi(1.96))*100,2),"%")
print("== P1 결함 인지 이득(CD % 를 DA 에 그대로): ", {L:(round(DA[L][0]*0.12,1),round(DA[L][0]*0.20,1)) for L in DA})
print("== P2: 재현 성분(분산 기준) 스캐너 60%·평탄도 40% 를 25~35% 감소 → RSS")
for L in ['LP','MC']:
    for f in (0.25,0.35):
        s2=16*16*(1-0.6*f)+12*12*(1-0.4*f)+sum(v*v for v in rand[L][2:]); print(f"  {L} f={f}: RSS {math.sqrt(s2):.2f} (이득 {rss[L]-math.sqrt(s2):.2f})")
