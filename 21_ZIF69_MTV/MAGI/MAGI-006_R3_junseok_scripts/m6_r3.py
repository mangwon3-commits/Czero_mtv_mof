#!/usr/bin/env python3
"""MAGI-006 R3 (Junseok/Caspar) 수비 산술. 입력 = 문제 정본 c6ce7f25 의 가상 수치뿐. 저장소 파일을 읽지 않음.
절 이름 = R3 의 D-k. 규약은 R1 m6_calc.py 와 같음(전폭, 편차 제외, 스캐너 16 기본, Mack = 무작위 RSS + 계통 선형)."""
import math
from statistics import NormalDist, mean

N = NormalDist()
LS = {'LP': 14, 'MC': 8, 'M1': 8}
DA = {'LP': 58, 'MC': 48, 'M1': 72}
DA_N = {'LP': 70, 'M1': 95}
CD = {'LP': 88, 'MC': 75, 'M1': 97}
TOPO = {'LP': (22, 34), 'MC': (80, 110), 'M1': (65, 95)}
TOPO_N = {'LP': (20, 30), 'M1': (70, 100)}
PAT = {'LP': (115, 95, 15), 'MC': (100, 85, 12), 'M1': (125, 110, 20)}
SYS = 5 + 3


def rnd(L, s=16, a=1.0, b=1.0, ls=None):
    return [s * a, 12 * b, LS[L] if ls is None else ls, 1.5]


def rss(x):
    return math.sqrt(sum(v * v for v in x))


def mack(L, dof, t, s=16, a=1.0, b=1.0, ls=None):
    return dof - rss(rnd(L, s, a, b, ls)) - SYS - t


def lin(L, dof, t, s=16):
    return dof - sum(rnd(L, s)) - SYS - t


def allrss(L, dof, t, s=16):
    return dof - math.sqrt(sum(v * v for v in rnd(L, s)) + 25 + 9 + t * t)


def overlap(w1, w2, d):
    return max(0.0, min(w1, w2, (w1 + w2) / 2 - abs(d)))


print('== D-2 (A-2) P2 이득: 네 가지 읽기 · 감소율 25 / 35 % ==')


def readings(red):
    return {
        '가 분산 몫 · σ 감소 (R1 "분산")': (math.sqrt(0.6 * (1 - red) ** 2 + 0.4), math.sqrt(0.4 * (1 - red) ** 2 + 0.6)),
        '나 선형 진폭 분할 (R1 "진폭" · B)': (1 - 0.6 * red, 1 - 0.4 * red),
        '다 분산 몫 · 분산 감소 (종합자 "분산")': (math.sqrt(1 - 0.6 * red), math.sqrt(1 - 0.4 * red)),
        '라 σ 몫 · σ 감소': (math.sqrt((0.6 * (1 - red)) ** 2 + 0.64), math.sqrt((0.4 * (1 - red)) ** 2 + 0.84)),
    }


G = {}
for L in ('LP', 'MC'):
    base, bl = rss(rnd(L)), sum(rnd(L))
    for red in (0.25, 0.35):
        for k, (a, b) in readings(red).items():
            g, gl = base - rss(rnd(L, 16, a, b)), bl - sum(rnd(L, 16, a, b))
            G.setdefault((L, k[0]), []).append((g, gl, a, b))
            print(f'  {L} {int(red * 100)}% {k:34s} 계수({a:.3f},{b:.3f})  Mack {g:.2f}  선형 {gl:.2f}')
for L in ('LP', 'MC'):
    for k in '가나다라':
        v = G[(L, k)]
        print(f'  {L} 읽기 {k}: Mack {v[0][0]:.2f}~{v[1][0]:.2f} · 선형 {v[0][1]:.2f}~{v[1][1]:.2f}')
    gg = [x[0] for k in '가나다라' for x in G[(L, k)]]
    print(f'  {L} 네 읽기 전체 Mack {min(gg):.2f}~{max(gg):.2f}')
ga, gb = [x[0] for x in G[('LP', '가')]], [x[0] for x in G[('LP', '나')]]
print(f'  R1 의 두 읽기(가 · 나) 차 LP Mack: {abs(gb[0] - ga[0]):.2f} · {abs(gb[1] - ga[1]):.2f} nm  (R1 "차 < 0.1" 은 틀림)')
allLP = [x for k in '가나다라' for x in G[('LP', k)]]
allMC = [x for k in '가나다라' for x in G[('MC', k)]]
p2lo, p2hi = min(x[0] for x in allLP), max(x[0] for x in allLP)
print(f'  LP P1+P2 차분(현 LP 대비, 평균): R1 −5.1~+0.2 → 네 읽기 {-14 + 58 * 0.12 + p2lo:+.1f}~{-14 + 58 * 0.20 + p2hi:+.1f}')
ms = [mack('MC', 48 * (1 + p), t, 16, a, b) for t in (15, 25) for p in (0.12, 0.20) for (_, _, a, b) in allMC]
print(f'  MC C2+P1+P2 절대 Mack 평균: R1 +1.4~+16.0 → 네 읽기 {min(ms):+.1f}~{max(ms):+.1f}')
m1 = [-18 + 72 * p + (rss(rnd('M1')) - rss(rnd('M1', 16, a, b))) for p in (0.12, 0.20) for (_, _, a, b) in allMC]
print(f'  M1 P1+P2 차분: R1 −7.1~−0.6 → 네 읽기 {min(m1):+.1f}~{max(m1):+.1f}')
lpd2 = [-14 + 58 * p + 5 + 8 + (rss(rnd('LP')) - rss(rnd('LP', 16, a, b))) for p in (0.12, 0.20) for (_, _, a, b) in allLP]
lpd3 = [-14 + 58 * p + 5 + 12 + (rss(rnd('LP')) - rss(rnd('LP', 16, a, b))) for p in (0.12, 0.20) for (_, _, a, b) in allLP]
print(f'  LP P1+P2+D1 차분(평균, D1 = 편차 +5 · 토포 22→10~14): R1 +7.9~+17.2 → 네 읽기 {min(lpd2 + lpd3):+.1f}~{max(lpd2 + lpd3):+.1f}')

print('\n== D-3 (A-3) 토포가 결함 인지 DoF 안에 일부 들어 있을 수 있는 상한 ==')
for L in ('LP', 'MC', 'M1'):
    w1, w2, d = PAT[L]
    ov = overlap(w1, w2, d)
    print(f'  {L}: 겹침 {ov:.1f} − CD 공통 {CD[L]} = {ov - CD[L]:.1f} (CD 창에 든 토포 상한, 편차는 모의값) · CD − DA = {CD[L] - DA[L]} · 토포 평균 {TOPO[L][0]}')
rows = [(22, 30), (80, 27), (65, 25), (20, 35), (70, 30)]
xs, ys = [r[0] for r in rows], [r[1] for r in rows]
mx, my = mean(xs), mean(ys)
sxx = sum((x - mx) ** 2 for x in xs)
b = sum((x - mx) * (y - my) for x, y in rows) / sxx
a0 = my - b * mx
se = math.sqrt(sum((y - a0 - b * x) ** 2 for x, y in rows) / 3 / sxx)
t3 = 3.182
print(f'  (CD − DA) 대 토포, 다섯 행 회귀: 기울기 {b:+.3f} (95 % {b - t3 * se:+.3f} ~ {b + t3 * se:+.3f}) — 토포가 DA 안에 f 만큼 들어 있으면 기울기 ≈ f')
need = -mack('MC', 48, 80)
print(f'  MC Mack 이 0 이 되려면 DA 안에 든 토포 {need:.1f} nm (f = {need / 80:.2f}) 필요 — 그러면 MC 의 CD − DA 는 기저 + {need:.1f} 이어야 하는데 실측 27')
inc = (CD['MC'] - DA['MC']) + (overlap(*PAT['MC']) - CD['MC'])
print(f'  극단 상한: CD−DA 27 전부 + 겹침 차 5.5 전부가 토포라 해도 포함 ≤ {inc:.1f} nm')
for s in (16, 10):
    for dof, lab in ((48, '중앙 48'), (60, '상한 60')):
        tt = 80 - inc
        print(f'    s{s} DA {lab}: 선형 {lin("MC", dof, tt, s):+.1f} · Mack {mack("MC", dof, tt, s):+.1f} · 전 RSS {allrss("MC", dof, tt, s):+.1f}  (최대 토포 110−{inc:.1f}: Mack {mack("MC", dof, 110 - inc, s):+.1f})')

print('\n== D-5 (A-5) Q3 원인 후보의 정합 검산 — 두 레이어를 동시에 맞히려면 ==')
lpN, m1N = mack('LP', 70, 20), mack('M1', 95, 70)
off = lpN - m1N
print(f'  현 LP Mack {lpN:+.1f} (0.3 %) · 현 M1 {m1N:+.1f} (0.2 %) → 한 곡선이면 LP 가 M1 보다 마진이 작아야 함. 필요한 이동 ≥ {off:.1f} nm')
sLP, sM1 = rss(rnd('LP')) / 6, rss(rnd('M1')) / 6
kL, kM = 3 + lpN / (2 * sLP), 3 + m1N / (2 * sM1)
print(f'  J-7a(레이어별 사상 = 임계 자리 수 비): 가우스 꼬리(σ LP {sLP:.2f} · M1 {sM1:.2f}, k {kL:.2f} · {kM:.2f})면 N_LP/N_M1 ≈ {1.5 * N.cdf(-kM) / N.cdf(-kL):.1e}')
for lam in (10.0, 17.5):
    print(f'      경험 e-배 폭 {lam} nm [가설 · 파일럿]면 N_LP/N_M1 ≈ {1.5 * math.exp(off / lam):.1f}')
for Lp in (0.6, 1.2):
    print(f'      M1 차분 18 nm 에 파일럿 {Lp} % → e-배 폭 {18 / math.log(Lp / 0.2):.1f} nm')
kM0 = -N.inv_cdf(0.002)
print(f'      참고 — M1 σ {sM1:.2f} 가우스면 18 nm 악화 → {N.cdf(-(kM0 - 9 / sM1)) * 100:.0f} % (파일럿 0.6~1.2 %)')
x_r = math.sqrt((70 - SYS - 20 - m1N) ** 2 - rss([16, 12, 1.5]) ** 2)
x_s = 70 - SYS - 20 - rss([16, 12, 1.5]) - m1N
print(f'  J-7c(LP 스택 LS 과소): 현 LP 마진을 M1 수준({m1N:+.1f})까지 내리려면 LS 가 무작위면 {x_r:.1f} · 계통(선형)이면 {x_s:.1f} nm 필요(문제 값 14)')
print(f'      비교: LS 를 계통으로만 옮기면 현 LP {70 - SYS - 20 - rss([16, 12, 1.5]) - 14:+.1f} · 현 M1 {95 - SYS - 70 - rss([16, 12, 1.5]) - 8:+.1f} → 역전 유지')
print('  J-7b(M1 단차가 창을 통째로 먹지 않음) — 두 패턴 장난감 모형: 제한 패턴이 한 높이에만 있을 때 소모 = 겹침 차')
for L, t in (('M1', 65), ('MC', 80)):
    w1, w2, d = PAT[L]
    base = overlap(w1, w2, d)
    fav, adv = base - overlap(w1, w2, d - t), base - overlap(w1, w2, d + t)
    print(f'    {L}: 단차 {t} · 편차 {d} → 소모 순방향 {fav:.1f} / 역방향 {adv:.1f} (선형 뺄셈 = {t})')
t_need = 95 - SYS - rss(rnd('M1')) - lpN
print(f'    현 M1 이 현 LP 보다 마진이 커지려면 실효 소모 ≤ {t_need:.1f} (70 중). 순방향이면 {overlap(125, 110, 20) - overlap(125, 110, 20 - 70):.1f} → 맞음 · 역방향 또는 제한 패턴이 두 높이 모두에 있으면 70 → 안 맞음')
print(f'    MC 는 순방향이어도 Mack {mack("MC", 48, overlap(100, 85, 12) - overlap(100, 85, 12 - 80)):+.1f} → 부족 불변')

print('\n== D-7 (A-7) 레버 뒤 — 최대 토포 환산 세 방식 · 원인 a 의 양날 ==')
for L, avg, mxt, c2 in (('MC', 80, 110, (15, 25)), ('M1', 65, 95, (12, 22))):
    for lab, f in (('비율(R1)', lambda t: t * mxt / avg), ('가산(최대−평균 일정)', lambda t: t + (mxt - avg)), ('바닥(최대 = 평균)', lambda t: t)):
        tm = [f(t) for t in c2]
        if L == 'M1':
            dm = [-23 - (t - 100) for t in tm]
            print(f'  M1 C2 최대 토포 {lab:18s} {tm[0]:.1f}~{tm[1]:.1f} → 차분(현 M1 최대 100 대비) {min(dm):+.1f}~{max(dm):+.1f}')
        else:
            vv = [mack('MC', 48 * (1 + p), t, 16, a, b) for t in tm for p in (0.12, 0.2) for (_, _, a, b) in allMC]
            print(f'  MC C2+P1+P2 최대 토포 {lab:18s} {tm[0]:.1f}~{tm[1]:.1f} → 절대 Mack {min(vv):+.1f}~{max(vv):+.1f}')
print(f'  M1 C2 차분이 0 이 되는 잔여 단차: 평균 ≤ {70 - 23:.0f} · 최대 ≤ {100 - 23:.0f} nm')
w1, w2, d = PAT['M1']
base = overlap(w1, w2, d)


def cons(t):
    return base - overlap(w1, w2, d - t)


before, afterc2, nref = cons(65), [cons(t) for t in (12, 22)], cons(70)
print(f'  원인 a(순방향) 가정: N+1 M1 소모 {before:.1f} → C2 뒤 {afterc2[0]:.1f}~{afterc2[1]:.1f} → C2 이득 {before - max(afterc2):.1f}~{before - min(afterc2):.1f} (선형이면 43~53)')
print(f'      현 M1 소모 {nref:.1f} [가정: 편차 20 같음] → 차분 레버 없음 {-23 - (before - nref):+.1f} · C2 뒤 {-23 - (max(afterc2) - nref):+.1f}~{-23 - (min(afterc2) - nref):+.1f} (선형 +25~+35)')

print('\n== D-9 (A-9) LS 를 상수 오프셋(보정됨)으로 볼 때 ==')
for L in ('LP', 'MC', 'M1'):
    print(f'  N+1 {L} Mack: 평균 {mack(L, DA[L], TOPO[L][0]):+.1f} → LS 제외 {mack(L, DA[L], TOPO[L][0], ls=0):+.1f} · 최대 {mack(L, DA[L], TOPO[L][1]):+.1f} → {mack(L, DA[L], TOPO[L][1], ls=0):+.1f}')
for L in ('LP', 'M1'):
    print(f'  현 {L} Mack 평균: {mack(L, DA_N[L], TOPO_N[L][0]):+.1f} → {mack(L, DA_N[L], TOPO_N[L][0], ls=0):+.1f}')
print(f'  LP 에서만 LS 제외(M1 유지): 현 LP {mack("LP", 70, 20, ls=0):+.1f} 대 현 M1 {mack("M1", 95, 70):+.1f} → 역전 유지. 차분은 두 세대 같은 LS 면 불변')

print('\n== D-11 (A-11) 공정 기간 +1.2 일 · D1 비용의 가정 ==')
wip = 60000 / 30 * 1.2
rev = wip * 1500e4 / 1e8
print(f'  재공 {wip:.0f} 장 × 1,500만원 = {rev:.0f} 억(매출가 상한, 일회성 운전자본) · 자본비용 r 5~10 %/년 [가정] → {rev * 0.05:.0f}~{rev * 0.10:.0f} 억/년')
print(f'  C2 연간 306~414 + {rev * 0.05:.0f}~{rev * 0.10:.0f} = {306 + rev * 0.05:.0f}~{414 + rev * 0.10:.0f} 대 X1+C1 489.6(+ 오버레이 · ArF 라인 유지 미상)')
print(f'  D1 432 = 0.4 % × 720,000 장 × 1,500만원 = {0.004 * 720000 * 1500e4 / 1e8:.0f} 억/년 — 웨이퍼당 매출이 순다이 수에 비례할 때(가정)')
