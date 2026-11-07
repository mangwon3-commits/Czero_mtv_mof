# -*- coding: utf-8 -*-
"""#5 (laptop2 몫) — 겹침 고리(0·1) 4,8-치환 −Cl · −Br 이완본의 관문 (0a)(0b). 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §2-1.
측정은 `znbdt_no2_measure.py`(#3, HKHOME)와 같은 코드입니다 — contacts · 골격 변위(모체 X선 원자와 짝지음) · `clash_gate.check`.
바꾼 것은 대상 둘과 자리별 기록(니트로 N 대신 할로젠 X)뿐입니다. 문턱: (0a) 이종–H ≥ 1.8 Å · 골격 최대 변위 ≤ 1.0 Å / (0b) 겹침 < 0.4 Å.
자리별 기록은 서술입니다: X 마다 최근접 접촉(부착 C 에서 2결합 안은 뺌 — clash_gate 제외 ②와 같은 범위) · X···O 최소 ·
그래프(공유 반지름 × 1.15)가 X 에 C 말고 다른 이웃을 붙였는지(랩탑 18:49 ⚠: 빌드본 Br···O 2.069 Å 가 결합으로 잡힘).
실행: czeromof 파이썬 — `python e24j_measure.py` (21_ZIF69_MTV 에서) → results_e24j_screen_laptop2.json"""
import collections, json, numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic
import clash_gate
JOBS = {'e24j_cl_ovl': ('e24j_candidates/e24j_cl_ovl.cif', 'relax_tnf/e24j_cl_ovl_relaxed.cif', 'Cl'),
        'e24j_br_ovl': ('e24j_candidates/e24j_br_ovl.cif', 'relax_tnf/e24j_br_ovl_relaxed.cif', 'Br')}
HET_H = ('H···O', 'H···N', 'F···H', 'Cl···H', 'H···S', 'Br···H')


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    return G


def contacts(a, G):
    ii, jj, dd = neighbor_list('ijd', a, 3.6); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]): continue
        if y in ({x} | G[x] | {w for v in G[x] for w in G[v]}): continue
        p = '···'.join(sorted((s[x], s[y])))
        if p not in best or d < best[p][0]: best[p] = (round(float(d), 3), f'{s[x]}{x}', f'{s[y]}{y}')
    return best


par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions()
res = {}
for tag, (B0, B1, X) in JOBS.items():
    a0, a1 = read(B0), read(B1); assert len(a0) == len(a1)
    X0 = a0.get_positions(); P1 = a1.get_positions(); dmax, nfw = 0.0, 0
    for k in range(len(a0)):
        _, dl = find_mic(P - X0[k], a0.cell, pbc=True); j = int(np.argmin(dl))
        if dl[j] < 0.3 and par[j].symbol == a0[k].symbol:
            nfw += 1; _, d1 = find_mic(P1 - X0[k], a0.cell, pbc=True)
            dmax = max(dmax, min(d1[m] for m in range(len(a1)) if a1[m].symbol == a0[k].symbol))
    G = graph(a1); s = a1.get_chemical_symbols(); c = contacts(a1, G)
    het = [(v[0], p, v[1], v[2]) for p, v in c.items() if p in HET_H]; hh = min(het)
    g = clash_gate.check(B1)
    ii, jj, dd = neighbor_list('ijd', a1, 3.6)
    sites = []
    for x in [n for n in range(len(a1)) if s[n] == X]:
        cs = [y for y in G[x] if s[y] == 'C']
        ring_c = cs[0] if cs else None
        # 제외 범위는 부착 C 에서 2결합 안이되, X 를 거치는 길은 쓰지 않음(X 의 거짓 이웃 O 가 제외되지 않게)
        n1 = (G[ring_c] - {x}) if ring_c is not None else set()
        excl = ({ring_c} | n1 | {w for v in n1 for w in G[v] if w != x}) if ring_c is not None else set()
        best = (9.9, None); xo = (9.9, None); w_in = (-9.9, None)
        for p_, q_, d in zip(ii, jj, dd):
            if p_ != x or q_ == x or s[q_] == 'Zn' or q_ in excl: continue
            if d < best[0]: best = (round(float(d), 3), f'{X}{x}···{s[q_]}{q_}')
            if s[q_] == 'O' and d < xo[0]: xo = (round(float(d), 3), f'{X}{x}···O{q_}')
            if s[q_] != 'H':
                m = clash_gate.BONDI[X] + clash_gate.BONDI[s[q_]] - d
                if m > w_in[0]: w_in = (round(float(m), 3), f'{X}{x}···{s[q_]}{q_} {d:.3f}')
        sites.append({'X': int(x), 'ipso_C': None if ring_c is None else int(ring_c),
                      'graph_neighbors_of_X': sorted(f'{s[y]}{y}' for y in G[x]),
                      'graph_nonC_neighbor(서술 — 랩탑 18:49 ⚠)': any(s[y] != 'C' for y in G[x]),
                      'closest_contact_any': best, 'min_X_O': xo, 'max_bondi_overlap_from_X': w_in})
    ok_a = hh[0] >= 1.8 and dmax <= 1.0
    res[tag] = {'build': B0, 'relaxed': B1, 'substituent': X, 'n_framework_matched': nfw,
                'max_framework_disp_A': round(float(dmax), 3), 'min_heteroatom_H': hh, 'gate0a_pass': ok_a,
                'gate0b': g, 'gate0b_pass': g['pass_0b'], 'gate_all_pass': ok_a and g['pass_0b'],
                'sites': sites, 'contacts_after': c}
    print(f"{tag}: 골격 변위 {dmax:.2f} Å (짝 {nfw}) | 이종–H 최소 {hh[0]} {hh[1]} | (0a) {'통과' if ok_a else '탈락'} | "
          f"(0b) 겹침 {g['min_margin_A']:+.3f} {g['worst_pair']} {'통과' if g['pass_0b'] else '탈락'}")
    for t in sites: print(f"  {X}{t['X']}: 이웃 {t['graph_neighbors_of_X']} · 최근접 {t['closest_contact_any']} · X···O {t['min_X_O']} · 최대 겹침 {t['max_bondi_overlap_from_X']}")
out = {'test': '#5 배치 민감도 — 겹침 고리(0·1) 4,8-치환 −Cl · −Br 관문 (0a)(0b) (laptop2 이완 · 측정)',
       'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §2-1', 'relax_record': 'results_e24j_relax_laptop2.json',
       'code': 'znbdt_no2_measure.py(#3) 와 같은 측정 · 같은 문턱', 'rows': res,
       'note': '판정은 종합자. 탈락이면 그 치환기는 여기서 끝(등록 §2-1).'}
json.dump(out, open('results_e24j_screen_laptop2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
