"""닫힌 상(상압)과 열린 상(1.47 GPa) 두 골격에 동일 조성을 치환해 '괄호치기(bracketing)' 쌍을 만든다.

배경:
    ZIF-8은 정적 구조 하나로는 다공성이 0으로 잡힌다(PLD 3.405 A < N2 프로브 지름 3.64 A).
    실제로는 리간드 회전(게이트 오프닝)으로 기체가 드나든다. 상압 구조와 1.47 GPa 구조
    (CCDC 739161-739168의 zf8147 블록)를 모두 모체로 써서 같은 조성의 하한/상한 쌍을 만들면,
    유연 골격 MD 없이도 게이트 오프닝의 범위를 제시할 수 있다.

    두 모체는 골격 연결성이 완전히 동일하고 리간드 배향만 다르므로, 같은 seed로
    치환하면 조성이 일치하는 쌍이 나온다.

주의:
    열린 상은 1.47 GPa에서 측정된 구조다. 치환체가 상압에서 이 배향을 취한다는 보장은
    없으며, 치환기 부피가 커질수록 게이트 오프닝 거동 자체가 달라진다. 따라서 이 쌍은
    수학적 상한/하한이 아니라 "동일 조성이 닫힌/열린 배향을 취했을 때의 시나리오"로
    해석해야 한다.
"""
import json
import os
import re
import subprocess
import tempfile

from ase.io import read

import mtv_cif_builder as mcb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '07_Bracketed_MTV')
PROBE_R = 1.82
PROBE_D = PROBE_R * 2
WORK = tempfile.mkdtemp()

PHASES = {
    'closed': ('ZIF8_mIm_only_P1.cif', 'site_map.json'),
    'open':   ('ZIF8_open_mIm_only_P1.cif', 'site_map_zif8_open.json'),
}

# 스크리닝할 조성 (mIm 잔량은 자동 계산)
COMPOSITIONS = [
    {'mIm': 1.00},
    {'mIm': 0.75, 'nIm': 0.25},
    {'mIm': 0.50, 'nIm': 0.50},
    {'mIm': 0.75, 'clIm': 0.25},
    {'mIm': 0.50, 'clIm': 0.50},
    {'mIm': 0.75, 'cnIm': 0.25},
    {'mIm': 0.50, 'nIm': 0.25, 'clIm': 0.25},
]


def zeopp(cif):
    base = os.path.join(WORK, os.path.basename(cif).replace('.cif', ''))
    lcd = pld = av = vf = 0.0
    try:
        subprocess.run(['network', '-ha', '-res', base + '.res', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        p = open(base + '.res').readline().split()
        lcd, pld = float(p[1]), float(p[2])
    except Exception:
        pass
    try:
        subprocess.run(['network', '-ha', '-vol', str(PROBE_R), str(PROBE_R), '20000',
                        base + '.vol', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        t = open(base + '.vol').read()
        m = re.search(r'AV_A\^3:\s*([0-9.eE+-]+)', t)
        v = re.search(r'AV_Volume_fraction:\s*([0-9.eE+-]+)', t)
        if m:
            av = float(m.group(1))
        if v:
            vf = float(v.group(1))
    except Exception:
        pass
    return lcd, pld, av, vf


def tag_of(comp):
    return '_'.join(f'{k}{int(v * 100):03d}' for k, v in sorted(comp.items()))


def main(seed=0):
    os.makedirs(OUT, exist_ok=True)
    rows = []
    print(f'{"조성":<30} {"상":<7} {"원자":>5} {"PLD":>7} {"AV(A^3)":>9} {"VF":>7} {"최소접촉":>8}')
    print('-' * 82)

    for comp in COMPOSITIONS:
        name = tag_of(comp)
        pair = {}
        for phase, (base_cif, site_map) in PHASES.items():
            out_cif = os.path.join(OUT, f'{name}__{phase}.cif')
            mcb.generate_mtv_cif(
                base_cif=os.path.join(HERE, base_cif),
                site_map_json=os.path.join(HERE, site_map),
                composition=comp,
                output_cif=out_cif,
                seed=seed,
            )
            a = read(out_cif)
            import numpy as np
            d = a.get_all_distances(mic=True)
            np.fill_diagonal(d, np.inf)
            lcd, pld, av, vf = zeopp(out_cif)
            print(f'{name:<30} {phase:<7} {len(a):>5} {pld:>7.3f} {av:>9.1f} {vf:>7.4f} {d.min():>8.3f}')
            pair[phase] = {'cif': os.path.basename(out_cif), 'n_atoms': len(a),
                           'LCD': lcd, 'PLD': pld, 'AV': av, 'VF': vf,
                           'min_contact': round(float(d.min()), 3)}
        rows.append({'composition': comp, 'seed': seed, 'phases': pair})
        print()

    idx = os.path.join(OUT, 'bracketed_index.json')
    with open(idx, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'[OK] 색인 저장: {idx}')
    print('\n주의: 열린 상은 1.47 GPa 실측 구조이므로 상한은 "그 배향을 취했을 때"의 시나리오다.')


if __name__ == '__main__':
    main()
