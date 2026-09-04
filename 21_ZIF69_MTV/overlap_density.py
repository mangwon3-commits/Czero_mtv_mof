"""CO2/H2O 격자 겹침 적분 + T-4 피크 거리 (ASSIGN_20260905 §2-3, 덱 82afe50 등록분).

[등록된 정의 — 결과 전에 고정]
    좌표    격자 인덱스는 **슈퍼셀 분율좌표**. 접기는 분율에서, 데카르트 변환은
            `frac @ cell` (셀 **행렬**). 육방 셀에서 길이만 쓰면 10~24 A 틀린다
            (092788e 에서 analyze_density.py 를 같은 이유로 고쳤다).
    접근가능 골격 원자에서 3.0 A 초과 복셀만 (ACCESSIBLE_MIN, 기존 규약)
    정규화  각 격자를 **접근가능 복셀 위에서 총합 1**
    겹침    O = sum_v min(p_CO2[v], p_H2O[v])   (교집합, 0~1 무차원) — **판정은 이것**
            참고로 Bhattacharyya sum_v sqrt(p1*p2) 를 함께 보고(판정에 안 씀)
    주기경계 위 분율 처리로 자동. 단위 시험 T1~T3 로 확인한다.
"""
import os
import numpy as np
from ase.io import read
from scipy.spatial import cKDTree

ACCESSIBLE_MIN = 3.0


def read_vtk_grid(path):
    """RASPA STRUCTURED_POINTS VTK -> (values[nx,ny,nz], cell_lengths, dims)."""
    with open(path) as f:
        head = [f.readline() for _ in range(10)]
        cellp = [float(x) for x in head[1].split()[1:4]]
        dims = [int(x) for x in head[4].split()[1:4]]
        vals = np.fromstring(f.read(), sep='\n')
    n = dims[0] * dims[1] * dims[2]
    if vals.size < n:
        raise ValueError(f'{path}: {vals.size} < {n}')
    v = vals[:n].reshape(dims[::-1]).transpose(2, 1, 0)
    return v, np.array(cellp), np.array(dims)


def accessible_mask(atoms, dims, L_sup):
    """접근가능 복셀 마스크와 각 복셀의 데카르트 좌표. 전부 분율 기반."""
    cell = np.array(atoms.get_cell())
    L = atoms.get_cell().lengths()
    reps = np.round(L_sup / L)
    idx = np.stack(np.meshgrid(*[np.arange(d) for d in dims], indexing='ij'), -1)
    f_unit = np.mod(idx.reshape(-1, 3) / dims * reps, 1.0)
    cart = f_unit @ cell
    fpos = atoms.get_scaled_positions() % 1.0
    sh = np.array([[i, j, k] for i in (-1, 0, 1)
                   for j in (-1, 0, 1) for k in (-1, 0, 1)])
    pad = ((fpos[None] + sh[:, None]) @ cell).reshape(-1, 3)
    dmin, _ = cKDTree(pad).query(cart, k=1)
    return dmin > ACCESSIBLE_MIN, cart, dmin


def normalise(g, acc):
    """접근가능 복셀 위에서 총합 1. 그 밖은 0."""
    v = g.reshape(-1).astype(float).copy()
    # [단위 시험 T2 가 잡음] 밀도는 음수일 수 없다. RASPA 산출에는 없지만
    # 음수가 섞이면 sum min() 과 sqrt() 가 조용히 틀린 값을 낸다
    # (자기겹침이 1 을 넘고, Bhattacharyya 에 nan 이 난다). 여기서 막는다.
    neg = v < 0
    if neg.any():
        raise ValueError(f'격자에 음수 {int(neg.sum())}개 — 밀도가 아닙니다')
    v[~acc] = 0.0
    s = v.sum()
    if s <= 0:
        raise ValueError('격자 총합이 0 — 접근가능 영역에 밀도가 없습니다')
    return v / s


def overlap(p1, p2):
    """등록 지표 O = sum min(p1,p2). 참고로 Bhattacharyya 도 낸다."""
    return float(np.minimum(p1, p2).sum()), float(np.sqrt(p1 * p2).sum())


def substituent_ON(atoms):
    """T-4 의 '치환기 O/N' — **원소만으로 고르면 안 된다.**

    [2026-09-05 정의 확정, 결과 전 등록]
        ZIF-69 계열은 이미다졸레이트 N 이 Zn 에 배위한다. 그 N 이 구조당 **96개**로
        골격 전체에 깔려 있어, 원소(O,N) 전체를 쓰면 **어느 복셀이든 3 Å 안에**
        들어와 T-4 판정이 자동 통과한다(무의미해진다).

        실측 (전체 N / Zn배위 N / 니트로 N):
            base     120 / 96 / 24        nbIm025  126 / 96 / 30
            saIm050  120 / 96 / 24   (O 84 = 니트로 48 + 설폰산 36)

        정의: **치환기 O/N = 모든 O + Zn 에 배위하지 않은 N.**
        이미다졸레이트 고리에는 O 가 없으므로 O 는 전부 치환기(니트로·설폰산)이고,
        비배위 N 은 니트로 N 과 정확히 일치한다(base 24 = 니트로 24).
    """
    from ase.neighborlist import natural_cutoffs, NeighborList
    sym = np.array(atoms.get_chemical_symbols())
    nl = NeighborList(natural_cutoffs(atoms), self_interaction=False, bothways=True)
    nl.update(atoms)
    sel = np.zeros(len(atoms), bool)
    sel[sym == 'O'] = True
    for i in np.where(sym == 'N')[0]:
        nb, _ = nl.get_neighbors(i)
        if not any(sym[j] == 'Zn' for j in nb):
            sel[i] = True
    return sel


def peak_distance(atoms, g, acc, cart, sel=None):
    """T-4: 밀도 최대 피크에서 **치환기** O/N 까지 최단거리 (주기 고려).

    sel 을 안 주면 substituent_ON() 을 쓴다. 원소 목록을 그대로 쓰지 않는 이유는
    그 함수 독스트링에 있다.
    """
    v = g.reshape(-1).astype(float).copy()
    v[~acc] = -1.0
    k = int(np.argmax(v))
    cell = np.array(atoms.get_cell())
    if sel is None:
        sel = substituent_ON(atoms)
    if not sel.any():
        return None, None, k
    fpos = atoms.get_scaled_positions()[sel] % 1.0
    sh = np.array([[i, j, k2] for i in (-1, 0, 1)
                   for j in (-1, 0, 1) for k2 in (-1, 0, 1)])
    pad = ((fpos[None] + sh[:, None]) @ cell).reshape(-1, 3)
    d = np.linalg.norm(pad - cart[k], axis=1).min()
    return float(d), float(v[k]), k
