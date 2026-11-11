# -*- coding: utf-8 -*-
"""등록 L (L-0) — `e24k_me37_open` · `e24k_me37_100` 이완본의 관문 (0a)(0b) + CIF 실측. 등록 `ASSIGN_DURABILITY_JK_20261111.md` §L ·
`ASSIGN_NOON_20261112.md` §1-1 · §L 보완.
측정은 `e24j_measure.py`(#5) · `znbdt_no2_measure.py`(#3)와 같은 코드 — contacts(이종–H 최소) · 골격 변위(빌드본 원자를 모체 X선 원자와 0.3 Å 로 짝지은 뒤
이완본의 같은 원소 최근접까지) · `clash_gate.check`(51f18eda · 모체 위상을 물려받는 판 · 무수정 호출).
**L 의 등록 문턱**(§L · NOON §L "L-0 판정 문턱은 §L 그대로"): (0a) 골격 최대 변위 ≤ 1.0 Å · (0b) 최소 여유 ≥ −0.4 Å(Bondi · clash_gate).
  E-24i 식 (0a) 의 앞 절반(이종 원자–H ≥ 1.8 Å)은 L 등록에 없으므로 **재서 적기만** 함(`min_heteroatom_H` · `gate0a_e24i_style_pass`).
  L-1 로 가는 표지는 `gate_all_pass`(주 구조 `e24k_me37_open`) 하나 — 빌더 표지 통과 · 이완 CIF 있음 · (0a) · (0b) · 짝짓기 · 위상이 모두 참일 때만.
덧붙인 안전 표지(§0 "실패가 결과처럼 보이는 것"): clash_gate 가 센 치환 원자 수 = 메틸 원자 수(아니면 골격 원자가 0.8 Å 넘게 움직여 치환기로 잡힌 것 → (0b) None) ·
  이완 뒤 결합 그래프에서 메틸 C 마다 이웃 = C 하나 + H 셋 · 링커 조성 그대로 · 성분 수(check_substituent_clash).
CIF 실측(이완 전 · 뒤): 메틸 C–자기 카복실레이트 비배위 O · 배위 O · 가장 가까운 Zn · 카복실레이트 비틀림(티오펜 평면 대 O–C–O 평면) · Zn–O · Zn–N 범위 ·
  메틸(C · H)에서 가장 가까운 비결합 원자. 자리는 번호가 아니라 결합 그래프로 다시 찾음(이완본은 원소별로 정렬돼 번호가 바뀜).
실행: czeromof 파이썬 — 21_ZIF69_MTV 에서 `python e24k_gate.py` → results_e24k_me37_gate_hkhome.json. 판정 없음(표지만).
"""
import collections
import hashlib
import json
import math
import os
import sys
import time

import numpy as np
from ase.data import covalent_radii
from ase.geometry import find_mic
from ase.io import read
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.chdir(HERE)                                   # clash_gate.PARENT 가 상대 경로
import clash_gate                                # noqa: E402
import check_substituent_clash as CK             # noqa: E402

JOBS = {'e24k_me37_open': ('e24k_candidates/E24k_ZnDia_Me37_open.cif', 'relax_tnf/e24k_me37_open_relaxed.cif', 4, 'E24k_ZnDia_Me37_open'),
        'e24k_me37_100': ('e24k_candidates/E24k_ZnDia_Me37_100.cif', 'relax_tnf/e24k_me37_100_relaxed.cif', 8, 'E24k_ZnDia_Me37_100')}
HET_H = ('H···O', 'H···N', 'F···H', 'Cl···H', 'H···S', 'Br···H')
OUT = 'results_e24k_me37_gate_hkhome.json'
TH_DISP, TH_MARGIN = 1.0, -0.4


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j):
        G[int(x)].add(int(y))
    return G


def contacts(a, G):
    ii, jj, dd = neighbor_list('ijd', a, 3.6); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]):
            continue
        if y in ({x} | G[x] | {w for v in G[x] for w in G[v]}):
            continue
        p = '···'.join(sorted((s[x], s[y])))
        if p not in best or d < best[p][0]:
            best[p] = (round(float(d), 3), f'{s[x]}{x}', f'{s[y]}{y}')
    return best


def comps(a, G):
    s = a.get_chemical_symbols(); seen, out = set(), []
    for k in range(len(a)):
        if k in seen or s[k] == 'Zn':
            continue
        c, st = set(), [k]
        while st:
            u = st.pop()
            if u in c:
                continue
            c.add(u); st += [w for w in G[u] if s[w] != 'Zn' and w not in c]
        seen |= c; out.append(c)
    return out


def facts(a):
    """결합 그래프로 메틸 · 카복실레이트 · Zn 둘레를 다시 찾아 잼."""
    s = a.get_chemical_symbols(); G = graph(a)
    d = lambda i, j: float(a.get_distance(i, j, mic=True))
    v = lambda i, j: a.get_distance(i, j, mic=True, vector=True)
    zn = [k for k in range(len(a)) if s[k] == 'Zn']
    ii, jj, dd = neighbor_list('ijd', a, 3.6)
    methyl, twists = [], []
    for c in range(len(a)):
        if s[c] != 'C' or sum(s[m] == 'O' for m in G[c]) != 2:
            continue
        os_ = [m for m in G[c] if s[m] == 'O']
        ca = [m for m in G[c] if s[m] == 'C']
        if len(ca) != 1:
            continue
        ca = ca[0]
        sn = [m for m in G[ca] if s[m] == 'S']; cb = [m for m in G[ca] if s[m] == 'C' and m != c]
        if len(sn) != 1 or len(cb) != 1:
            continue
        cb = cb[0]
        n1 = np.cross(v(ca, cb), v(ca, sn[0])); n1 /= np.linalg.norm(n1)
        n2 = np.cross(v(c, os_[0]), v(c, os_[1])); n2 /= np.linalg.norm(n2)
        tw = math.degrees(math.acos(min(1.0, abs(float(n1.dot(n2))))))
        ofree = [m for m in os_ if not any(s[w] == 'Zn' for w in G[m])]
        ocoord = [m for m in os_ if any(s[w] == 'Zn' for w in G[m])]
        me = [m for m in G[cb] if s[m] == 'C' and m != ca and sum(s[w] == 'H' for w in G[m]) == 3]
        row = {'carboxyl_C': c, 'C2': ca, 'C3': cb, 'twist_deg': tw, 'n_O_free': len(ofree), 'n_O_coord': len(ocoord), 'has_methyl': bool(me)}
        twists.append(row)
        for m in me:
            grp = {m} | {w for w in G[m] if s[w] == 'H'}
            near = sorted((float(q), f'{s[x]}{x}···{s[y]}{y}') for x, y, q in zip(ii, jj, dd)
                          if x in grp and y not in grp and y != cb and y not in G[cb])[:3]
            methyl.append({'methyl_C': m, 'attached_ring_C': cb, 'neighbors': sorted(s[w] for w in G[m]),
                           'neighbors_ok': sorted(s[w] for w in G[m]) == ['C', 'H', 'H', 'H'],
                           'd_methylC_ringC_A': d(m, cb), 'd_methylC_own_O_free_A': d(m, ofree[0]) if len(ofree) == 1 else None,
                           'd_methylC_own_O_coord_A': d(m, ocoord[0]) if len(ocoord) == 1 else None,
                           'd_methylC_nearest_Zn_A': min(d(m, k) for k in zn), 'carboxylate_twist_deg': tw,
                           'margin_methylC_own_O_free_A': (d(m, ofree[0]) - (clash_gate.BONDI['C'] + clash_gate.BONDI['O'])) if len(ofree) == 1 else None,
                           'nearest_nonbonded_to_methyl(C · H)': [[round(q, 3), n] for q, n in near]})
    zo = sorted(d(k, m) for k in zn for m in G[k] if s[m] == 'O'); znn = sorted(d(k, m) for k in zn for m in G[k] if s[m] == 'N')
    link = collections.Counter(str(dict(sorted(collections.Counter(s[k] for k in c).items()))) for c in comps(a, G) if 'S' in {s[k] for k in c})
    return {'n_atoms': len(a), 'formula': a.get_chemical_formula(), 'methyl': methyl, 'n_methyl': len(methyl),
            'methyl_neighbors_ok': all(m['neighbors_ok'] for m in methyl) if methyl else None,
            'carboxylate_twist_deg': {'with_methyl': sorted(round(t['twist_deg'], 2) for t in twists if t['has_methyl']),
                                      'without_methyl': sorted(round(t['twist_deg'], 2) for t in twists if not t['has_methyl'])},
            'n_carboxylate': len(twists), 'Zn_O_A': [zo[0], zo[-1], len(zo)] if zo else None, 'Zn_N_A': [znn[0], znn[-1], len(znn)] if znn else None,
            'Zn_coordination': sorted(collections.Counter(tuple(sorted(s[m] for m in G[k])) for k in zn).items(), key=str).__repr__(),
            'linker_compositions': dict(link)}


def measure(tag, B0, B1, nme, b, relax, par, P):
    """한 구조의 관문 · 실측 행. b = 빌더 기록 행(builder_markers_ok · clash_check)·relax = 이완 기록 dict(tag → 행)."""
    row = {'build': B0, 'build_md5': md5(B0), 'relaxed': B1, 'n_methyl_expected': nme, 'builder_markers_ok': b['builder_markers_ok'],
           'builder_clash_check_pass': b['clash_check']['pass'], 'before': facts(read(B0)),
           'relax_record': {k: relax.get(tag, {}).get(k) for k in ('error', 'steps', 'minutes', 'fmax_reached', 'wrote_cif', 'cell_moved', 'dmin_before', 'dmin_after')}}
    if not os.path.exists(B1):
        row.update(relaxed_exists=False, gate0a_pass=None, gate0b_pass=None, gate_all_pass=False,
                   why='이완 CIF 없음(이완 실패 또는 미실행) — 관문 값 None(탈락과 다름 · 다만 L-1 로는 안 감)')
        print(f"{tag}: 이완 CIF 없음 · 이완 기록 {row['relax_record']}", flush=True)
        return row
    a0, a1 = read(B0), read(B1)
    row.update(relaxed_exists=True, relaxed_md5=md5(B1), n_atoms_equal=len(a0) == len(a1),
               cell_max_diff_A=float(np.abs(np.array(a0.cell) - np.array(a1.cell)).max()))
    X0, P1 = a0.get_positions(), a1.get_positions(); dmax, nfw, worst = 0.0, 0, None
    for k in range(len(a0)):
        _, dl = find_mic(P - X0[k], a0.cell, pbc=True); j = int(np.argmin(dl))
        if dl[j] < 0.3 and par[j].symbol == a0[k].symbol:
            nfw += 1; _, d1 = find_mic(P1 - X0[k], a0.cell, pbc=True)
            dk = min(d1[m] for m in range(len(a1)) if a1[m].symbol == a0[k].symbol)
            if dk > dmax:
                dmax, worst = float(dk), f'{a0[k].symbol}{k}'
    G = graph(a1); c = contacts(a1, G)
    het = sorted((v[0], p, v[1], v[2]) for p, v in c.items() if p in HET_H)
    hh = het[0] if het else None
    g = clash_gate.check(B1)
    n_sub_expected = nme * 4
    mapping_ok = g['n_sub_atoms'] == n_sub_expected
    after = facts(a1)
    topo_ok = bool(after['n_methyl'] == nme and after['methyl_neighbors_ok'] and after['linker_compositions'] == row['before']['linker_compositions'])
    ck = CK.check(B1)
    ok_a = bool(dmax <= TH_DISP)
    ok_a_e24i = bool(ok_a and hh is not None and hh[0] >= 1.8)
    ok_b = (bool(g['min_margin_A'] >= TH_MARGIN) if mapping_ok else None)
    row.update(n_framework_matched=nfw, max_framework_disp_A=round(dmax, 3), max_framework_disp_atom=worst, min_heteroatom_H=hh,
               gate0a_pass=ok_a, gate0a_e24i_style_pass=ok_a_e24i, gate0b=g, n_sub_atoms_expected=n_sub_expected, gate0b_mapping_ok=mapping_ok,
               gate0b_pass=ok_b, gate0b_pass_clash_gate_own=g['pass_0b'], topology_after_ok=topo_ok, clash_check_after=ck, after=after,
               contacts_after=c)
    row['gate_all_pass'] = bool(row['builder_markers_ok'] and ok_a and ok_b is True and topo_ok and row['n_atoms_equal'] and row['cell_max_diff_A'] < 1e-6)
    print(f"{tag}: 빌더 표지 {row['builder_markers_ok']} · 골격 변위 {dmax:.3f} Å({worst} · 짝 {nfw}) (0a) {'통과' if ok_a else '탈락'} | 이종–H 최소 {hh[0] if hh else None} {hh[1] if hh else ''} "
          f"(E-24i 식 (0a) {'통과' if ok_a_e24i else '탈락'}) | (0b) 최소 여유 {g['min_margin_A']:+.3f} {g['worst_pair']} 충돌 짝 {g['n_clash_pairs']} 치환 원자 {g['n_sub_atoms']}/{n_sub_expected} "
          f"{'통과' if ok_b else ('탈락' if ok_b is False else 'None')} | 위상 {topo_ok} · 성분 {ck['n_components']}/{ck['expected']} | 관문 전부 {row['gate_all_pass']}", flush=True)
    for m0, m1 in zip(sorted(row['before']['methyl'], key=lambda m: m['d_methylC_nearest_Zn_A']), sorted(after['methyl'], key=lambda m: m['d_methylC_nearest_Zn_A'])):
        print(f"    메틸: 자기 비배위 O {m0['d_methylC_own_O_free_A']:.3f} → {m1['d_methylC_own_O_free_A']:.3f} · Zn {m0['d_methylC_nearest_Zn_A']:.3f} → {m1['d_methylC_nearest_Zn_A']:.3f} · "
              f"비틀림 {m0['carboxylate_twist_deg']:.1f} → {m1['carboxylate_twist_deg']:.1f}° · 가장 가까운 것 {m1['nearest_nonbonded_to_methyl(C · H)'][0] if m1['nearest_nonbonded_to_methyl(C · H)'] else None}", flush=True)
    print(f"    Zn–O {row['before']['Zn_O_A']} → {after['Zn_O_A']} · Zn–N {row['before']['Zn_N_A']} → {after['Zn_N_A']} · 메틸 없는 카복실레이트 비틀림 {after['carboxylate_twist_deg']['without_methyl']}", flush=True)
    return row


def main():
    par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions()
    build = {r['name']: r for r in json.load(open('e24k_candidates/e24k_build.json', encoding='utf-8'))['rows']}
    relax = {}
    if os.path.exists('results_e24k_relax_hkhome.json'):
        relax = {r['tag']: r for r in json.load(open('results_e24k_relax_hkhome.json', encoding='utf-8'))}
    res = {}
    for tag, (B0, B1, nme, bname) in JOBS.items():
        res[tag] = measure(tag, B0, B1, nme, build[bname], relax, par, P)
    out = {'test': '등록 L (L-0) — 티오펜 3,7-메틸판 관문 (0a)(0b) + CIF 실측', 'assign': 'ASSIGN_DURABILITY_JK_20261111.md §L · ASSIGN_NOON_20261112.md §1-1 · §L',
           'machine': 'hkhome', 'made': time.strftime('%F %T'), 'script': 'e24k_gate.py', 'script_md5': md5(os.path.abspath(__file__)),
           'code': 'e24j_measure.py(#5) · znbdt_no2_measure.py(#3) 와 같은 측정 · clash_gate.check(' + md5('clash_gate.py')[:8] + ') 무수정',
           'thresholds_registered_L': {'0a_max_framework_disp_A': TH_DISP, '0b_min_margin_A': TH_MARGIN},
           'parent': 'e22_candidates/E22_ZnDia_parent.cif', 'parent_md5': md5('e22_candidates/E22_ZnDia_parent.cif'),
           'relax': 'relax_tnf.py(' + md5('relax_tnf.py')[:8] + ') GFN-FF 고정셀 · fmax 0.05 · 800단계 · xtb 스레드 1(e24k_relax_hkhome.py)',
           'rows': res, 'L1_go': bool(res['e24k_me37_open'].get('gate_all_pass')),
           'note': '기계적 사실뿐. L-1 로 갈지는 주 구조 e24k_me37_open 의 gate_all_pass 표지만으로 정함(등록 NOON §L). e24k_me37_100 은 참고.'}
    tmp = OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, OUT)
    print(f"저장 {OUT} · L-1 진행 표지 {out['L1_go']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
