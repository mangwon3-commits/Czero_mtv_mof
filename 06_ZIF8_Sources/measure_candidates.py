"""이 폴더의 모든 CIF 후보에 대해 무결성 검증 + PLD/접근가능부피를 실측한다.

CCDC에서 받은 파일을 이 폴더에 넣고 실행하면, 어느 것이 게이트 열린 상인지 바로 나온다.

    conda activate czeromof
    python ~/mof_project/06_ZIF8_Sources/measure_candidates.py

판정 기준: PLD >= N2 프로브 지름(1.82*2 = 3.64 A)이면 정적 구조로도 다공성이 인식됨.
"""
import glob
import os
import re
import subprocess
import tempfile
from collections import Counter

from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_R = 1.82
PROBE_D = PROBE_R * 2
WORK = tempfile.mkdtemp()

# 비교 기준으로 현재 파이프라인이 쓰는 구조도 항상 함께 측정한다.
BASELINE = os.path.join(HERE, '..', '01_CIF_Cleaned', 'ZIF-8.cif')


def integrity_check(path):
    """404 페이지가 .cif로 저장되는 사고가 실제로 있었으므로 파싱 전에 먼저 거른다."""
    size = os.path.getsize(path)
    if size < 500:
        head = open(path, encoding='utf-8', errors='ignore').read(80).strip()
        return False, f'파일이 너무 작음({size}B): {head!r}'
    return True, f'{size}B'


def pressure_of(path):
    """CIF에 기록된 압력/온도를 뽑는다(있으면). 압력 시리즈 구분용."""
    txt = open(path, encoding='utf-8', errors='ignore').read()
    out = []
    for tag in ('_diffrn_ambient_pressure', '_cell_measurement_pressure',
                '_diffrn_ambient_temperature'):
        m = re.search(rf'{tag}\s+(\S+)', txt)
        if m:
            out.append(f'{tag.split("_")[-1]}={m.group(1)}')
    return ' '.join(out) or '-'


def zeopp(cif):
    base = os.path.join(WORK, os.path.basename(cif).replace('.cif', ''))
    lcd = pld = av = vf = 0.0
    try:
        subprocess.run(['network', '-ha', '-res', base + '.res', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        with open(base + '.res') as f:
            p = f.readline().split()
            lcd, pld = float(p[1]), float(p[2])
    except Exception:
        pass
    try:
        subprocess.run(['network', '-ha', '-vol', str(PROBE_R), str(PROBE_R), '20000',
                        base + '.vol', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        txt = open(base + '.vol').read()
        m = re.search(r'AV_A\^3:\s*([0-9.eE+-]+)', txt)
        v = re.search(r'AV_Volume_fraction:\s*([0-9.eE+-]+)', txt)
        if m:
            av = float(m.group(1))
        if v:
            vf = float(v.group(1))
    except Exception:
        pass
    return lcd, pld, av, vf


def min_contact(atoms):
    import numpy as np
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    return d.min()


targets = []
if os.path.exists(BASELINE):
    targets.append((BASELINE, '[기준] 현재 파이프라인'))
targets += [(p, '') for p in sorted(glob.glob(os.path.join(HERE, '*.cif')))]

print(f'N2 프로브 지름 = {PROBE_D:.2f} A 기준\n')
print(f'{"구조":<24} {"원자":>5} {"a(A)":>7} {"LCD":>7} {"PLD":>7} {"PLD/a":>7} '
      f'{"AV(A^3)":>9} {"최소접촉":>7}  판정')
print('-' * 108)

for path, tag in targets:
    name = os.path.basename(path).replace('.cif', '')
    ok, info = integrity_check(path)
    if not ok:
        print(f'{name:<24} !! 무결성 실패: {info}')
        continue
    try:
        a = read(path)
    except Exception as e:
        print(f'{name:<24} !! 파싱 실패: {type(e).__name__}')
        continue

    cell = a.cell.cellpar()[0]
    lcd, pld, av, vf = zeopp(path)
    mc = min_contact(a)

    if pld == 0:
        verdict = 'Zeo++ 실패'
    elif pld >= PROBE_D:
        verdict = '*** 게이트 열림 ***'
    else:
        verdict = '닫힘'
    if mc < 0.7:
        verdict += ' [원자겹침 있음!]'

    print(f'{name:<24} {len(a):>5} {cell:>7.3f} {lcd:>7.3f} {pld:>7.3f} '
          f'{pld / cell if cell else 0:>7.4f} {av:>9.1f} {mc:>7.3f}  {verdict} {tag}')
    cond = pressure_of(path)
    if cond != '-':
        print(f'{"":24} 조건: {cond} | 조성 {dict(Counter(a.get_chemical_symbols()))}')

print('\nPLD/a는 셀 크기 효과를 제거한 상대 창구 크기 — 이 값이 같이 커져야 진짜 리간드 재배향.')
