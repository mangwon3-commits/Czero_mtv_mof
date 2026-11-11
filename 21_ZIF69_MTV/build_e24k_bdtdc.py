# -*- coding: utf-8 -*-
"""등록 L (L-0) — Zn(bib)(bdtdc) 티오펜 3,7-자리(카복실레이트 바로 옆) 메틸 빌드. 등록 `ASSIGN_DURABILITY_JK_20261111.md` §L ·
`ASSIGN_NOON_20261112.md` §1-1 · §L 보완(이름 · 빌더 표지 · CIF 실측).
`build_e24i_bdtdc.py`(e98c2c87) 사본 — 바꾼 것: **자리 찾기** · 치환기는 −CH₃ 하나 · 출력 · 빌더 표지. 조각(rdkit PhCH₃) · 틀 · 비틀림 주사 · 쓰기 ·
점검 함수(`build_e24_bdtdc.checks` · `check_substituent_clash.check`)는 원판 그대로(무수정 import).
[자리 — 번호가 아니라 결합 그래프로] 카복실 C(O 둘을 이웃으로 가진 C) → 그 C 가 붙은 고리 C(C2 · 이웃이 카복실 C · S · C) →
  **C2 의 이웃 C(S 쪽이 아닌 쪽 · H 하나를 가진 C)** = 티오펜 3-자리(다른 끝은 7-자리). 셀당 8(링커당 2). 틀은 원판과 같이 그 C 의
  H 방향 · 고리 이웃 둘(C2 · 접합 C)로 잡음.
[어느 링커] 원판과 같은 고리 번호(가운데 벤젠 고리를 원자 번호 최소값 순으로 0~3) — 열린 고리 = 2 · 3(모체 4,8-H···O 4.10 Å 쪽).
  티오펜 자리는 무 Zn 결합 그래프의 같은 연결 성분(같은 bdtdc)에 든 벤젠 고리의 번호를 물려받음.
  `e24k_me37_open` = 고리 2 · 3 의 링커 둘(메틸 4) · `e24k_me37_100` = 네 링커(메틸 8).
[빌더 표지(등록 §L 보완)] 붙인 메틸 C 수 · 각 메틸 C 의 이웃 = 고리 C 하나 + H 셋 · 치환 링커 조성 C14H8O4S2 · 그 밖의 원자 좌표가 모체와 같음
  (최소상 최대 차 < 1e-6 Å) · 형판 md5. 하나라도 어긋나면 그 판은 `builder_markers_ok` = False.
[CIF 실측(이완 전)] 자리마다 메틸 C–자기 카복실레이트 비배위 O · 메틸 C–가장 가까운 Zn · 카복실레이트 비틀림(고리 평면 대 O–C–O 평면) ·
  종합자 사전 실측 방식(메틸 C 를 C–H 방향 1.50 Å 에 놓음)의 같은 두 거리도 나란히.
출력: e24k_candidates/E24k_ZnDia_Me37_{open,100}.cif(P1 · 전하 없음) + e24k_candidates/e24k_build.json. 판정 없음.
실행: czeromof 파이썬(rdkit) — 21_ZIF69_MTV 에서 `python build_e24k_bdtdc.py`
"""
import hashlib
import json
import math
import os
import sys
from collections import Counter

import networkx as nx
import numpy as np
from ase import Atoms
from ase.geometry import find_mic
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
OUTD = os.path.join(HERE, 'e24k_candidates')
KIND = 'CH3'                  # E.B.SMILES['CH3'] = 'c1ccccc1C'(E-24 · E-24i 와 같은 조각)
OPEN_RINGS = (2, 3)           # build_e24i_bdtdc.py 와 같은 번호
SRC_MD5 = '526ff364'          # core_pop_cifs/2017_Zn__dia_3_ASR_1.cif(zip 판과 같음)
SUB_LINKER = Counter({'C': 14, 'H': 8, 'O': 4, 'S': 2})


def sites37(a, G):
    """티오펜 3,7-자리. 반환: 자리 목록(ring = 같은 링커의 벤젠 고리 번호) · 벤젠 고리 수."""
    sym = a.get_chemical_symbols()
    S48, nring = B.sites(a, G)                                   # 벤젠 고리 번호는 원판 그대로
    Hz = G.subgraph([k for k in G if sym[k] != 'Zn'])
    comp = {}
    for ci, c in enumerate(nx.connected_components(Hz)):
        for k in c:
            comp[k] = ci
    ring_of = {}
    for s in S48:
        if ring_of.setdefault(comp[s['C']], s['ring']) != s['ring']:
            raise SystemExit('!! 한 링커에 벤젠 고리 번호가 둘')
    out = []
    for c in range(len(a)):
        if sym[c] != 'C' or sum(sym[m] == 'O' for m in G[c]) != 2:
            continue                                             # 카복실 C 만
        ca = [m for m in G[c] if sym[m] == 'C']
        if len(ca) != 1:
            raise SystemExit(f'!! 카복실 C{c} 의 C 이웃이 {len(ca)}개')
        ca = ca[0]
        cb = [m for m in G[ca] if sym[m] == 'C' and m != c]
        if len(cb) != 1 or sum(sym[m] == 'S' for m in G[ca]) != 1:
            raise SystemExit(f'!! 고리 C{ca} 의 이웃이 (카복실 C · S · C) 모양이 아님')
        cb = cb[0]
        hs = [m for m in G[cb] if sym[m] == 'H']
        nb = sorted(m for m in G[cb] if sym[m] == 'C')
        if len(hs) != 1 or len(nb) != 2 or comp[cb] not in ring_of:
            raise SystemExit(f'!! 자리 C{cb}: H {len(hs)} · C 이웃 {len(nb)}')
        ofree = [m for m in G[c] if sym[m] == 'O' and not any(sym[w] == 'Zn' for w in G[m])]
        ocoord = [m for m in G[c] if sym[m] == 'O' and any(sym[w] == 'Zn' for w in G[m])]
        out.append({'ring': ring_of[comp[cb]], 'C': cb, 'H': hs[0], 'nbr': nb, 'C2': ca, 'carboxyl_C': c,
                    'O_free': ofree[0] if len(ofree) == 1 else None, 'O_coord': ocoord[0] if len(ocoord) == 1 else None})
    out.sort(key=lambda s: (s['ring'], s['C']))
    return out, nring


def mic(a, i, j):
    return float(a.get_distance(i, j, mic=True))


def twist(a, s):
    """카복실레이트 비틀림: 티오펜 고리 평면(C2 · 3-C · S) 대 O–C–O 평면의 각(°)."""
    sym = a.get_chemical_symbols()
    sn = [m for m in B.graph(a)[s['C2']] if sym[m] == 'S'][0]
    v = lambda i, j: a.get_distance(i, j, mic=True, vector=True)
    n1 = np.cross(v(s['C2'], s['C']), v(s['C2'], sn)); n1 /= np.linalg.norm(n1)
    os_ = [m for m in B.graph(a)[s['carboxyl_C']] if sym[m] == 'O']
    n2 = np.cross(v(s['carboxyl_C'], os_[0]), v(s['carboxyl_C'], os_[1])); n2 /= np.linalg.norm(n2)
    return math.degrees(math.acos(min(1.0, abs(float(n1.dot(n2))))))


def site_facts(a0, s):
    """이완 전 실측 — 종합자 사전 실측과 같은 방식(메틸 C 를 C–H 방향 1.50 Å)."""
    zn = [k for k in range(len(a0)) if a0[k].symbol == 'Zn']
    ch = a0.get_distance(s['C'], s['H'], mic=True, vector=True); p = a0.positions[s['C']] + 1.50 * ch / np.linalg.norm(ch)
    d = lambda k: float(find_mic(a0.positions[k] - p, a0.cell, pbc=True)[1])
    return {'ring': s['ring'], 'site_C': s['C'], 'site_H': s['H'], 'C2': s['C2'], 'carboxyl_C': s['carboxyl_C'], 'O_free': s['O_free'], 'O_coord': s['O_coord'],
            'CH_A': mic(a0, s['C'], s['H']), 'presurvey_methylC_at_1.50A_to_own_O_free_A': d(s['O_free']) if s['O_free'] is not None else None,
            'presurvey_methylC_at_1.50A_to_nearest_Zn_A': min(d(k) for k in zn), 'carboxylate_twist_deg_parent': twist(a0, s),
            'presurvey_margin_C_O_A': (d(s['O_free']) - (1.70 + 1.52)) if s['O_free'] is not None else None}


def one(a0, G, S, chosen, name, frac, rec):
    new, th, hist, loc = B.build(a0, G, S, KIND, chosen)
    path = os.path.join(OUTD, name + '.cif'); B.write_cif(path, new)
    sym = new.get_chemical_symbols(); Gn = B.graph(new)
    n_sub = len(chosen) * len(loc); first = len(new) - n_sub
    # ---- 빌더 표지
    keep = [k for k in range(len(a0)) if k not in {s['H'] for s in chosen}]
    dmax = max(float(find_mic(new.positions[i] - a0.positions[k], a0.cell, pbc=True)[1]) for i, k in enumerate(keep))
    same_el = all(sym[i] == a0[k].symbol for i, k in enumerate(keep))
    remap = {k: i for i, k in enumerate(keep)}
    mc = [first + i * len(loc) for i in range(len(chosen))]                      # 조각의 첫 원자 = 메틸 C
    nb_ok, methyl = True, []
    for s, c in zip(chosen, mc):
        nbs = sorted(sym[m] for m in Gn[c]); ring_nb = [m for m in Gn[c] if sym[m] == 'C']
        ok = sym[c] == 'C' and nbs == ['C', 'H', 'H', 'H'] and ring_nb == [remap[s['C']]]
        nb_ok &= ok
        zn = [k for k in range(len(new)) if sym[k] == 'Zn']
        methyl.append({'ring': s['ring'], 'methyl_C': c, 'attached_ring_C': remap[s['C']], 'neighbors': nbs, 'neighbors_ok': ok,
                       'd_methylC_ringC_A': mic(new, c, remap[s['C']]),
                       'd_methylC_own_O_free_A': mic(new, c, remap[s['O_free']]) if s['O_free'] is not None else None,
                       'd_methylC_own_O_coord_A': mic(new, c, remap[s['O_coord']]) if s['O_coord'] is not None else None,
                       'd_methylC_nearest_Zn_A': min(mic(new, c, k) for k in zn),
                       'carboxylate_twist_deg': twist(new, {**s, 'C': remap[s['C']], 'C2': remap[s['C2']], 'carboxyl_C': remap[s['carboxyl_C']]}),
                       'torsion_deg': round(math.degrees(th[s['C']]), 1)})
    Hz = Gn.subgraph([k for k in Gn if sym[k] != 'Zn'])
    sub_comp = [Counter(sym[k] for k in nx.node_connected_component(Hz, c)) for c in mc]
    comp_ok = all(c == SUB_LINKER for c in sub_comp)
    link = Counter(tuple(sorted(Counter(sym[k] for k in c).items())) for c in nx.connected_components(Hz) if 'S' in {sym[k] for k in c})
    markers = {'site_rule': '카복실 C(O 둘) → 그 고리 C(C2) → C2 의 이웃 C–H(S 쪽 아님) · 번호가 아니라 결합 그래프', 'n_methyl_C': len(mc), 'n_methyl_C_expected': len(chosen),
               'methyl_neighbors_ok': bool(nb_ok), 'substituted_linker_composition_ok': bool(comp_ok),
               'linker_compositions': {str(dict(k)): v for k, v in link.items()},
               'other_atoms_max_shift_A(최소상)': dmax, 'other_atoms_same_element': bool(same_el), 'other_atoms_unchanged': bool(dmax < 1e-6 and same_el),
               'n_atoms': len(new), 'n_atoms_expected': len(a0) + len(chosen) * (len(loc) - 1)}
    ok = (len(mc) == len(chosen) and nb_ok and comp_ok and markers['other_atoms_unchanged'] and len(new) == markers['n_atoms_expected'])
    r = {'name': name, 'kind': KIND, 'fraction': frac, 'n_substituted': len(chosen), 'rings': sorted({s['ring'] for s in chosen}), 'sweeps_changed': hist,
         'fragment_local': [[e, [round(x, 4) for x in pp]] for e, pp in loc], 'builder_markers': markers, 'builder_markers_ok': bool(ok), 'methyl': methyl,
         **E.checks(new, n_sub, loc, KIND, len(chosen)), 'clash_check': B.CK.check(path), 'cif': os.path.relpath(path, HERE),
         'cif_md5': hashlib.md5(open(path, 'rb').read()).hexdigest()}
    rec['rows'].append(r)
    print(f"{name:24s} {r['formula']:26s} 표지 {'통과' if ok else '!! 어긋남'} · 메틸 C {len(mc)} · 그 밖 원자 이동 {dmax:.1e} Å · 비결합 최소 {r['nonbonded_min_A(topo>=3)']} · "
          f"치환기 {r['substituent_nonbonded_min_A']} · C–X {r['C-X_range']} · 충돌검사 {'통과' if r['clash_check']['pass'] else '탈락'} · 재주사 {hist}", flush=True)
    for m in methyl:
        print(f"    고리 {m['ring']} · 메틸 C{m['methyl_C']} · 자기 비배위 O {m['d_methylC_own_O_free_A']:.3f} · 배위 O {m['d_methylC_own_O_coord_A']:.3f} · "
              f"Zn {m['d_methylC_nearest_Zn_A']:.3f} · 카복실레이트 비틀림 {m['carboxylate_twist_deg']:.1f}° · 주사 각 {m['torsion_deg']}°", flush=True)
    return ok


def main():
    if os.path.exists(OUTD):
        raise SystemExit(f'!! {OUTD} 이미 있음 — 중단')
    m = hashlib.md5(open(B.SRC, 'rb').read()).hexdigest()
    if not m.startswith(SRC_MD5):
        raise SystemExit(f'!! 형판 md5 {m[:8]} ≠ {SRC_MD5}')
    os.makedirs(OUTD)
    a0 = read(B.SRC); a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)
    G = B.graph(a0); S, nring = sites37(a0, G)
    if nring != 4 or len(S) != 8 or Counter(s['ring'] for s in S) != Counter({0: 2, 1: 2, 2: 2, 3: 2}):
        raise SystemExit(f'!! 자리 수가 셀당 8(링커당 2)이 아님: 고리 {nring} · 자리 {len(S)}')
    rec = {'test': '등록 L (L-0) 빌드 — 티오펜 3,7-메틸(카복실레이트 옆)', 'assign': 'ASSIGN_DURABILITY_JK_20261111.md §L · ASSIGN_NOON_20261112.md §1-1 · §L',
           'builder': 'build_e24k_bdtdc.py ← build_e24i_bdtdc.py(e98c2c87) 사본 · build_e24_bdtdc.py → build_e22_bdtdc.py import(무수정)',
           'template': os.path.relpath(B.SRC, HERE), 'template_md5': m, 'seed': B.SEED, 'torsion_step_deg': B.STEP, 'open_rings': list(OPEN_RINGS),
           'sites': [site_facts(a0, s) for s in S], 'rows': [],
           'note': '기계적 사실뿐 — 판정 없음. presurvey_* 는 종합자 사전 실측(메틸 C 를 C–H 방향 1.50 Å)과 같은 방식으로 다시 잰 값.'}
    print(f'형판 {os.path.relpath(B.SRC, HERE)} md5 {m[:8]} · 3,7-자리 {len(S)} · 벤젠 고리 {nring}', flush=True)
    for f in rec['sites']:
        print(f"  고리 {f['ring']} · 자리 C{f['site_C']}(H{f['site_H']}) · 사전 실측 방식 메틸 C–자기 비배위 O {f['presurvey_methylC_at_1.50A_to_own_O_free_A']:.2f} Å · "
              f"Zn {f['presurvey_methylC_at_1.50A_to_nearest_Zn_A']:.2f} Å · 여유 {f['presurvey_margin_C_O_A']:+.2f} · 모체 카복실레이트 비틀림 {f['carboxylate_twist_deg_parent']:.1f}°", flush=True)
    ok1 = one(a0, G, S, [s for s in S if s['ring'] in OPEN_RINGS], 'E24k_ZnDia_Me37_open', 0.5, rec)
    ok2 = one(a0, G, S, S, 'E24k_ZnDia_Me37_100', 1.0, rec)
    json.dump(rec, open(os.path.join(OUTD, 'e24k_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0 if (ok1 and ok2) else 2


if __name__ == '__main__':
    sys.exit(main())
