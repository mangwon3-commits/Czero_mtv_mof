"""밀도맵에서 '위치별 흡착 특성'을 정량 추출한다 -- 눈으로 보는 대신 숫자로.

ParaView로 밀도맵을 띄우면 "CO2가 여기 몰려 있다"까지는 보이지만, 그게
    (a) 단지 그 자리가 넓어서인지
    (b) 특정 작용기가 실제로 끌어당겨서인지
    (c) 그 인력이 분산력(LJ)인지 정전기인지
는 구별되지 않는다. 세 가지를 분리하는 게 이 스크립트의 목적이다.

세 가지 분석:

  [1] 접촉 선호도(enrichment) -- (a)와 (b)의 분리
      각 복셀에서 '가장 가까운 골격 원자가 어느 작용기인가'로 공간을 분할한다.
      작용기 F가 차지하는 접근가능 부피 분율 V_F/V 와 그 안에 든 CO2 분율
      N_F/N 을 비교해서
              E_F = (N_F/N) / (V_F/V)
      E>1 이면 '자리가 넓어서'가 아니라 실제로 그 작용기가 CO2를 끌어당긴
      것이다. 부피로 나누기 때문에 개수가 많은 작용기가 유리해지는 편향이
      제거된다.

  [2] 정전기 차분맵 -- (c)의 분리
      같은 골격에 대해 전하 ON/OFF 두 번 GCMC를 돌려놨으므로
              dρ(r) = ρ_on(r) - ρ_off(r)      (각각 총합 1로 정규화 후)
      LJ 항은 전하와 무관하므로 차분에서 소거된다. 남는 것은 순수하게
      '정전기가 CO2를 어디로 옮겼는가'의 공간 지도다. 이건 실험으로는
      분리할 수 없고 계산에서만 가능하다.
      작용기별로 dρ를 합산하면 '어느 작용기가 정전기로 버는가'가 나온다.

  [3] 밀도 피크의 화학적 정체
      극대점을 찾아 주변 골격 원자를 조회한다. "이 자리는 니트로 O에서
      3.1 A, 메틸 H에서 3.4 A" 식으로 결합 기하가 특정된다.

부수적으로 '벽에 붙어 있는가 공동 중앙에 떠 있는가'를 최근접 거리 분포로 낸다.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np
import networkx as nx
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '07_Bracketed_MTV')

# CO2가 물리적으로 존재할 수 있는 최소 접근 거리. 이보다 가까운 복셀은
# 골격 원자 내부이므로 부피 정규화에서 제외한다(안 그러면 V_F가 원자 부피에
# 지배되어 enrichment가 무의미해진다). 3.0 A는 대략 C-O LJ sigma 수준.
ACCESSIBLE_MIN = 3.0

# 작용기 분류 -> 보고용 한글 이름
FAMILY_KO = {
    'Zn': 'Zn 금속',
    'ring': '이미다졸 고리',
    'methyl': '메틸 (-CH3)',
    'nitro': '니트로 (-NO2)',
    'Cl': '염소 (-Cl)',
    'cyano': '시아노 (-CN)',
    'amine': '아민 (-NH2)',
    'CF3': '삼불화메틸 (-CF3)',
    'sulfo': '술폰산 (-SO3H)',
    'other': '기타',
}


def read_vtk_grid(path):
    """RASPA STRUCTURED_POINTS VTK -> (values[nx,ny,nz], cell_lengths)."""
    with open(path) as f:
        head = [f.readline() for _ in range(10)]
        cellp = [float(x) for x in head[1].split()[1:4]]
        dims = [int(x) for x in head[4].split()[1:4]]
        vals = np.fromstring(f.read(), sep='\n')
    n = dims[0] * dims[1] * dims[2]
    if vals.size < n:
        raise ValueError(f'{path}: {vals.size} < {n}')
    # VTK STRUCTURED_POINTS: x가 가장 빠르게 변한다
    v = vals[:n].reshape(dims[::-1]).transpose(2, 1, 0)
    return v, np.array(cellp), np.array(dims)


def classify_atoms(atoms):
    """골격 원자를 작용기로 분류한다. 수소는 붙어 있는 중원자를 따른다."""
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(atoms)
    G = nx.Graph()
    G.add_nodes_from(range(len(atoms)))
    for i in range(len(atoms)):
        for j in nl.get_neighbors(i)[0]:
            G.add_edge(i, int(j))
    s = atoms.get_chemical_symbols()

    fam = ['other'] * len(atoms)
    for i, sym in enumerate(s):
        nb = list(G.neighbors(i))
        nbs = [s[j] for j in nb]
        if sym == 'Zn':
            fam[i] = 'Zn'
        elif sym == 'Cl':
            fam[i] = 'Cl'
        elif sym == 'F':
            fam[i] = 'CF3'
        elif sym == 'S':
            fam[i] = 'sulfo'
        elif sym == 'O':
            fam[i] = 'nitro' if 'N' in nbs else ('sulfo' if 'S' in nbs else 'other')
        elif sym == 'N':
            if 'Zn' in nbs:
                fam[i] = 'ring'
            elif 'O' in nbs:
                fam[i] = 'nitro'
            elif len(nb) == 1 and 'C' in nbs:
                fam[i] = 'cyano'          # 말단 N = 니트릴
            elif 'H' in nbs:
                fam[i] = 'amine'
            else:
                fam[i] = 'ring'
        elif sym == 'C':
            heavy = [j for j in nb if s[j] != 'H']
            nH = sum(1 for x in nbs if x == 'H')
            if sum(1 for j in heavy if s[j] == 'N' and 'Zn' in [s[k] for k in G.neighbors(j)]) >= 1 \
                    and len(heavy) >= 2 and nH <= 1:
                fam[i] = 'ring'
            elif 'F' in nbs:
                fam[i] = 'CF3'
            elif any(s[j] == 'N' and len(list(G.neighbors(j))) == 1 for j in heavy):
                fam[i] = 'cyano'
            elif nH >= 2:
                fam[i] = 'methyl'         # -CH3 또는 -CH2- (아민 링커)
            else:
                fam[i] = 'ring'
    # 수소는 중원자 상속
    for i, sym in enumerate(s):
        if sym == 'H':
            nb = list(G.neighbors(i))
            fam[i] = fam[nb[0]] if nb else 'other'
    return np.array(fam)


def analyze(struct_cif, dir_on, dir_off, use_com=True):
    atoms = read(struct_cif)
    fam = classify_atoms(atoms)
    L_unit = atoms.get_cell().lengths()

    fn = 'COMDensityProfile_CO2.vtk' if use_com else 'DensityProfile_CO2.vtk'
    g_on, L_sup, dims = read_vtk_grid(os.path.join(dir_on, 'VTK', 'System_0', fn))
    g_off, _, _ = read_vtk_grid(os.path.join(dir_off, 'VTK', 'System_0', fn))
    if g_on.sum() <= 0 or g_off.sum() <= 0:
        return None

    # 격자 좌표 -> 단위셀로 접기 (밀도 격자는 슈퍼셀 위에 정의되어 있다)
    idx = np.stack(np.meshgrid(*[np.arange(d) for d in dims], indexing='ij'), -1)
    cart = idx / dims * L_sup                       # 슈퍼셀 직교좌표
    folded = np.mod(cart.reshape(-1, 3), L_unit)    # 단위셀로 환원 (정방정계)

    # 주기 이미지로 패딩한 KD-트리 (최근접 원자를 주기 경계 넘어서도 찾도록)
    pos = atoms.get_positions() % L_unit
    shifts = np.array([[i, j, k] for i in (-1, 0, 1)
                       for j in (-1, 0, 1) for k in (-1, 0, 1)])
    pad_pos = (pos[None] + (shifts * L_unit)[:, None]).reshape(-1, 3)
    pad_fam = np.tile(fam, len(shifts))
    tree = cKDTree(pad_pos)
    dmin, jmin = tree.query(folded, k=1)
    near_fam = pad_fam[jmin]

    # 접근가능 복셀만 사용
    acc = dmin > ACCESSIBLE_MIN
    r_on = g_on.reshape(-1) / g_on.sum()
    r_off = g_off.reshape(-1) / g_off.sum()
    d_rho = r_on - r_off

    out = {'n_voxel': int(acc.size), 'n_accessible': int(acc.sum()),
           'rho_in_accessible_pct': round(float(r_on[acc].sum()) * 100, 2)}

    # [1]+[2] 작용기별 부피분율 / CO2분율 / enrichment / 정전기 이득
    fams = sorted(set(fam.tolist()))
    Vtot = acc.sum()
    Ntot = r_on[acc].sum()
    rows = []
    for F in fams:
        m = acc & (near_fam == F)
        if m.sum() == 0:
            continue
        vfrac = m.sum() / Vtot
        nfrac = r_on[m].sum() / Ntot
        rows.append({
            'family': F, 'family_ko': FAMILY_KO.get(F, F),
            'n_atoms': int((fam == F).sum()),
            'vol_frac': round(float(vfrac), 4),
            'co2_frac': round(float(nfrac), 4),
            'enrichment': round(float(nfrac / vfrac), 3) if vfrac > 0 else None,
            # 정전기 켰을 때 이 작용기 주변에서 늘어난 CO2 분율 (전체 대비 %p)
            'delta_rho_pct': round(float(d_rho[m].sum()) * 100, 3),
        })
    out['families'] = sorted(rows, key=lambda r: -(r['enrichment'] or 0))

    # 벽에 붙는가 / 중앙에 뜨는가 -- 밀도가중 최근접거리
    w = r_on[acc]
    out['mean_wall_dist'] = round(float((dmin[acc] * w).sum() / w.sum()), 3)
    out['median_accessible_dist'] = round(float(np.median(dmin[acc])), 3)

    # [3] 밀도 피크 -> 화학적 정체
    peaks = []
    order = np.argsort(-r_on)
    taken = []
    for p in order[:40000]:
        if r_on[p] <= 0:
            break
        c = folded[p]
        if any(np.linalg.norm(
                (c - t + L_unit / 2) % L_unit - L_unit / 2) < 2.5 for t in taken):
            continue
        taken.append(c)
        near = tree.query_ball_point(c, 5.0)
        by = {}
        for j in near:
            d = float(np.linalg.norm(pad_pos[j] - c))
            f = pad_fam[j]
            if f not in by or d < by[f]:
                by[f] = d
        peaks.append({
            'rho_pct': round(float(r_on[p]) * 100, 4),
            'delta_rho_pct': round(float(d_rho[p]) * 100, 4),
            'wall_dist': round(float(dmin[p]), 2),
            'contacts': {FAMILY_KO.get(k, k): round(v, 2)
                         for k, v in sorted(by.items(), key=lambda x: x[1])},
        })
        if len(peaks) >= 6:
            break
    out['peaks'] = peaks
    return out


def main():
    dirs = [d for d in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, d))]
    pairs = {}
    for d in dirs:
        m = re.match(r'(.+)__(closed|open)__q_(on|off)$', d)
        if m:
            pairs.setdefault((m.group(1), m.group(2)), {})[m.group(3)] = d

    results = {}
    for (tag, phase), dd in sorted(pairs.items()):
        if 'on' not in dd or 'off' not in dd:
            continue
        cif = os.path.join(SRC, f'{tag}__{phase}.cif')
        if not os.path.exists(cif):
            print(f'  [skip] CIF 없음: {tag}__{phase}')
            continue
        try:
            r = analyze(cif, os.path.join(HERE, dd['on']), os.path.join(HERE, dd['off']))
        except Exception as e:
            print(f'  [fail] {tag}__{phase}: {type(e).__name__}: {e}')
            continue
        if r is None:
            print(f'  [skip] {tag}__{phase}: 밀도 0 (흡착 없음)')
            continue
        results[f'{tag}__{phase}'] = r
        print(f'  [ok] {tag}__{phase}', flush=True)

    with open(os.path.join(HERE, 'density_analysis.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ---- 보고 ----
    print('\n' + '=' * 100)
    print('[1] 접촉 선호도  E = (CO2 분율)/(부피 분율).  E>1 = 자리가 넓어서가 아니라 실제로 끌어당김')
    print('=' * 100)
    for k, r in results.items():
        print(f'\n{k}   (접근가능 복셀에 전체 CO2의 {r["rho_in_accessible_pct"]}%, '
              f'평균 벽거리 {r["mean_wall_dist"]} A)')
        print(f'  {"작용기":<20} {"원자":>5} {"부피%":>7} {"CO2%":>7} {"E":>7} {"정전기이득%p":>12}')
        for f_ in r['families']:
            print(f'  {f_["family_ko"]:<20} {f_["n_atoms"]:>5} '
                  f'{f_["vol_frac"]*100:>7.2f} {f_["co2_frac"]*100:>7.2f} '
                  f'{f_["enrichment"]:>7.2f} {f_["delta_rho_pct"]:>+12.2f}')

    print('\n' + '=' * 100)
    print('[3] 최대 밀도 자리의 화학적 정체 (구조당 상위 3개)')
    print('=' * 100)
    for k, r in results.items():
        print(f'\n{k}')
        for i, p in enumerate(r['peaks'][:3], 1):
            cs = ', '.join(f'{a} {d}A' for a, d in list(p['contacts'].items())[:4])
            print(f'  #{i} ρ={p["rho_pct"]:.3f}%  Δρ(정전기)={p["delta_rho_pct"]:+.3f}%p  '
                  f'벽거리 {p["wall_dist"]}A')
            print(f'      접촉: {cs}')
    print(f'\n[OK] density_analysis.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
