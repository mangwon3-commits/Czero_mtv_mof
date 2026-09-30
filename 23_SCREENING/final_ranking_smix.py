"""S_mix(작동점, 이원 GCMC 0.15/0.85 · 1 bar · 298 K) 축의 3D 순위표 — CoRE 행(1씨앗, CoRE 앞단) + 우리 행(3~6씨앗, 우리 앞단).

등록: COREMIX_REGISTRATION_20260930.md §3. 자료: results_coremix_s60_hkhome.json(21행 1단계) + results_tj1_mix_laptop*.json(T-J1′ CoRE 6)
+ 우리: E-24i 5(3~6씨앗) · 형판 모체(e23_mix, 3씨앗) · ZIF-69 base(T-J1′ 1씨앗) · mslm050/saIm050/sa50nb50(E-23 §1, 6실현).
순위: screen_core.rank 1.5×합성 오차(각 행의 ±: 우리 = ±̄/√n, CoRE = 1씨앗 RASPA ±). 부분 자료로도 돈다(완주 행만).
사용: /home/mangwon1/miniconda3/bin/python final_ranking_smix.py
"""
import glob, json, math, os, statistics as st, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); Z = os.path.join(HERE, '..', '21_ZIF69_MTV')
sys.path.insert(0, HERE)
from screen_core import rank

def J(p): return json.load(open(p, encoding='utf-8'))
def rows_of(d): return d['rows'] if isinstance(d, dict) and 'rows' in d else d
ANN = {r['file'][:-4]: r for r in rows_of(J(os.path.join(Z, 'core_pop_annotated.json')))}
def sel_err(kc, ec, kn, en): S = kc / kn; return S, S * math.hypot(ec / kc, en / kn)

rows, notes = [], []
# ---- CoRE: 1단계(coremix) + T-J1′
seen = {}
def add_core(r, src):
    n = r['name']; a = ANN.get(n)
    if r.get('status') != 'ok' or r.get('S_mix') is None: return
    SH, SHe = sel_err(a['KH_CO2'], a['KH_CO2_err'], a['KH_N2'], a['KH_N2_err']) if a else (r.get('S_Henry'), r.get('S_Henry_err') or 0)
    row = dict(name=n, label=n.replace('__', ' ').replace('_', ' '), type='CoRE', S=r['S_mix'], S_err=r['S_mix_err'], n_seed=1, sd=None,
               S_H=SH, S_H_err=SHe, ret=r['S_mix'] / SH, ret_err=r['S_mix'] / SH * math.hypot(r['S_mix_err'] / r['S_mix'], SHe / SH),
               dim=(a or {}).get('dim', r.get('dim')), topo=(a or {}).get('topo'), metal=(a or {}).get('metal'), PLD=(a or {}).get('PLD'),
               probe=(a or {}).get('probe_convention'), fcz=(a or {}).get('formal_charge_nonzero'), src=src, minutes=r.get('minutes'), N_super=r.get('N_super'))
    if n in seen:   # 같은 물질 두 실행 → 일치 검사, 1단계 값을 표에
        o = seen[n]; d = row['S'] - o['S']; u = math.hypot(row['S_err'], o['S_err'])
        notes.append(f"일치 검사 {n}: {src} {row['S']:.1f} ± {row['S_err']:.1f} 대 {o['src']} {o['S']:.1f} ± {o['S_err']:.1f} → 차 {d:+.1f} = {d / u:+.2f} 단위 → {'같은 결과(≤ 1.5)' if abs(d) <= 1.5 * u else '⚠ 1.5 단위 밖'}")
        if src.startswith('coremix'):
            rows.remove(o); rows.append(row); seen[n] = row
        return
    seen[n] = row; rows.append(row)
tj = rows_of(J(os.path.join(Z, 'results_tj1_mix_laptop.json'))) + rows_of(J(os.path.join(Z, 'results_tj1_mix_laptop_add11.json')))
for r in tj:
    if r.get('group') != '우리': add_core(r, 'T-J1′')
cm_path = os.path.join(Z, 'results_coremix_s60_hkhome.json')
n_cm = 0
if os.path.exists(cm_path):
    for r in rows_of(J(cm_path)):
        add_core(r, 'coremix 1단계'); n_cm += 1 if r.get('status') == 'ok' else 0
# ---- 우리 행
def seeds(files, pick=None):
    v = []
    for f in files:
        for r in rows_of(J(f)):
            if r.get('status') == 'ok' and r.get('S_mix') is not None and (pick is None or pick(r)): v.append((r['S_mix'], r['S_mix_err']))
    return v
def ours(label, name, v, SH, SHe, dim=3, extra=''):
    m = sum(x for x, _ in v) / len(v); e = sum(e for _, e in v) / len(v) / math.sqrt(len(v)); sd = st.stdev([x for x, _ in v]) if len(v) > 1 else None
    rows.append(dict(name=name, label=label, type=('모체' if '모체' in label else '설계'), S=m, S_err=e, n_seed=len(v), sd=sd, S_H=SH, S_H_err=SHe,
                     ret=m / SH, ret_err=m / SH * math.hypot(e / m, SHe / SH), dim=dim, topo=None, metal=None, PLD=None, probe=False, fcz=None, src=extra))
def widom_on(path):
    for r in rows_of(J(path)):
        if r.get('charges') == 'on' and r.get('status_CO2') == 'ok' and r.get('status_N2') == 'ok': return r
KO = {'cn': '−CN', 'br': '−Br', 'cl': '−Cl', 'ch3': '−CH₃', 'c2h5': '−C₂H₅'}
for tag in ('cn', 'br', 'cl', 'ch3', 'c2h5'):
    w = widom_on(glob.glob(os.path.join(Z, f'results_magi5_e3_e24i_{tag}_open_widom_*.json'))[0])
    SH, SHe = sel_err(w['KH_CO2'], w['KH_CO2_err'], w['KH_N2'], w['KH_N2_err'])
    v = seeds(sorted(glob.glob(os.path.join(Z, f'results_e24i_e24i_{tag}_open_mix_*.json'))))
    ours(f'Zn(bib)(bdtdc) 열린 자리 {KO[tag]}', f'e24i_{tag}_open', v, SH, SHe, extra=f'{len(v)}씨앗 · 우리 앞단')
w = widom_on(os.path.join(Z, 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json')); SH, SHe = sel_err(w['KH_CO2'], w['KH_CO2_err'], w['KH_N2'], w['KH_N2_err'])
ours('Zn(bib)(bdtdc) 모체(형판, 우리 앞단)', 'e22_parent', seeds([os.path.join(Z, 'results_e23_mix_desktop.json')], lambda r: r['name'].startswith('e22_parent')), SH, SHe, extra='3씨앗 · 우리 앞단')
v3 = {r['name']: r for r in rows_of(J(os.path.join(Z, 'results_v3.json')))}; v4 = {r['name']: r for r in rows_of(J(os.path.join(Z, 'results_v4mix.json')))}
ours('ZIF-69 모체', 'base', seeds([os.path.join(Z, 'results_tj1_mix_laptop.json')], lambda r: r['name'] == 'base'), v3['base']['selectivity'], v3['base']['selectivity_err'], extra='1씨앗(T-J1′)')
# ZIF-69 셋: E-23 §1 (6실현 평균 · ±̄/√n · 배치 SD) — 등록 표 값 그대로
for nm, lab, m, e, sd, src in [('mslm050', 'ZIF-69 −SO₂CH₃ 50 %', 39.71, 0.38, 3.39, v3), ('saIm050', 'ZIF-69 −SO₃H 50 %', 38.80, 0.29, 2.66, v3), ('sa50nb50', 'ZIF-69 −SO₃H 50 % + −NO₂ 50 %', 38.05, 0.31, 5.07, v4)]:
    SH, SHe = src[nm]['selectivity'], src[nm]['selectivity_err']
    rows.append(dict(name=nm, label=lab, type='설계', S=m, S_err=e, n_seed=6, sd=sd, S_H=SH, S_H_err=SHe, ret=m / SH, ret_err=m / SH * math.hypot(e / m, SHe / SH), dim=3, topo=None, metal=None, PLD=None, probe=False, fcz=None, src='E-23 §1 6실현(배치 SD 병기)'))
# ---- 관문·분류
main = [r for r in rows if not r.get('probe') and r.get('fcz') is not True and r.get('dim') == 3]
side = [r for r in rows if r not in main]
groups, msg = rank(main, 'S', 'S_err')
pos = 0
for gi, g in enumerate(groups, 1):
    for r in g: pos += 1; r['cl'] = gi; r['pos'] = pos
core3 = [r for r in main if r['type'] == 'CoRE']
def sep(r, ref):
    up = dn = tie = 0
    for c in ref:
        if c is r: continue
        u = 1.5 * math.hypot(r['S_err'], c['S_err']); d = c['S'] - r['S']
        if d >= u: up += 1
        elif d <= -u: dn += 1
        else: tie += 1
    return up, tie, dn
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
def f1(x, e): return f"{x:.1f} ± {e:.1f}"
L = [f"# S_mix 축 3D 순위표 — CoRE 기존 물질(CoRE 앞단, 1씨앗) + 우리 모체·설계(우리 앞단, 3~6씨앗) ({now}, HKHOME)\n",
     f"등록 `COREMIX_REGISTRATION_20260930.md` §3. 자료: 1단계 `results_coremix_s60_hkhome.json` **{n_cm}/21 완주** + T-J1′ CoRE 6 + 우리 9. 스크립트 `final_ranking_smix.py`. 축 = 작동점 선택도 S_mix(CO₂/N₂ 0.15/0.85 · 1 bar · 298 K · 5,000+15,000). **{msg}**; 덩어리 안 동률.\n",
     "## G. S_mix 순위 — 3D · 탐침/짝이온 관문 통과 행 전부\n",
     "| # | 덩어리 | 물질 | 부류 | 씨앗 | S_mix ± | 씨앗 SD | S_Henry ± | 유지비 S_mix/S_Henry ± | 위상 · 금속 | CoRE 3D 행 중 1.5 단위 위/구별 불가/아래 |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in sorted(main, key=lambda r: r['pos']):
    up, tie, dn = sep(r, core3)
    L.append(f"| {r['pos']} | **{r['cl']}** | {r['label']} | {r['type']} | {r['n_seed']} | **{f1(r['S'], r['S_err'])}** | {'' if r['sd'] is None else f'{r['sd']:.1f}'} | {f1(r['S_H'], r['S_H_err'])} | {r['ret']:.2f} ± {r['ret_err']:.2f} | {(r.get('topo') or '') + (' · ' + r['metal'] if r.get('metal') else '')} | {up} / {tie} / {dn} |")
L.append("\n## G′. 표 밖 행(2D · 탐침 규약값 · 짝이온 삭제) — 참고\n")
L.append("| 물질 | S_mix ± | S_Henry | 유지비 | 이유 |"); L.append("|---|---|---|---|---|")
for r in sorted(side, key=lambda r: -r['S']):
    why = ('2D' if r.get('dim') == 2 else '') + (' 탐침 규약값' if r.get('probe') else '') + (' 짝이온 삭제' if r.get('fcz') else '')
    L.append(f"| {r['label']} | {f1(r['S'], r['S_err'])} | {r['S_H']:.1f} | {r['ret']:.2f} | {why.strip()} |")
L.append("\n## 일치 검사 · 예측 대조\n")
for n_ in notes: L.append(f"- {n_}")
rets = sorted(r['ret'] for r in core3)
if rets: L.append(f"- CoRE 3D 유지비: 중앙값 **{st.median(rets):.2f}**(1단계 21행만 {st.median([r['ret'] for r in core3 if r['src'].startswith('coremix')]):.2f}), 범위 {rets[0]:.2f}~{rets[-1]:.2f} (n = {len(rets)}) — 등록 예측 ≈ 0.9.")
cn = next(r for r in main if r['name'] == 'e24i_cn_open'); above = [r['label'] for r in core3 if r['S'] - cn['S'] >= 1.5 * math.hypot(r['S_err'], cn['S_err'])]
L.append(f"- −CN(141.5)보다 1.5 단위 위인 CoRE 3D 행: **{len(above)}** {above} — 등록 예측 0~1.")
par = next(r for r in main if r['name'] == 'e22_parent'); near = [(r['label'], round(r['S'], 1)) for r in core3 if abs(r['S'] - par['S']) < 1.5 * math.hypot(r['S_err'], par['S_err'])]
L.append(f"- 형판 모체(75.4)와 1.5 단위 안(2단계 +2씨앗 후보): {near}")
L.append("\n## 읽는 법\n- CoRE 행은 1씨앗(± = RASPA 95 % CI), 우리 행은 3~6씨앗(± = ±̄/√n, 씨앗 SD 병기). 자가 다르므로 CoRE 행 사이 덩어리는 넓게 읽을 것.\n- 앞단 차이(CoRE 배포 기하 대 우리 GFN-FF 이완)는 `FINAL_RANKING_20260930.md` F절 그대로(같은 물질 비 0.62~0.98) — 우리 행 자리는 보수적 하한.\n- 유지비 > 1 은 작동점에서 선택도가 오르는 골격(CO₂ 협동 흡착 또는 N₂ 밀려남, 해석 미확인).")
open(os.path.join(HERE, 'FINAL_RANKING_SMIX_20260930.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(f"coremix ok {n_cm}/21 · main rows {len(main)} · {msg}")
for r in sorted(main, key=lambda r: r['pos']): print(f"  {r['pos']:>2} c{r['cl']:<2} {r['label']:<40} {r['S']:7.1f} ± {r['S_err']:4.1f}  ret {r['ret']:.2f}  {r['type']}")
for n_ in notes: print(' ', n_)
