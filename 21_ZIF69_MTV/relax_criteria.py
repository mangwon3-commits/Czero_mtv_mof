"""이완 판정 기준 — 한 군데에만 둔다.

[왜 따로 뺐나 — 2026-08-16 의 오탐]
    `relax_series_v3.py` 가 ZIF69_cf3Im075 를 "② C-C 폭 0.145, 실패" 로 찍었습니다.
    구조를 열어 보니 **구조가 아니라 검사기가 틀렸습니다.**

        방향족 C-C  168개   1.370~1.423   폭 0.0524   <- 통과였음
        C(고리)-C(F3) 18개  1.512~1.515   폭 0.0030   <- sp2-sp3 교과서값

    원소쌍만 보고 ('C','C') 를 한 통에 넣으니 화학적으로 다른 두 결합이 섞였고,
    그 사이 간격 0.09 A 가 통째로 "폭" 으로 잡혔습니다.

    사전 등록한 문구는 **"벤조 C-C 폭"** 이었습니다. 의도는 처음부터 방향족
    고리였고, 구현이 그 의도를 못 따라간 것입니다. 모체(base)에는 sp3 탄소가
    아예 없어서 그때는 구현과 의도가 우연히 일치했고, **지방족 치환기가 붙는
    순간 갈라졌습니다.** 그러니 이 수정은 기준을 무르게 하는 것이 아니라
    등록된 기준을 제대로 재는 것입니다.

    이 프로젝트에서 같은 계열의 오탐이 반복됐습니다 --
      · 검사기가 모체의 O 원자 48개를 안 세어 nbIm 전부를 결함으로 찍음
      · 충돌 검사기에 거리 조건이 빠져 정상 나이트로 기 O-O 를 114건 찍음
      · 충돌 검사기가 'Zn' 을 하드코딩해 멀쩡한 ZIF-67 9종 전부를 찍음
    **나쁜 결과를 보면 검사기부터 의심합니다.**

[구분하는 법]
    탄소의 이웃 수로 가릅니다. 방향족 고리 탄소는 3(예: N,N,H 또는 C,C,치환기),
    sp3 탄소(CF3, CH3)는 4 입니다. 둘 다 3 인 쌍만 방향족으로 셉니다.
"""
import collections

import numpy as np
from ase.neighborlist import neighbor_list

COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'Cl': 1.02, 'Zn': 1.22,
       'S': 1.05, 'F': 0.57, 'Br': 1.20, 'Co': 1.26}


def bonds(atoms):
    """원소쌍별 결합 길이. C-C 는 방향족(sp2-sp2)과 그 외를 따로 돌려준다."""
    syms = sorted(set(atoms.get_chemical_symbols()))
    cut = {(a, b): 1.25 * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j, d = neighbor_list('ijd', atoms, cut)
    s = atoms.get_chemical_symbols()
    deg = collections.Counter(i)          # 이웃 수 (수소 포함)
    out = collections.defaultdict(list)
    for a, b, dd in zip(i, j, d):
        if a >= b:
            continue
        key = tuple(sorted((s[a], s[b])))
        if key == ('C', 'C'):
            key = ('C', 'C') if (deg[a] == 3 and deg[b] == 3) else ('C', 'C_sp3')
        out[key].append(float(dd))
    return {k: np.array(v) for k, v in out.items()}


def evaluate(st0, st1, dmin1, cell_moved):
    """사전 등록한 넷 + 셀 고정 확인. st0/st1 은 bonds() 결과."""
    ch = st1.get(('C', 'H'))
    ch1 = float(np.median(ch)) if ch is not None else 0.0
    cc1 = st1.get(('C', 'C'))
    w1 = float(cc1.max() - cc1.min()) if cc1 is not None else 9.0
    cc0 = st0.get(('C', 'C'))
    w0 = float(cc0.max() - cc0.min()) if cc0 is not None else float('nan')
    zn = st1.get(('N', 'Zn'))
    sp3 = st1.get(('C', 'C_sp3'))

    ok = {
        '1_CH': ch is not None and 1.05 <= ch1 <= 1.12,
        '2_방향족CC폭': w1 < 0.08,
        '3_ZnN': zn is not None and float(zn.min()) > 1.90 and float(zn.max()) < 2.10,
        '5_최소거리': dmin1 > 0.9,
        '셀고정': cell_moved < 1e-9,
    }
    num = {
        'CH_before': float(np.median(st0[('C', 'H')])) if ('C', 'H') in st0 else None,
        'CH_after': ch1,
        'aromCC_width_before': w0,
        'aromCC_width_after': w1,
        'aromCC_n': int(len(cc1)) if cc1 is not None else 0,
        # sp3 C-C 는 판정에 쓰지 않지만, 값이 이상하면 눈에 띄어야 하므로 남깁니다.
        'sp3CC_n': int(len(sp3)) if sp3 is not None else 0,
        'sp3CC_range': [float(sp3.min()), float(sp3.max())] if sp3 is not None else None,
        'ZnN_min': float(zn.min()) if zn is not None else None,
        'ZnN_max': float(zn.max()) if zn is not None else None,
        'ZnN_pairs': int(len(zn)) if zn is not None else 0,
        'dmin': float(dmin1),
        'cell_moved': float(cell_moved),
    }
    return ok, num


def min_distance(atoms):
    d = neighbor_list('d', atoms, 1.3)
    return float(d.min()) if len(d) else float('inf')
