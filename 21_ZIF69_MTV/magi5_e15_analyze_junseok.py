# -*- coding: utf-8 -*-
"""E-15 기계적 수(판정 아님) — 등록 예측 (1)~(4) 에 들어갈 양만 계산. `ASSIGN_MAGI5B §Junseok 5차 ②`.
G = S_ON / S_OFF, ± = 두 상대 ± 의 제곱합. ρ = Spearman(G, S_ON) 46행 + 부트스트랩(10,000, 씨앗 20260925) 95 % 백분위 구간.
짝(3): asr_fsr_pair 가 서로를 가리키고 둘 다 대상 안 · 둘 다 anion_removed 없음 → |ΔG| / √(e₁² + e₂²) (합성 ±) 와 / max(e₁, e₂) 둘 다."""
import json
import math
import random
import statistics as st

D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
d = json.load(open(D + 'results_magi5_e15_offwidom_junseok.json', encoding='utf-8'))
rows = [r for r in d['rows'] if r.get('status') == 'ok']
print(f"행 {len(d['rows'])} · ok {len(rows)} · 비정상 {[(r['name'], r['status']) for r in d['rows'] if r.get('status') != 'ok']}")
for r in rows:
    r['G'] = r['S_ON'] / r['S_OFF']
    r['G_err'] = r['G'] * math.hypot(r['S_ON_err'] / r['S_ON'], r['S_OFF_err'] / r['S_OFF'])


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float('nan')


g3 = [r['G'] for r in rows if r.get('set') == '3D']
g2 = [r['G'] for r in rows if r.get('set') == '2D']
print(f"(1) 3D {len(g3)}행 G 중앙 {st.median(g3):.3f} · 범위 {min(g3):.2f}~{max(g3):.2f}")
G = [r['G'] for r in rows]
S = [r['S_ON'] for r in rows]
rho = spearman(G, S)
rnd = random.Random(20260925)
boots = []
for _ in range(10000):
    idx = [rnd.randrange(len(rows)) for _ in rows]
    b = spearman([G[i] for i in idx], [S[i] for i in idx])
    if not math.isnan(b):
        boots.append(b)
boots.sort()
lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]
print(f"(2) ρ(G, S_ON) {len(rows)}행 = {rho:.3f} · 부트스트랩 95 % [{lo:.3f}, {hi:.3f}] ({len(boots)} 회)")
by = {r['key']: r for r in rows}
pairs, seen = [], set()
for r in rows:
    p = r.get('asr_fsr_pair')
    if not p or p not in by or (p, r['key']) in seen:
        continue
    q = by[p]
    seen.add((r['key'], p))
    if r.get('anion_removed') or q.get('anion_removed'):
        continue
    dG = abs(r['G'] - q['G'])
    u_q = dG / math.hypot(r['G_err'], q['G_err'])
    u_m = dG / max(r['G_err'], q['G_err'])
    pairs.append((r['key'], q['key'], r['G'], q['G'], u_q, u_m))
out_q = sum(p[4] > 1.5 for p in pairs)
out_m = sum(p[5] > 1.5 for p in pairs)
print(f"(3) ASR/FSR 짝 {len(pairs)} (anion_removed 제외) · 1.5 단위 밖: 합성 ± 로 {out_q}/{len(pairs)} · max ± 로 {out_m}/{len(pairs)} "
      f"(기각선: 1/3 넘게 = {len(pairs) / 3:.1f} 초과)")
for p in pairs:
    print(f"      {p[0]:<24} G {p[2]:.3f}  ·  {p[1]:<24} G {p[3]:.3f}  ·  {p[4]:.2f} / {p[5]:.2f} 단위")
print(f"(4) 2D {len(g2)}행 G 중앙 {st.median(g2):.3f} 대 3D {len(g3)}행 {st.median(g3):.3f}")
print(f"    참고: 46행 G 중앙 {st.median(G):.3f} · ln_ratio 중앙 {st.median([r['ln_ratio'] for r in rows]):.3f} · "
      f"G < 1 행 {sum(g < 1 for g in G)} · anion_removed 행 {[r['name'] for r in rows if r.get('anion_removed')]}")
for r in sorted(rows, key=lambda r: -r['G'])[:5]:
    print(f"    G 상위 {r['name']:<24} {r['set']} S_ON {r['S_ON']:.1f} S_OFF {r['S_OFF']:.1f} G {r['G']:.2f} ± {r['G_err']:.2f}")
