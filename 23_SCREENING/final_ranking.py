"""최종 순위표 — CoRE 모집단(우리 자) + 문헌 앵커 + 우리 모체·설계 조성을 한 자(298 K Widom) 위에.

등록: FINAL_RANKING_REGISTRATION_20260930.md (자료 보기 전). 순위 규칙은 screen_core.rank (1.5×합성 오차 덩어리).
원본 노트북(셀 69)의 0.6/0.4 점수는 참고 열로만 재현(D5).
사용: /home/mangwon1/miniconda3/bin/python final_ranking.py
"""
import csv, glob, json, math, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); Z = os.path.join(HERE, '..', '21_ZIF69_MTV')
sys.path.insert(0, HERE)
from screen_core import rank, WIDOM_SANITY_MAX

PLD_PROBE = 3.64
def J(p): return json.load(open(p, encoding='utf-8'))
def rows_of(d): return d['rows'] if isinstance(d, dict) and 'rows' in d else d
def sel_err(kc, ec, kn, en, S): return S * math.sqrt((ec / kc) ** 2 + (en / kn) ** 2)

GROUP_KO = {'-Br': '−Br', '-CF3': '−CF₃', '-CN': '−CN', '-F': '−F', '-CH3': '−CH₃', '-SO2CH3': '−SO₂CH₃', '-NO2': '−NO₂', '-SO3H': '−SO₃H'}
MIX_KO = {'sa50nb50': '−SO₃H 50 % + −NO₂ 50 %', 'ms50nb50': '−SO₂CH₃ 50 % + −NO₂ 50 %', 'sa25nb75': '−SO₃H 25 % + −NO₂ 75 %'}
E24_KO = {'cn': '−CN', 'br': '−Br', 'cl': '−Cl', 'ch3': '−CH₃', 'c2h5': '−C₂H₅'}

def mk(name, label, typ, kc, ec, kn, en, PLD, **kw):
    S = kc / kn
    r = dict(name=name, label=label, type=typ, KH_CO2=kc, KH_CO2_err=ec, KH_N2=kn, KH_N2_err=en,
             S=S, S_err=sel_err(kc, ec, kn, en, S), PLD=PLD)
    r.update(kw); return r

rows = []
# --- CoRE 524 (우리 자)
core = rows_of(J(os.path.join(Z, 'core_pop_annotated.json')))
TEMPLATE_KEYS = ('2017[Zn][dia]3[FSR]1', '2017[Zn][dia]3[ASR]1')          # = Zn(bib)(bdtdc) 형판의 CoRE 수록본(LIT_CHECK_E24 §4-2)
E22E_KEYS = ('2014[Cu][dia]3[FSR]6', '2018[Cd][dia]3[FSR]4', '2021[Co][dia]3[FSR]1', '2021[Zn][srs]3[FSR]1', '2024[Co][pcu]3[ASR]1')
def core_label(k):
    lab = k.replace('[', ' ').replace(']', '')
    if k in TEMPLATE_KEYS: lab += ' **= Zn(bib)(bdtdc) 형판(CoRE 기하·CoRE 전하)**'
    elif k in E22E_KEYS: lab += ' (E-22e 검토 형판)'
    return lab
for c in core:
    rows.append(mk(c['key'], core_label(c['key']), 'CoRE', c['KH_CO2'], c['KH_CO2_err'], c['KH_N2'], c['KH_N2_err'], c['PLD'],
                   LCD=c.get('LCD'), dim=c.get('dim'), topo=c.get('topo'), metal=c.get('metal'), set=c.get('set'),
                   probe_convention=c.get('probe_convention'), formal_charge_nonzero=c.get('formal_charge_nonzero'), gate5=None, file=c.get('file')))
# --- ZIF-69 base + 30 치환 (results_v3) with gate5 (risk_results_v3)
risk = {r['name']: r for r in rows_of(J(os.path.join(Z, 'risk_results_v3.json')))}
for r in rows_of(J(os.path.join(Z, 'results_v3.json'))):
    if r.get('status') != 'ok': continue
    g = risk.get(r['name'], {})
    lab = 'ZIF-69 모체' if r['name'] == 'base' else f"ZIF-69 {GROUP_KO.get(r['group'], r['group'])} {int(round(r['frac'] * 100))} %"
    rows.append(mk(r['name'], lab, '모체' if r['name'] == 'base' else '설계', r['KH_CO2'], r['KH_CO2_err'], r['KH_N2'], r['KH_N2_err'], r['PLD'],
                   LCD=r.get('LCD'), gate5=g.get('pass'), LCD_drop=g.get('LCD_drop_pct'), S_stored_err=r.get('selectivity_err')))
# --- v4mix 3
risk4 = {r['name']: r for r in rows_of(J(os.path.join(Z, 'risk_results_v4mix.json')))}
for r in rows_of(J(os.path.join(Z, 'results_v4mix.json'))):
    if r.get('status') != 'ok': continue
    g = risk4.get(r['name'], {})
    rows.append(mk(r['name'], f"ZIF-69 {MIX_KO.get(r['name'], r['name'])}", '설계', r['KH_CO2'], r['KH_CO2_err'], r['KH_N2'], r['KH_N2_err'], r['PLD'],
                   LCD=r.get('LCD'), gate5=g.get('pass'), LCD_drop=g.get('LCD_drop_pct'), S_stored_err=r.get('selectivity_err')))
# --- 형판 모체 (E-22 parent) + E-24i 5
def widom_on(path):
    for r in rows_of(J(path)):
        if r.get('charges') == 'on' and r.get('status_CO2') == 'ok' and r.get('status_N2') == 'ok': return r
    raise SystemExit(f'no ON row: {path}')
g22 = J(os.path.join(Z, 'results_e22b_gate5_hkhome.json'))['rows']
p = widom_on(os.path.join(Z, 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json'))
rows.append(mk('e22_parent', 'Zn(bib)(bdtdc) 모체(형판)', '모체', p['KH_CO2'], p['KH_CO2_err'], p['KH_N2'], p['KH_N2_err'], g22['e22_parent']['before']['PLD'],
               LCD=g22['e22_parent']['before']['LCD'], gate5=g22['e22_parent']['pass'], LCD_drop=g22['e22_parent']['LCD_drop_pct'], S_stored_err=p.get('selectivity_err')))
g24 = J(os.path.join(Z, 'results_e24i_gate5_desktop-nvsrr9m.json'))['rows']
for f in sorted(glob.glob(os.path.join(Z, 'results_magi5_e3_e24i_*_open_widom_*.json'))):
    tag = os.path.basename(f).split('e24i_')[1].split('_open')[0]; key = f'e24i_{tag}_open'
    w = widom_on(f); g = g24[key]
    rows.append(mk(key, f"Zn(bib)(bdtdc) 열린 자리 {E24_KO[tag]}", '설계', w['KH_CO2'], w['KH_CO2_err'], w['KH_N2'], w['KH_N2_err'], g['before']['PLD'],
                   LCD=g['before']['LCD'], gate5=g['pass'], LCD_drop=g['LCD_drop_pct'], S_stored_err=w.get('selectivity_err')))
# --- 문헌 앵커 (선택 파일)
anch_path = os.path.join(HERE, 'anchors_20260930.json')
if os.path.exists(anch_path):
    for a in J(anch_path):
        rows.append(mk(a['name'], a['label'], '앵커', a['KH_CO2'], a['KH_CO2_err'], a['KH_N2'], a['KH_N2_err'], a.get('PLD'), source=a.get('source'), note=a.get('note'), gate5=None))
extra = J(os.path.join(HERE, 'ours_extra_20260930.json')) if os.path.exists(os.path.join(HERE, 'ours_extra_20260930.json')) else {}

# 검산: 저장된 selectivity_err 와 전파식
for r in rows:
    if r.get('S_stored_err'):
        assert abs(r['S_stored_err'] - r['S_err']) < 0.02 * r['S_err'] + 1e-9, (r['name'], r['S_stored_err'], r['S_err'])

# --- 관문
excluded = []
def gate(r):
    if not (0 < r['KH_CO2'] < WIDOM_SANITY_MAX and 0 < r['KH_N2'] < WIDOM_SANITY_MAX): return 'Widom 건전성'
    if r.get('PLD') is None: return None
    if r['PLD'] < PLD_PROBE: return f"탐침 규약값(PLD {r['PLD']:.3f} < {PLD_PROBE})"
    if r.get('formal_charge_nonzero') is True: return '짝이온 삭제(formal charge ≠ 0)'
    if r['type'] == '설계' and r.get('gate5') is False: return f"관문 ⑤ 탈락(LCD −{r.get('LCD_drop')} %)"
    return None
kept = []
for r in rows:
    why = gate(r)
    if why: r['excluded'] = why; excluded.append(r)
    else: kept.append(r)

# --- 순위 (S) · (K_H)
groups, msg = rank(kept, 'S', 'S_err')
pos = 0
for gi, g in enumerate(groups, 1):
    for r in g:
        pos += 1; r['S_cluster'] = gi; r['S_pos'] = pos
gK, msgK = rank(kept, 'KH_CO2', 'KH_CO2_err')
posK = 0
for gi, g in enumerate(gK, 1):
    for r in g:
        posK += 1; r['K_cluster'] = gi; r['K_pos'] = posK
N = len(kept)
pool = [r for r in kept if r['type'] == 'CoRE']
poolS = sorted(r['S'] for r in pool); poolK = sorted(r['KH_CO2'] for r in pool)
pool3 = sorted(r['S'] for r in pool if r.get('dim') == 3)
def sep(r, ref):
    """1.5×합성 오차 밖으로 위/아래인 CoRE 풀 행 수와 구별 안 되는 행 수 (사슬 덩어리와 달리 행별로 읽힘)."""
    up = dn = tie = 0
    for c in ref:
        u = 1.5 * math.hypot(r['S_err'], c['S_err'])
        d = c['S'] - r['S']
        if d >= u: up += 1
        elif d <= -u: dn += 1
        else: tie += 1
    return up, tie, dn
def pct(sorted_vals, x):
    if x > sorted_vals[-1]: return '풀 최대보다 위'
    n = sum(1 for v in sorted_vals if v < x); return f'{100.0 * n / len(sorted_vals):.1f} %'
# --- 원본 점수(참고): 상위 5 % 클리핑 → min-max ×100 → 0.6/0.4
def q95(vals):
    v = sorted(vals); k = 0.95 * (len(v) - 1); f = math.floor(k); c = min(f + 1, len(v) - 1); return v[f] + (v[c] - v[f]) * (k - f)
sc, cc = q95([r['S'] for r in kept]), q95([r['KH_CO2'] for r in kept])
sclip = [min(r['S'], sc) for r in kept]; cclip = [min(r['KH_CO2'], cc) for r in kept]
smin, smax, cmin, cmax = min(sclip), max(sclip), min(cclip), max(cclip)
for r, s_, c_ in zip(kept, sclip, cclip):
    r['nb_score'] = 0.6 * (s_ - smin) / (smax - smin) * 100 + 0.4 * (c_ - cmin) / (cmax - cmin) * 100
nb_sorted = sorted(kept, key=lambda r: -r['nb_score'])
for i, r in enumerate(nb_sorted, 1): r['nb_rank'] = i

# --- 출력
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
def fS(r): return f"{r['S']:.1f} ± {r['S_err']:.1f}"
def fK(r): return f"{r['KH_CO2']:.2e} ± {r['KH_CO2_err']:.1e}"
def desc(r):
    if r['type'] == 'CoRE': return f"{r.get('topo')} · {r.get('metal')} · {r.get('dim')}D · {r.get('set')}" + (' · 전하 미검사' if r.get('formal_charge_nonzero') is None else '')
    return r.get('source') or r.get('note') or ''
def ex(r):
    e = extra.get(r['name'], {})
    if not e: return ''
    parts = []
    if 'S_mix' in e: parts.append(f"S_mix {e['S_mix']}")
    if 'water_idx' in e: parts.append(f"물 {e['water_idx']}")
    if 'n_dry' in e: parts.append(f"건조 {e['n_dry']}")
    if 'wc_tsa' in e: parts.append(f"습윤 TSA {e['wc_tsa']}")
    return ' · '.join(parts)
L = []
L.append(f"# 최종 순위표 — CoRE 기존 물질 + 문헌 앵커 + 우리 모체·설계, 한 자(우리 298 K Widom) 위에 ({now}, HKHOME)\n")
L.append(f"등록 `FINAL_RANKING_REGISTRATION_20260930.md` 그대로. 스크립트 `final_ranking.py`, 전체 행 `final_ranking_20260930.csv`. **새 시뮬레이션 0건.**\n")
cnt = {}
for r in rows: cnt[r['type']] = cnt.get(r['type'], 0) + 1
cntk = {}
for r in kept: cntk[r['type']] = cntk.get(r['type'], 0) + 1
L.append(f"- 모집단 {len(rows)}행 = " + ' · '.join(f"{k} {v}" for k, v in cnt.items()) + f" → 관문 뒤 **{N}행**(" + ' · '.join(f"{k} {v}" for k, v in cntk.items()) + f") · 제외 {len(excluded)}")
L.append(f"- 축 ① 헨리 선택도 S: **{msg}** · 축 ② K_H(CO₂): {msgK}. 덩어리 번호가 순위, 덩어리 안은 동률(차이 < 1.5 × 합성 오차).")
L.append(f"- 백분위 풀 = 관문 통과 CoRE {len(pool)}종(3D 만 {len(pool3)}종). 원본 점수(0.6 S + 0.4 K_H, 상위 5 % 클리핑)는 참고 열.\n")
L.append("## A. 헨리 선택도 순위 — 상위 40행 (덩어리 = 순위)\n")
L.append("| # | 덩어리 | 이름 | 부류 | 설명 | PLD Å | S ± | K_H(CO₂) mol/kg/Pa ± | K_H 덩어리 | 원본 점수(참고) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for r in kept[:40] if False else sorted(kept, key=lambda r: r['S_pos'])[:40]:
    L.append(f"| {r['S_pos']} | **{r['S_cluster']}** | {r['label']} | {r['type']} | {desc(r)} | {r['PLD']:.2f} | {fS(r)} | {fK(r)} | {r['K_cluster']} | {r['nb_score']:.1f} (#{r['nb_rank']}) |")
L.append("\n## A′. 3차원 골격만 — 상위 20행 (CoRE dim = 3 + 우리 전부; 원본 노트북의 dimension == 3 필터에 해당)\n")
k3 = [r for r in kept if r['type'] != 'CoRE' or r.get('dim') == 3]
g3, msg3 = rank(k3, 'S', 'S_err'); p3 = 0
for gi, g in enumerate(g3, 1):
    for r in g:
        p3 += 1; r['S3_cluster'] = gi; r['S3_pos'] = p3
L.append(f"{len(k3)}행 · {msg3}\n")
L.append("| # | 덩어리 | 이름 | 부류 | 설명 | PLD Å | S ± | K_H(CO₂) ± |"); L.append("|---|---|---|---|---|---|---|---|")
for r in sorted(k3, key=lambda r: r['S3_pos'])[:20]:
    L.append(f"| {r['S3_pos']} | **{r['S3_cluster']}** | {r['label']} | {r['type']} | {desc(r)} | {r['PLD']:.2f} | {fS(r)} | {fK(r)} |")
L.append("\n## B. 우리 물질과 문헌 앵커의 자리 (전부)\n")
L.append(f"| 이름 | 부류 | 위치 / {N} | S ± | CoRE 풀 백분위(S) | 3D 풀 백분위(S) | CoRE 풀 중 1.5 단위 **위 / 구별 안 됨 / 아래** | K_H(CO₂) ± | K_H 백분위 | 병기(순위 축 아님) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for r in sorted([r for r in kept if r['type'] != 'CoRE'], key=lambda r: r['S_pos']):
    up, tie, dn = sep(r, pool); r['sep_up'], r['sep_tie'], r['sep_dn'] = up, tie, dn
    L.append(f"| {r['label']} | {r['type']} | {r['S_pos']} | {fS(r)} | {pct(poolS, r['S'])} | {pct(pool3, r['S'])} | **{up} / {tie} / {dn}** | {fK(r)} | {pct(poolK, r['KH_CO2'])} | {ex(r)} |")
L.append("\n## C. K_H(CO₂) 순위 — 상위 20행\n")
L.append("| # | 덩어리 | 이름 | 부류 | K_H(CO₂) ± | S ± | S 덩어리 |")
L.append("|---|---|---|---|---|---|---|")
for r in sorted(kept, key=lambda r: r['K_pos'])[:20]:
    L.append(f"| {r['K_pos']} | **{r['K_cluster']}** | {r['label']} | {r['type']} | {fK(r)} | {fS(r)} | {r['S_cluster']} |")
L.append("\n## D. 제외된 행\n")
L.append("| 이름 | 부류 | 이유 | S(참고) |"); L.append("|---|---|---|---|")
for r in sorted(excluded, key=lambda r: -r['S']):
    if r['type'] != 'CoRE' or r['S'] >= 60:
        L.append(f"| {r['label']} | {r['type']} | {r['excluded']} | {r['S']:.1f} |")
nco = sum(1 for r in excluded if r['type'] == 'CoRE')
L.append(f"\n(CoRE 제외 {nco}행 중 S < 60 은 표에서 생략 — CSV 에 전부 있음.)\n")
L.append("## F. 같은 물질, 두 앞단 — CoRE 행(배포 기하·CoRE 전하) 대 우리 앞단(GFN-FF 이완·우리 PACMAN)\n")
L.append("| 물질 | CoRE 행 S ± | 우리 앞단 S ± | 비(우리/CoRE) | 출처 |"); L.append("|---|---|---|---|---|")
byk = {r['name']: r for r in rows if r['type'] == 'CoRE'}
pairs = [('2017[Zn][dia]3[FSR]1', 'Zn(bib)(bdtdc) 형판', next(r for r in rows if r['name'] == 'e22_parent'), 'e22_parent')]
for k in E22E_KEYS:
    fname = (byk.get(k) or {}).get('file', '')[:-4]
    fs = glob.glob(os.path.join(Z, f'results_magi5_e3_e22e_{fname}_widom_*.json'))
    if not fs: continue
    w = widom_on(fs[0]); S = w['KH_CO2'] / w['KH_N2']
    pairs.append((k, k.replace('[', ' ').replace(']', ''), dict(S=S, S_err=sel_err(w['KH_CO2'], w['KH_CO2_err'], w['KH_N2'], w['KH_N2_err'], S)), os.path.basename(fs[0])))
ratios = []
for k, lab, ours, src in pairs:
    c = byk.get(k)
    if not c: continue
    ratios.append(ours['S'] / c['S'])
    L.append(f"| {lab} | {c['S']:.1f} ± {c['S_err']:.1f} | {ours['S']:.1f} ± {ours['S_err']:.1f} | **{ours['S'] / c['S']:.2f}** | {src} |")
ratios.sort()
L.append(f"\n비의 범위 {ratios[0]:.2f}~{ratios[-1]:.2f}, 중앙값 **{ratios[len(ratios)//2]:.2f}**(n = {len(ratios)}). 우리 앞단이 같은 물질을 **낮게** 읽는다 — 그래서 B 표의 우리 행 자리는 보수적 하한이고, CoRE 앞단으로 옮기면 대략 이 비의 역수만큼 위로 간다(물질마다 다름 · 외삽 금지).\n")
L.append("## E. 읽는 법 · 한계\n")
L.append("- 이 표의 순위 축은 **무한희석 헨리 선택도**다. 작동점(15:85 혼합, 1 bar) 선택도 S_mix 와 물 지수·습윤 WC 는 우리 조성에만 있어 병기 열로만 둔다 — CoRE 행과 그 축으로 견주지 않는다.")
L.append("- 같은 자(UFF_MOF · García-Sánchez CO₂ · PACMAN DDEC6 · 298 K Widom 15,000)에서 낸 값끼리의 순위다. 이 자는 ZIF 에서 실험 헨리 선택도를 1.6~2.1배 높게 읽는다(`MAGI5_E2_VERDICT`) — 절대값이 아니라 **자리**만 읽을 것.")
L.append("- 덩어리는 **인접 행 사이** 차이가 1.5 × 합성 오차를 넘을 때만 갈린다. 모집단이 촘촘한 중간 대역(S 20~80)은 인접 차이가 늘 작아 한 덩어리로 이어진다 — 그 안의 두 행이 '같다' 는 뜻이 아니라 **인접한 이웃과 가를 수 없다**는 뜻이다. 그래서 B 표에 행별로 'CoRE 풀 중 1.5 단위 위/구별 안 됨/아래' 를 따로 셌다 — 이 셋이 자리의 정직한 요약이다.")
L.append("- 덩어리 안은 동률이다(CLAUDE.md §2). 백분위는 '관문 통과 CoRE 풀 중 우리보다 낮은 비율' 이고 풀 정의 없이 인용하지 않는다(`COREPOP_REGISTRATION` (ㄴ)).")
L.append("- 원본 노트북 점수는 임의 가중(0.6/0.4)·클리핑이라 순위 근거로 쓰지 않는다(감사 D5). 참고 열로만 둔다.")
L.append("- CoRE 행의 `formal_charge_nonzero` 는 상위 69행만 검사됐다(나머지 '전하 미검사').")
L.append("- ⚠ **앞단(전처리)이 다르다.** CoRE 행 = CoRE 배포 기하 + CoRE 수록 PACMAN 전하. 우리 행 = GFN-FF 고정셀 이완 기하 + 우리 PACMAN 전하. 힘장·프로토콜은 같지만 기하가 다르고, 같은 물질에서 그 차이가 크다 — Zn(bib)(bdtdc) 형판 한 물질이 **87.8**(우리 이완 기하·우리 전하, `e22_parent`) · **120.5**(우리 이완 기하·CoRE 전하, `e22d_relaxgeom_coreq`) · **140.1**(CoRE 기하·우리 전하, `e22d_coregeom`) · **139.8**(CoRE 행 `2017 Zn dia3 FSR1`, CoRE 기하·CoRE 전하)로 읽힌다(`MAGI5_E22_VERDICT_20260925.md` E-22d). 그래서 **표 안에 같은 물질이 두 번 있다**(CoRE 행 2 + 우리 모체 1 — CoRE 행에 표지). 우리 설계 조성을 CoRE 앞단으로 돌리면 자리가 위로 갈 가능성이 크지만(형판 1.6배), 그 수는 없다 — 이 표의 우리 행 자리는 **보수적 하한**으로 읽을 것. 우리 설계 안의 순위(형판 → 치환체)는 같은 앞단이라 그대로다.")
open(os.path.join(HERE, 'FINAL_RANKING_20260930.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
cols = ['S_pos', 'S_cluster', 'name', 'label', 'type', 'topo', 'metal', 'dim', 'set', 'PLD', 'LCD', 'S', 'S_err', 'KH_CO2', 'KH_CO2_err', 'KH_N2', 'KH_N2_err', 'K_pos', 'K_cluster', 'nb_score', 'nb_rank', 'gate5', 'LCD_drop', 'probe_convention', 'formal_charge_nonzero', 'excluded', 'sep_up', 'sep_tie', 'sep_dn', 'S3_pos', 'S3_cluster']
with open(os.path.join(HERE, 'final_ranking_20260930.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore'); w.writeheader()
    for r in sorted(kept, key=lambda r: r['S_pos']) + sorted(excluded, key=lambda r: -r['S']): w.writerow(r)
print(f"rows {len(rows)} kept {N} excluded {len(excluded)} | {msg} | {msgK}")
for r in sorted([r for r in kept if r['type'] != 'CoRE'], key=lambda r: r['S_pos']):
    print(f"  {r['S_pos']:>3} c{r['S_cluster']:<3} {r['label']:<34} S {r['S']:7.1f} ± {r['S_err']:5.1f}  pct {pct(poolS, r['S']):>14}  K {r['KH_CO2']:.2e} c{r['K_cluster']}")
print('excluded ours:', [(r['label'], r['excluded']) for r in excluded if r['type'] != 'CoRE'])
print('top5:', [(r['S_pos'], r['label'], round(r['S'], 1)) for r in sorted(kept, key=lambda r: r['S_pos'])[:5]])
