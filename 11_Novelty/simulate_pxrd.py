"""14개 괄호치기 구조 + 참조 구조의 모의 PXRD(Cu K-alpha)와 결정학 기술자를 뽑는다.

[이 스크립트가 보여줄 수 있는 것 / 없는 것]
    보여줄 수 있는 것: 치환·게이트오프닝이 회절 패턴을 어떻게 바꾸는가.
        -> 합성 시료를 실험적으로 구분하는 지표로 유효하다.
    보여줄 수 없는 것: 이 구조들이 '신규 물질'이라는 증명.
        모의 PXRD는 가정한 구조가 어떻게 보일지를 계산할 뿐,
        그 물질이 보고된 적 없음을 입증하지 않는다. 자세한 이유는 NOVELTY_NOTE.md 참조.
"""
import glob
import json
import os

import numpy as np
from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
WAVELENGTH = 'CuKa'          # 1.54184 A
TWO_THETA = (3, 40)
N_PEAKS = 8


def descriptors(s: Structure):
    """단위셀 부피, 골격 밀도, 공간군."""
    try:
        from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
        sga = SpacegroupAnalyzer(s, symprec=0.1)
        sg, sgno = sga.get_space_group_symbol(), sga.get_space_group_number()
    except Exception:
        sg, sgno = 'P1(해석실패)', 1
    return {
        'volume_A3': round(s.volume, 2),
        'density_g_cm3': round(float(s.density), 4),
        'n_sites': len(s),
        'formula': s.composition.reduced_formula,
        'spacegroup': sg,
        'spacegroup_number': sgno,
        'a': round(s.lattice.a, 4),
        'b': round(s.lattice.b, 4),
        'c': round(s.lattice.c, 4),
    }


def main():
    calc = XRDCalculator(wavelength=WAVELENGTH)
    targets = []
    for p in sorted(glob.glob(os.path.join(ROOT, '07_Bracketed_MTV', '*.cif'))):
        targets.append((os.path.basename(p).replace('.cif', ''), p, 'MTV 생성'))
    # 참조: 실험 원본 두 상
    for lbl, rel in [('REF_ZIF8_ambient', '05_MTV_Ligand_Library/ZIF8_mIm_only_P1.cif'),
                     ('REF_ZIF8_open_1.47GPa', '06_ZIF8_Sources/ZIF8_gateopen_zf8147.cif')]:
        fp = os.path.join(ROOT, rel)
        if os.path.exists(fp):
            targets.append((lbl, fp, '실험 원본(참조)'))

    rows = []
    print(f'{"구조":<32} {"공간군":<12} {"V(A^3)":>9} {"밀도":>7}  주요 2theta (deg)')
    print('-' * 104)
    for name, path, kind in targets:
        s = Structure.from_file(path)
        d = descriptors(s)
        pat = calc.get_pattern(s, two_theta_range=TWO_THETA)
        order = np.argsort(pat.y)[::-1][:N_PEAKS]
        peaks = sorted([(round(float(pat.x[i]), 3), round(float(pat.y[i]), 1)) for i in order])
        top = ' '.join(f'{x:.2f}' for x, _ in peaks[:6])
        print(f'{name:<32} {d["spacegroup"]:<12} {d["volume_A3"]:>9.1f} '
              f'{d["density_g_cm3"]:>7.3f}  {top}')
        rows.append({'name': name, 'kind': kind, **d,
                     'peaks_2theta_intensity': peaks})

    with open(os.path.join(HERE, 'pxrd_descriptors.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    # CSV
    import csv
    with open(os.path.join(HERE, 'pxrd_descriptors.csv'), 'w', newline='',
              encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['name', 'kind', 'formula', 'spacegroup', 'spacegroup_number',
                    'a', 'volume_A3', 'density_g_cm3', 'n_sites',
                    'peak1_2theta', 'peak1_I', 'peak2_2theta', 'peak2_I'])
        for r in rows:
            pk = r['peaks_2theta_intensity']
            w.writerow([r['name'], r['kind'], r['formula'], r['spacegroup'],
                        r['spacegroup_number'], r['a'], r['volume_A3'],
                        r['density_g_cm3'], r['n_sites'],
                        pk[0][0] if pk else '', pk[0][1] if pk else '',
                        pk[1][0] if len(pk) > 1 else '', pk[1][1] if len(pk) > 1 else ''])

    # 참조 대비 최저각 피크 이동량
    ref = next((r for r in rows if r['name'] == 'REF_ZIF8_ambient'), None)
    if ref:
        r0 = min(x for x, _ in ref['peaks_2theta_intensity'])
        print(f'\n참조(상압 ZIF-8) 최저각 피크 = {r0:.3f} deg 대비 이동량')
        print('-' * 60)
        for r in rows:
            if r['kind'] != 'MTV 생성':
                continue
            x0 = min(x for x, _ in r['peaks_2theta_intensity'])
            print(f'  {r["name"]:<32} {x0:7.3f}  ({x0 - r0:+.3f})')
    print(f'\n[OK] 저장: pxrd_descriptors.csv / .json')


if __name__ == '__main__':
    main()
