# -*- coding: utf-8 -*-
"""MAGI-006 R1 Junseok(Caspar) 계산 — 입력은 문제 정본(c6ce7f25:21_ZIF69_MTV/MAGI/MAGI-006_problem.md)의 가상 수치만.
폭 규약: 모든 항을 '전폭(창 폭과 같은 단위)' 으로 통일. ±x → 2x · p-v → 그대로 · '전 폭' 명시 → 그대로 · 명시 없음 → 그대로(전폭으로 가정; 반폭이면 ×2 — 별도 감도).
결합 규칙 셋: linear(전 항목 선형) · mack(무작위 RSS + 계통 선형) · rss(전 항목 RSS).
마진 = DoF(전폭) − 예산(전폭). 패턴 간 최적 초점 편차는 공통 DoF 안에 이미 들어 있으므로(겹침 산술로 확인) 기본 예산에서 뺌 — '문서대로(편차 포함)' 판을 따로 냄."""
import math

S = {'fab16': 16.0, 'ven10': 10.0, 'ven20': 20.0}          # 팹 모니터 ±8 → 16 · 제조사 10(전폭으로 읽음) · 제조사 ±10(반폭으로 읽음) → 20
FLAT, RET, LENS, RES = 12.0, 1.5, 5.0, 3.0
LS = {'LP': 14.0, 'MC': 8.0, 'M1': 8.0}
OFF = {'LP': 15.0, 'MC': 12.0, 'M1': 20.0}
TOPO = {'LP': {'mean': 22.0, 'max': 34.0}, 'MC': {'mean': 80.0, 'max': 110.0}, 'M1': {'mean': 65.0, 'max': 95.0}}
DDEF = {'LP': (58.0, 45.0, 70.0), 'MC': (48.0, 35.0, 60.0), 'M1': (72.0, 60.0, 84.0)}     # 결함 인지 공통 DoF (중앙, 95% 하한, 상한)
DCD = {'LP': 88.0, 'MC': 75.0, 'M1': 97.0}
PAT = {'LP': (115.0, 95.0), 'MC': (100.0, 85.0), 'M1': (125.0, 110.0)}
NDEF = {'LP': (70.0, 64.0, 76.0), 'M1': (95.0, 88.0, 102.0)}
NCD = {'LP': 105.0, 'M1': 125.0}
NTOPO = {'LP': {'mean': 20.0, 'max': 30.0}, 'M1': {'mean': 70.0, 'max': 100.0}}
NLOSS = {'LP': 0.3, 'M1': 0.2}
PILOT = {'LP': (0.4, 0.9), 'MC': (4.0, 8.0), 'M1': (0.6, 1.2)}
LAYERS = ('LP', 'MC', 'M1')
RULES = ('linear', 'mack', 'rss')


def rnd_terms(layer, s, s_scale=1.0, f_scale=1.0):
    return [s * s_scale, FLAT * f_scale, LS[layer], RET]


def budget(layer, s, topo, rule, off=False, s_scale=1.0, f_scale=1.0, lens_res=True):
    r = rnd_terms(layer, s, s_scale, f_scale)
    y = ([LENS, RES] if lens_res else []) + [topo] + ([OFF[layer]] if off else [])
    if rule == 'linear':
        return sum(r) + sum(y)
    if rule == 'mack':
        return math.sqrt(sum(x * x for x in r)) + sum(y)
    return math.sqrt(sum(x * x for x in r + y))


def overlap(w1, w2, d):
    return min(w1 / 2, d + w2 / 2) - max(-w1 / 2, d - w2 / 2)


print('=== 0. 경제성 상수 검산')
rev = 720000 * 1500e4
print(f'  연매출 {rev/1e12:.2f} 조원 · 수율 0.1% = {rev*0.001/1e8:.1f} 억 · 웨이퍼당 1만원 = {720000*1e4/1e8:.1f} 억')

print('\n=== 1. 이중 계상 검사 — 두 패턴 창의 겹침(최적 초점 편차 d) 대 표의 공통 DoF(CD)')
for L in LAYERS:
    w1, w2 = PAT[L]
    print(f'  {L}: 겹침({w1:.0f},{w2:.0f},d={OFF[L]:.0f}) = {overlap(w1, w2, OFF[L]):.1f}  대 공통 DoF {DCD[L]:.0f}  (편차 없이 겹침 = {min(w1,w2):.0f})')
print('  CD→결함 인지 감소폭:', {L: DCD[L] - DDEF[L][0] for L in LAYERS}, '· 토포 평균', {L: TOPO[L]['mean'] for L in LAYERS},
      '· 현 세대', {L: NCD[L] - NDEF[L][0] for L in ('LP', 'M1')})

print('\n=== 2. 무작위 항 합(전폭)')
for L in LAYERS:
    for sk, s in S.items():
        r = rnd_terms(L, s)
        print(f'  {L} {sk}: 선형 {sum(r):.1f} · RSS {math.sqrt(sum(x*x for x in r)):.2f}')

print('\n=== 3. N+1 감도표 — 마진 = 결함 인지 공통 DoF − 예산 (편차 제외; [하한, 상한] = DoF 95% 구간) | CD 공통 DoF 기준 마진')
for L in LAYERS:
    d0, dl, dh = DDEF[L]
    print(f'  -- {L} (결함 인지 {d0:.0f} [{dl:.0f},{dh:.0f}] · CD 공통 {DCD[L]:.0f})')
    for rule in RULES:
        for sk, s in S.items():
            row = []
            for tk in ('mean', 'max'):
                b = budget(L, s, TOPO[L][tk], rule)
                row.append(f'{tk} 예산 {b:6.1f} → {d0-b:+6.1f} [{dl-b:+6.1f},{dh-b:+6.1f}] | CD {DCD[L]-b:+6.1f}')
            print(f'    {rule:6s} {sk:5s}  ' + '  ‖  '.join(row))
    for sk, s in S.items():
        b = budget(L, s, TOPO[L]['mean'], 'linear', off=True)
        bm = budget(L, s, TOPO[L]['max'], 'linear', off=True)
        print(f'    linear+편차(팹 문서 그대로) {sk}: mean {d0-b:+.1f} · max {d0-bm:+.1f}')

print('\n=== 4. 현 세대 N — 같은 규칙 · 같은 무작위 항(같은 NXE 장비군 가정) · 편차 제외')
for rule in RULES:
    for sk, s in S.items():
        out = []
        for L in ('LP', 'M1'):
            d0, dl, dh = NDEF[L]
            for tk in ('mean', 'max'):
                b = budget(L, s, NTOPO[L][tk], rule)
                out.append((L, tk, d0 - b))
        m = {(L, tk): v for L, tk, v in out}
        order = ['LP>M1' if m[('LP', tk)] > m[('M1', tk)] else 'LP<M1' for tk in ('mean', 'max')]
        print(f'  {rule:6s} {sk:5s} LP mean {m[("LP","mean")]:+6.1f} max {m[("LP","max")]:+6.1f} · M1 mean {m[("M1","mean")]:+6.1f} max {m[("M1","max")]:+6.1f}'
              f'  · 마진 순서 {order} 대 손실 LP 0.3 > M1 0.2(= LP 마진이 작아야 정합)')

print('\n=== 5. 차분 — (N+1 마진) − (N 마진), 같은 레이어 · 같은 장비군 → 공통 항 상쇄')
for L in ('LP', 'M1'):
    for tk in ('mean', 'max'):
        dD = DDEF[L][0] - NDEF[L][0]
        dT = TOPO[L][tk] - NTOPO[L][tk]
        hw = math.hypot((DDEF[L][2] - DDEF[L][1]) / 2, (NDEF[L][2] - NDEF[L][1]) / 2)
        lin = dD - dT
        rs = []
        for sk, s in S.items():
            rs.append((DDEF[L][0] - budget(L, s, TOPO[L][tk], 'rss')) - (NDEF[L][0] - budget(L, s, NTOPO[L][tk], 'rss')))
        print(f'  {L} {tk}: ΔDoF {dD:+.0f} − Δ토포 {dT:+.0f} = {lin:+.1f} (linear·mack 공통) · 구간 ≈ [{lin-hw:+.1f},{lin+hw:+.1f}] (95% 반폭 제곱합 {hw:.1f}) · rss {min(rs):+.1f}~{max(rs):+.1f}')

print('\n=== 6. 조종 산술(가설 — 기울기 = 파일럿 손실 추정과 차분에서; 선형 가정)')
for L, need in (('LP', 14.0), ('M1', 18.0)):
    lo, hi = PILOT[L]
    s_lo, s_hi = (lo - NLOSS[L]) / need, (hi - NLOSS[L]) / need
    print(f'  {L}: 기울기 {s_lo:.4f}~{s_hi:.4f} %/nm (파일럿 {lo}~{hi}% · 현 {NLOSS[L]}% · 차분 {need:.0f} nm)')
    if L == 'LP':
        print(f'     LP 가 0.2% 에 닿으려면 현 LP 보다 {0.1/s_hi:.1f}~{0.1/s_lo:.1f} nm 더 → N+1 LP 필요 개선 {need+0.1/s_hi:.1f}~{need+0.1/s_lo:.1f} nm')

print('\n=== 7. 레버 산술 (선택 규칙 mack · 스캐너 fab16; 토포 평균 · 최대는 비례 환산)')
def p2_scales():
    # 재현 성분 비율 60%(스캐너)·40%(평탄도) 를 분산 몫으로 읽음: 재현 진폭 25~35% 감소 → 분산 몫 × (0.65²~0.75²)
    out = {}
    for red in (0.25, 0.35):
        k = (1 - red) ** 2
        out[red] = (math.sqrt(0.4 + 0.6 * k), math.sqrt(0.6 + 0.4 * k))
    return out
P2 = p2_scales()
print('  P2 분산 해석 계수(스캐너, 평탄도):', {k: (round(a, 3), round(b, 3)) for k, (a, b) in P2.items()})
for red in (0.25, 0.35):
    # 진폭 가산 해석: 스캐너 16 = 재현 9.6 + 비재현 6.4 → 재현만 감소
    sa = (16 * 0.6 * (1 - red) + 16 * 0.4) / 16
    fa = (12 * 0.4 * (1 - red) + 12 * 0.6) / 12
    print(f'  P2 진폭 해석 red {red}: 스캐너 계수 {sa:.3f} · 평탄도 계수 {fa:.3f}')
for L in LAYERS:
    base = math.sqrt(sum(x * x for x in rnd_terms(L, 16)))
    g = [base - math.sqrt(sum(x * x for x in rnd_terms(L, 16, a, b))) for a, b in P2.values()]
    gl = [sum(rnd_terms(L, 16)) - sum(rnd_terms(L, 16, a, b)) for a, b in P2.values()]
    print(f'  P2 이득 {L}: mack(RSS) {min(g):.1f}~{max(g):.1f} nm · linear {min(gl):.1f}~{max(gl):.1f} nm')
for L in LAYERS:
    print(f'  P1 {L}: CD 기준 +{0.12*DCD[L]:.1f}~{0.20*DCD[L]:.1f} · 결함 인지에 같은 % 가정 +{0.12*DDEF[L][0]:.1f}~{0.20*DDEF[L][0]:.1f} (미측정)')
w1, w2 = PAT['LP']
print(f'  D1 LP: 편차 15→8~10 이면 CD 겹침 {overlap(w1,w2,15):.1f} → {overlap(w1,w2,10):.1f}~{overlap(w1,w2,8):.1f} (+{overlap(w1,w2,10)-overlap(w1,w2,15):.1f}~{overlap(w1,w2,8)-overlap(w1,w2,15):.1f}) · 토포 22→10~14 (−8~−12; 최대 34→{34*10/22:.1f}~{34*14/22:.1f})')

def mack_margin(L, dof, topo, s_scale=1.0, f_scale=1.0):
    return dof - budget(L, 16.0, topo, 'mack', s_scale=s_scale, f_scale=f_scale)

print('  -- MC (결함 인지 48 [35,60])')
for name, t_lo, t_hi in (('레버 없음', 80, 80), ('C1', 35, 50), ('C2', 15, 25), ('C3(제조사 발표)', 5, 5)):
    for tk, sc in (('mean', 1.0), ('max', 110 / 80)):
        vals = []
        for t in (t_lo, t_hi):
            for dof in (48, 35):
                for p1 in (0.0, 0.12, 0.20):
                    vals.append(mack_margin('MC', dof * (1 + p1), t * sc))
        m0 = [mack_margin('MC', 48, t * sc) for t in (t_lo, t_hi)]
        m1 = [mack_margin('MC', 48 * 1.2, t * sc) for t in (t_lo, t_hi)] + [mack_margin('MC', 48 * 1.12, t * sc) for t in (t_lo, t_hi)]
        m12 = [mack_margin('MC', 48 * (1 + p), t * sc, *ab) for t in (t_lo, t_hi) for p in (0.12, 0.2) for ab in P2.values()]
        print(f'    {name:14s} {tk}: 단독(중앙 48) {min(m0):+.1f}~{max(m0):+.1f} · +P1 {min(m1):+.1f}~{max(m1):+.1f} · +P1+P2 {min(m12):+.1f}~{max(m12):+.1f} · 전체(35~48 · P1 0~20%) {min(vals):+.1f}~{max(vals):+.1f}')
print('  -- M1 (결함 인지 72 [60,84])')
RSS_M1 = math.sqrt(sum(x * x for x in rnd_terms('M1', 16)))
for name, t_lo, t_hi in (('레버 없음', 65, 65), ('C1(M1 추정)', 30, 45), ('C2(M1 추정)', 12, 22), ('P1만', 65, 65), ('P1+P2', 65, 65)):
    for tk, sc in (('mean', 1.0), ('max', 95 / 65)):
        p1s = (0.12, 0.2) if 'P1' in name else (0.0,)
        abs_ = tuple(P2.values()) if 'P2' in name else ((1.0, 1.0),)
        m = [mack_margin('M1', 72 * (1 + p), t * sc, *ab) for t in (t_lo, t_hi) for p in p1s for ab in abs_]
        mlo = [mack_margin('M1', 60 * (1 + p), t * sc, *ab) for t in (t_lo, t_hi) for p in p1s for ab in abs_]
        # 차분(현 M1 대비): ΔDoF −23 (P1 이면 +72p) − (토포 − 70·(max 이면 100)) + P2 이득(N+1 에만)
        nt = 70 if tk == 'mean' else 100
        dd = [(72 * (1 + p) - 95) - (t * sc - nt) + (RSS_M1 - math.sqrt(sum(x * x for x in rnd_terms('M1', 16, *ab))))
              for t in (t_lo, t_hi) for p in p1s for ab in abs_]
        print(f'    {name:12s} {tk}: 절대(중앙) {min(m):+.1f}~{max(m):+.1f} · 절대(하한 60) {min(mlo):+.1f}~{max(mlo):+.1f} · 차분(현 M1=0.2% 기준) {min(dd):+.1f}~{max(dd):+.1f}')
print('  -- LP (결함 인지 58 [45,70]) — 평탄화 레버(C) 는 LP 에 해당 없음(커패시터 전). D1 의 DoF 이득 = 겹침 산술 +5(결함 인지에도 같은 절대값 가정)')
RSS_LP = math.sqrt(sum(x * x for x in rnd_terms('LP', 16)))
for name in ('레버 없음', 'P1', 'P1+P2', 'P1+P2+D1', 'D1', 'P2+D1'):
    for tk in ('mean', 'max'):
        t0 = TOPO['LP'][tk]
        res = []
        for p in ((0.0,) if 'P1' not in name else (0.12, 0.2)):
            for ab in ((1.0, 1.0),) if 'P2' not in name else tuple(P2.values()):
                for d1 in ((0.0, 0.0),) if 'D1' not in name else ((5.0, 8.0), (5.0, 12.0)):
                    dof = 58 * (1 + p) + d1[0]
                    t = t0 - d1[1] * (1 if tk == 'mean' else 34 / 22)
                    p2gain = RSS_LP - math.sqrt(sum(x * x for x in rnd_terms('LP', 16, *ab)))   # N+1 에만 걸리는 무작위 항 감소(차분에 더함)
                    res.append((mack_margin('LP', dof, t, *ab), (dof - 70) - (t - NTOPO['LP'][tk]) + p2gain))
        a = [x for x, _ in res]
        dd = [y for _, y in res]
        print(f'    {name:10s} {tk}: 절대 mack {min(a):+.1f}~{max(a):+.1f} · 차분(현 LP=0.3% 기준) {min(dd):+.1f}~{max(dd):+.1f}')

print('\n=== 8. 비용(억원) — 연간 | 일회성')
Y = 108.0  # 억/0.1%
W = 72.0   # 억/만원
cost = {
    'P1(레이어당)': (0, 5), 'P2': (0, 120), 'C1': (0.8 * W, 0), 'C2': ((3.5 * W + 0.05 * 10 * Y, 3.5 * W + 0.15 * 10 * Y), 1),
    'C3': (2 * W, 1400), 'D1(순다이 −0.4%)': (0.4 * 10 * Y, 0), 'X1': (6 * W, 0)}
for k, v in cost.items():
    print(f'  {k}: 연간 {v[0]} | 일회성 {v[1]}')
for L in LAYERS:
    lo, hi = PILOT[L]
    print(f'  목표 초과 손실(파일럿 − 0.2%) {L}: {(lo-0.2)*10*Y:.0f}~{(hi-0.2)*10*Y:.0f} 억/년')
for n in (1, 2, 3):
    print(f'  C2 레이어당 연간(수혜 {n}): {(3.5*W+0.05*10*Y)/n:.0f}~{(3.5*W+0.15*10*Y)/n:.0f} · C3 레이어당 일회 {1400/n:.0f} + 연간 {2*W/n:.0f}')

print('\n=== 9. Q4 — 0.55NA')
for lab, lo, hi in (('문제 모의 40~55', 40.0, 55.0), ('imec 2~3배 감소(88/3~88/2)', 88 / 3, 88 / 2)):
    for ratio_lab, r in (('결함/CD 0.64(MC)', 0.64), ('0.74(M1)', 0.74)):
        dl, dh = lo * r, hi * r
        for plab, p in (('레버 없음', 0.0), ('SMO+SRAF 18%', 0.18), ('비대칭 32%', 0.32)):
            t_lo = dl * (1 + p) - math.sqrt(sum(x * x for x in rnd_terms('MC', 16))) - 8
            t_hi = dh * (1 + p) - math.sqrt(sum(x * x for x in rnd_terms('MC', 16))) - 8
            print(f'  {lab:28s} {ratio_lab:16s} {plab:12s}: Photo 이득(결함 인지 척도) +{dl*p:.1f}~{dh*p:.1f} · 허용 단차 문턱 {t_lo:+.1f}~{t_hi:+.1f} nm')
t033 = [72 - math.sqrt(sum(x * x for x in rnd_terms('M1', 16))) - 8, 48 - math.sqrt(sum(x * x for x in rnd_terms('MC', 16))) - 8]
print(f'  0.33NA 허용 단차 문턱(레버 없음): M1 {t033[0]:.1f} · MC {t033[1]:.1f} · LP {58 - math.sqrt(sum(x*x for x in rnd_terms("LP",16))) - 8:.1f}')
for L in LAYERS:
    print(f'  0.33NA P1 이득 CD {0.12*DCD[L]:.1f}~{0.20*DCD[L]:.1f} → 결함 인지 {0.12*DDEF[L][0]:.1f}~{0.20*DDEF[L][0]:.1f}')
