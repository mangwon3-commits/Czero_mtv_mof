"""T-5 — 마주보는 방향족 고리 평면 쌍 거리 분포 (DESIGN_STUDY 5-A T-5).

판정 규칙과 정의는 `ASSIGN_20260904.md` §2 D5 에 **수를 보기 전에** 등록됐습니다.
여기서 바꾸지 않습니다.

    고리    이미다졸레이트 5원 + 벤조 6원. C/N 만으로 이루어진 5·6원 고리를
            결합 그래프에서 찾는다. 중심 = 고리 원자 좌표 평균(최소상 기준),
            법선 = 고리 원자 최소제곱 평면의 법선
    마주봄  두 법선 사이 각 <= 30도
    대역    중심-중심 거리 6.5 ~ 7.0 A, **주기 경계 최소상**
    정규화  단위셀당 쌍 수
    판정    base 값이 saIm0583 앙상블(생산 + e1~e5, n=6) 평균 +- 2.776 x SEM
            **밖**이면 "차이 실재", 안이면 "차이 없음 -> 슬릿이 아니다"

⚠️ 08-04 에 주기 경계 언랩 버그로 계산 전량을 폐기한 전력이 있습니다.
`--selftest` 가 2x2x2 슈퍼셀을 만들어 **쌍 수가 정확히 8배**인지 먼저 확인합니다.

산출: t5_ring_pairs.json
"""
import argparse
import itertools
import json
import math
import os
import sys
from statistics import mean, stdev

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = 2.776
ANGLE_MAX = 30.0        # 등록: 법선 사이 각
BAND = (6.5, 7.0)       # 등록: 중심-중심 거리 대역 (A)
RCOV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'F': 0.57,
        'S': 1.05, 'Cl': 1.02, 'Zn': 1.22, 'Br': 1.20}
BOND_TOL = 1.15

ENSEMBLE = ['saIm0583'] + [f'saIm0583e{i}' for i in range(1, 6)]
CONTROL = 'base'


def bond_graph(atoms, keep=('C', 'N')):
    sym = atoms.get_chemical_symbols()
    idx = [i for i, s in enumerate(sym) if s in keep]
    pos = atoms.get_positions()
    cell = np.array(atoms.get_cell())
    inv = np.linalg.inv(cell)
    adj = {i: set() for i in idx}
    for a, b in itertools.combinations(idx, 2):
        d = min_image(pos[a] - pos[b], cell, inv)
        r = np.linalg.norm(d)
        if r < BOND_TOL * (RCOV[sym[a]] + RCOV[sym[b]]):
            adj[a].add(b)
            adj[b].add(a)
    return adj


def min_image(vec, cell, inv):
    f = vec @ inv
    f -= np.round(f)
    return f @ cell


def find_rings(adj, sizes=(5, 6)):
    """단순 고리 — 시작점을 고리 최소 인덱스로 고정해 한 번만 센다."""
    rings = set()
    for start in adj:
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if len(path) > max(sizes):
                continue
            for nb in adj[node]:
                if nb == start and len(path) in sizes:
                    rings.add(tuple(sorted(path)))
                elif nb not in path and nb > start:
                    stack.append((nb, path + [nb]))
    return [list(r) for r in sorted(rings)]


def ring_frame(atoms, ring, cell, inv):
    pos = atoms.get_positions()
    ref = pos[ring[0]]
    pts = np.array([ref + min_image(pos[i] - ref, cell, inv) for i in ring])
    c = pts.mean(axis=0)
    u, s, vt = np.linalg.svd(pts - c)
    return c, vt[2] / np.linalg.norm(vt[2])


def count_pairs(atoms, images=1):
    cell = np.array(atoms.get_cell())
    inv = np.linalg.inv(cell)
    rings = find_rings(bond_graph(atoms))
    frames = [ring_frame(atoms, r, cell, inv) for r in rings]
    n = 0
    dists = []
    shifts = [np.array([i, j, k]) @ cell
              for i in range(-images, images + 1)
              for j in range(-images, images + 1)
              for k in range(-images, images + 1)]
    for a in range(len(frames)):
        ca, na = frames[a]
        for b in range(len(frames)):
            cb, nb = frames[b]
            ang = math.degrees(math.acos(min(1.0, abs(float(np.dot(na, nb))))))
            if ang > ANGLE_MAX:
                continue
            for sh in shifts:
                if a == b and not sh.any():
                    continue
                d = float(np.linalg.norm(cb + sh - ca))
                if BAND[0] <= d <= BAND[1]:
                    n += 1
                    dists.append(d)
    return len(rings), n / 2.0, dists      # /2 — (a,b) 와 (b,a) 를 다 셌다


def load(name):
    p = os.path.join(HERE, 'charged_v3', f'{name}_DDEC6.cif')
    if not os.path.exists(p):
        return None
    return read(p)


def selftest():
    a = load(CONTROL)
    if a is None:
        sys.exit('base CIF 없음')
    nr1, n1, _ = count_pairs(a)
    nr2, n2, _ = count_pairs(a.repeat((2, 2, 2)))
    ok = abs(n2 - 8 * n1) < 1e-6 and nr2 == 8 * nr1
    print('=== 최소상 단위 시험 (08-04 언랩 버그 재발 방지) ===')
    print(f'  단위셀     고리 {nr1:>4}  대역 쌍 {n1:>8.1f}')
    print(f'  2x2x2      고리 {nr2:>4}  대역 쌍 {n2:>8.1f}   기대 {8*n1:.1f}')
    print(f'  -> {"통과" if ok else "실패 — 최소상 처리가 틀렸다"}')
    return 0 if ok else 1


def collect(name, lo=4.0, hi=9.0):
    """마주봄(<=30도) 쌍의 중심-중심 거리 목록 — 대역 필터 없이."""
    atoms = load(name)
    cell = np.array(atoms.get_cell())
    inv = np.linalg.inv(cell)
    frames = [ring_frame(atoms, r, cell, inv)
              for r in find_rings(bond_graph(atoms))]
    shifts = [np.array([i, j, k]) @ cell
              for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)]
    ds = []
    for x in range(len(frames)):
        ca, na = frames[x]
        for y in range(len(frames)):
            cb, nb = frames[y]
            ang = math.degrees(math.acos(min(1.0, abs(float(np.dot(na, nb))))))
            if ang > ANGLE_MAX:
                continue
            for sh in shifts:
                if x == y and not sh.any():
                    continue
                d = float(np.linalg.norm(cb + sh - ca))
                if lo < d < hi:
                    ds.append(d)
    return ds


def sweep():
    """[감도, 판정 아님] 등록 대역 [6.5, 7.0] 을 흔들면 어떻게 되는가."""
    names = [CONTROL] + ENSEMBLE
    ds = {n: collect(n) for n in names}
    bands = [(6.3, 7.2), (6.45, 7.0), BAND, (6.5, 7.05), (6.0, 7.5), (5.5, 8.0)]
    print('=== [감도, 판정 아님] 대역 폭 흔들기 ===')
    print(f'  {"대역":<14}{"base":>8}' + ''.join(f'{n[-4:]:>7}' for n in ENSEMBLE)
          + '   앙상블 ± / 방향')
    for lo, hi in bands:
        row = [sum(1 for d in ds[n] if lo <= d <= hi) / 2 for n in names]
        ens = row[1:]
        m, ci = mean(ens), T95 * stdev(ens) / len(ens) ** 0.5
        side = ('base 큼' if row[0] > m else 'base 작음')
        tag = '밖' if abs(row[0] - m) > ci else '안'
        mark = '  <- 등록 대역' if (lo, hi) == BAND else ''
        print(f'  [{lo}, {hi}]'.ljust(16) + f'{row[0]:>8.1f}'
              + ''.join(f'{v:>7.1f}' for v in ens)
              + f'   {m:>5.1f}±{ci:.1f} {tag} / {side}{mark}')
    print(f'\n  base 의 마주봄 거리는 이산적입니다: '
          f'{sorted({round(d, 3) for d in ds[CONTROL] if 5.5 < d < 8.0})}')
    print('  등록 대역 [6.5, 7.0] 은 그 이산값 6.455 와 7.134 **사이**에 떨어집니다.')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--sweep', action='store_true',
                    help='[감도, 판정 아님] 대역 폭을 흔들어 본다')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.sweep:
        return sweep()

    targets = [CONTROL] + ENSEMBLE
    missing = [t for t in targets if load(t) is None]
    print('=== T-5 대상 파일 ===')
    for t in targets:
        print(f'  {"O" if t not in missing else "X"} charged_v3/{t}_DDEC6.cif')
    print('  (saIm0583r1~r5 는 무작위 배치 대조군이고 관문 탈락이라 제외 — '
          'PLACEMENT_CONTROL_20260826.md 48행)')
    if missing:
        sys.exit(f'\n대상 {len(missing)}개 없음: {missing} — 추측으로 채우지 않고 멈춥니다.')
    if len(ENSEMBLE) < 6:
        sys.exit('\n앙상블 실현이 6개 미만 — 등록문대로 멈춥니다.')

    res = {}
    for t in targets:
        nr, npair, dists = count_pairs(load(t))
        res[t] = {'n_rings': nr, 'pairs_per_cell': npair,
                  'mean_dist': mean(dists) if dists else None}
        print(f'  {t:<14} 고리 {nr:>4}   대역 쌍/셀 {npair:>7.1f}')

    ens = [res[t]['pairs_per_cell'] for t in ENSEMBLE]
    m, sd = mean(ens), stdev(ens)
    ci = T95 * sd / len(ens) ** 0.5
    b = res[CONTROL]['pairs_per_cell']
    outside = abs(b - m) > ci
    verdict = ('차이 실재 — base 가 앙상블 95% CI 밖' if outside else
               '차이 없음 — saIm 의 Q_st 상승은 슬릿이 아니다 (등록문 예상)')

    print(f'\n=== 판정 (등록 규칙 그대로) ===')
    print(f'  saIm0583 앙상블 n={len(ens)}  평균 {m:.2f}  배치 SD {sd:.2f}  '
          f'± (2.776xSEM) {ci:.2f}   구간 [{m-ci:.2f}, {m+ci:.2f}]')
    print(f'  base {b:.2f}  -> {"밖" if outside else "안"}')
    print(f'  → {verdict}')
    print('  병기: base 는 단일 실현이라 자기 CI 가 없다(분모 비대칭).')

    out = {'rule': 'ASSIGN_20260904 §2 D5 (결과 전 등록)',
           'angle_max_deg': ANGLE_MAX, 'band_A': BAND, 't95': T95,
           'per': res, 'ensemble': ENSEMBLE, 'control': CONTROL,
           'ensemble_mean': m, 'ensemble_batch_sd': sd, 'ensemble_ci95': ci,
           'control_value': b, 'outside': outside, 'verdict': verdict}
    json.dump(out, open(os.path.join(HERE, 't5_ring_pairs.json'), 'w',
                        encoding='utf-8'), indent=2, ensure_ascii=False)
    print('\n-> t5_ring_pairs.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
