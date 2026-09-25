# -*- coding: utf-8 -*-
"""MAGI-005 E-28c 분석 (Junseok) — 등록 (1) 격자 CO₂ 적재 대 습윤 WC ads 3씨앗 · (2) 서술: 물 분포를 **영역**으로(단일 복셀 금지).

영역 = E-24c ① 의 막음 구(분율 좌표 · 반지름, 단위셀 기준). 격자(COMDensityProfile_*.vtk.gz) 는 초격자(1×2×3) 를 분율로 90³ 나눔 —
격자점 (i, j, k) → 초격자 분율 (i/90, j/90, k/90) → 단위셀 분율로 접어 막음 구 중심까지 최소 이미지 거리(단위셀 행렬)로 안/밖을 가름.
양: 영역 안 COM 밀도 합 / 전체 합(몫) · 영역의 격자점 비율(부피 몫 어림). 검산: CO₂ 격자의 CO₂ 막음 구 안 몫 ≈ 0 · 물 격자의 물(1.3) 막음 구 안 몫 ≈ 0.
C₂H₅ 는 물 탐침에서 통로 넷 모두 열림(CO₂ 는 둘) — "CO₂ 못 가는 통로(= CO₂ 1.65 막음 구)" 안 물의 몫을 셈. 기계적 사실뿐 — 판정은 종합자.
"""
import gzip
import json
import math
import os
import statistics as st

import numpy as np
from ase.io import read

H = '/home/mangwon/mof_project/21_ZIF69_MTV'
OUT = os.path.join(H, 'results_e28c_region_junseok.json')


def vtk(path):
    with gzip.open(path, 'rt') as f:
        lines = f.read().split('\n')
    hdr = {ln.split()[0]: ln.split()[1:] for ln in lines[:10] if ln.strip() and not ln.startswith('#')}
    dims = [int(x) for x in hdr['DIMENSIONS']]
    start = next(i for i, ln in enumerate(lines) if ln.startswith('LOOKUP_TABLE')) + 1
    v = np.array([float(x) for x in lines[start:start + dims[0] * dims[1] * dims[2]]])
    return hdr, dims, v


def spheres(path):
    t = open(path).read().split()
    n = int(t[0])
    return [(np.array([float(t[1 + 4 * i]), float(t[2 + 4 * i]), float(t[3 + 4 * i])]), float(t[4 + 4 * i])) for i in range(n)]


def inside_mask(dims, rep, cell, sph):
    nx, ny, nz = dims
    i, j, k = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing='ij')
    # VTK STRUCTURED_POINTS 순서: x 가 가장 빠름 → 평탄화는 (k, j, i) 순. 여기서는 (i, j, k) 격자를 만든 뒤 Fortran 순으로 평탄화해 맞춤.
    f = np.stack([(i / nx) * rep[0], (j / ny) * rep[1], (k / nz) * rep[2]], axis=-1) % 1.0
    m = np.zeros(f.shape[:3], dtype=bool)
    for c, r in sph:
        d = f - c
        d -= np.round(d)
        x = d @ cell
        m |= (np.linalg.norm(x, axis=-1) < r)
    return m.reshape(-1, order='F')


def main():
    uc = read(os.path.join(H, 'relax_tnf', 'e24c_c2h5_100_relaxed.cif'))
    cell = uc.cell.array
    rep = (1, 2, 3)
    d = os.path.join(H, 'water_runs_density_v3w', 'rh90_e24c_c2h5_100', 'VTK', 'System_0')
    hw, dims, w = vtk(os.path.join(d, 'COMDensityProfile_water.vtk.gz'))
    hc, dims_c, c = vtk(os.path.join(d, 'COMDensityProfile_CO2.vtk.gz'))
    assert dims == dims_c == [90, 90, 90]
    sp = {'CO2_block1.65': spheres(os.path.join(H, 'e24c_zeo_runs', 'e24c_c2h5_100', 'block1.65', 'e24c_c2h5_100_relaxed.block')),
          'water_block1.30': spheres(os.path.join(H, 'e24e_zeo', 'block1.30', 'e24c_c2h5_100_relaxed.block')),
          'N2_block1.82': spheres(os.path.join(H, 'e24c_zeo_runs', 'e24c_c2h5_100', 'block1.82', 'e24c_c2h5_100_relaxed.block'))}
    reg = {}
    for name, s in sp.items():
        m = inside_mask(dims, rep, cell, s)
        reg[name] = {'n_spheres': len(s), 'radii': [round(r, 3) for _, r in s], 'grid_fraction': float(m.mean()),
                     'water_fraction_inside': float(w[m].sum() / w.sum()) if w.sum() else None,
                     'CO2_fraction_inside': float(c[m].sum() / c.sum()) if c.sum() else None}
        if reg[name]['water_fraction_inside'] is not None and reg[name]['grid_fraction']:
            reg[name]['water_enrichment'] = reg[name]['water_fraction_inside'] / reg[name]['grid_fraction']
    # (1) 격자 CO₂ 적재 대 E-24f ads 3씨앗(C₂H₅)
    g = json.load(open(os.path.join(H, 'density_water_v3w', 'tpl_e24c_c2h5_100', 'water_results.json')))['rows']['e24c_c2h5_100']
    wc = json.load(open(os.path.join(H, 'v3w_humid_wc', 'humid_working_capacity_w2_e24f_c2h5_junseok.json')))['rows']
    ads = [(r['loadings']['ads']['CO2']['mol_per_kg'], r['loadings']['ads']['CO2']['err']) for r in wc]
    am, ae = st.mean(a for a, _ in ads), st.mean(e for _, e in ads) / math.sqrt(len(ads))
    u = (g['CO2'][0] - am) / math.hypot(g['CO2'][1], ae)
    cl = json.load(open(os.path.join(H, 'density_water_v3w', 'tpl_e24c_cl_100', 'water_results.json')))['rows']['e24c_cl_100']
    out = {'test': 'MAGI-005 E-28c 분석 — (1) 격자 CO₂ 대 습윤 WC ads · (2) 물 분포 영역', 'machine': 'junseok', 'assign': 'ASSIGN_MAGI5B §Junseok 18차',
           'grid': {'dims': dims, 'cell_parameters_supercell': hw.get('CELL_PARAMETERS'), 'rep': rep},
           '(1)_C2H5': {'grid_CO2': g['CO2'], 'grid_water': g['water'], 'wc_ads_each': ads, 'wc_ads_mean': am, 'wc_ads_mean_err': ae, 'units': u,
                        'within_1.5': abs(u) <= 1.5, 'wc_src': 'v3w_humid_wc/humid_working_capacity_w2_e24f_c2h5_junseok.json'},
           '(1)_Cl': {'grid_CO2': cl['CO2'], 'grid_water': cl['water'], 'note': 'laptop2 E-24f Cl 습윤 WC 가 아직 저장소에 없음 — 비교는 그 뒤(종합자)'},
           '(2)_C2H5_regions': reg,
           'note': '몫 = 영역 안 COM 밀도 합 / 전체 합(단위 무관). grid_fraction = 영역 안 격자점 비율(부피 몫 어림). 기계적 사실뿐 — 판정은 종합자.'}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(json.dumps(out, ensure_ascii=False, indent=1)[:2500])


if __name__ == '__main__':
    main()
