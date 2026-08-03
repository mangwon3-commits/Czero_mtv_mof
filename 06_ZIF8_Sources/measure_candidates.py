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
    """CIF에 기록된 압력/온도/R factor를 뽑는다. 압력 시리즈에서 목표 구조 식별용."""
    txt = open(path, encoding='utf-8', errors='ignore').read()
    out = []
    for tag, lab in (('_diffrn_ambient_pressure', '압력'),
                     ('_cell_measurement_pressure', '셀압력'),
                     ('_diffrn_ambient_temperature', '온도'),
                     ('_refine_ls_R_factor_gt', 'R')):
        m = re.search(rf'{tag}\s+(\S+)', txt)
        if m:
            out.append(f'{lab}={m.group(1)}')
    return ' '.join(out) or '-'


def disorder_of(path):
    """부분점유(무질서) 사이트 수를 센다.

    [중요] ASE의 CIF 리더는 _atom_site_occupancy를 무시하고 occ<1 사이트도 온전한
    원자로 전개한다. 실제로 COD의 ZIF-8들은 메틸 수소가 두 배향에 각각 occ=0.5로
    등재돼 있어 H가 화학적 정답(120개) 대신 192개로 읽힌다. 이 유령 원자는
    (a) 원자 수를 부풀리고 (b) '원자 겹침' 오경보를 만든다.

    다만 ZIF-8에서 실측해보니 이 유령 수소를 전부 제거해도 PLD가 소수점 3자리까지
    동일했다 -- 창구를 좁히는 건 메틸 H가 아니라 골격의 C/N이기 때문. 따라서 다공성
    판정 자체는 무질서 처리 방식에 둔감하다. 원자 겹침 경고 해석에만 주의하면 된다.
    """
    txt = open(path, encoding='utf-8', errors='ignore').read()
    lines = txt.split('\n')
    tags = [i for i, l in enumerate(lines) if l.strip().startswith('_atom_site_')]
    if not tags:
        return 0
    names = [lines[i].strip() for i in tags]
    try:
        col = next(i for i, n in enumerate(names) if n == '_atom_site_occupancy')
    except StopIteration:
        return 0
    partial = 0
    for l in lines[tags[-1] + 1:]:
        p = l.split()
        if len(p) <= col or l.strip().startswith(('_', '#', 'loop_')):
            if partial:
                break
            continue
        try:
            if abs(float(re.sub(r'\(.*?\)', '', p[col])) - 1.0) > 1e-3:
                partial += 1
        except ValueError:
            continue
    return partial


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
    ndis = disorder_of(path)
    comp = dict(Counter(a.get_chemical_symbols()))
    if cond != '-':
        print(f'{"":24} 조건: {cond}')
    print(f'{"":24} 조성 {comp}')
    if ndis:
        print(f'{"":24} !! 부분점유 사이트 {ndis}개 -- ASE가 occupancy를 무시하고 전개하므로 '
              f'원자 수/겹침 경고가 부풀려짐 (PLD 판정에는 영향 없음)')

print('\nPLD/a는 셀 크기 효과를 제거한 상대 창구 크기 — 이 값이 같이 커져야 진짜 리간드 재배향.')
