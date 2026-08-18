"""GFN-FF 이완 결과를 다시 판정한다 — 단위 함정을 걷어내고.

[왜 다시 하나]
    relax_test.py 가 "셀부피 11435.7 -> 50939.7" 을 찍고 죽었습니다(4.45배 팽창).
    그 숫자가 사실이면 GFN-FF 는 즉시 폐기입니다. 그런데 xtb 자신의 로그는
    마지막 사이클에서 **7548.5 A^3** 이라고 적었습니다. 둘이 안 맞습니다.

        50939.7 / 7548.5 = 6.748 = (1 Bohr / 1 Angstrom)^3 = 1.8897^3

    **xtbopt.poscar 의 격자는 Bohr 로 적혀 있고 ASE 는 그것을 Angstrom 으로
    읽었습니다.** 물질의 성질이 아니라 단위입니다. 스택 한도 세그폴트에 이어
    두 번째로 같은 함정에 걸릴 뻔했습니다.

    좌표는 Direct(분율)이므로 격자만 고치면 결합 길이가 제자리를 찾습니다.
    검산: 고친 뒤 C-H 가 물리적으로 말이 되는 값이면 가설이 맞습니다.
"""
import os
import sys

import numpy as np
from ase.io import read, write

sys.path.insert(0, '/home/mangwon1/mof_project/21_ZIF69_MTV')
from relax_test import bond_stats, report, judge  # noqa: E402

BOHR = 0.52917721092
R = '/home/mangwon1/mof_project/21_ZIF69_MTV/relax_test'

before = read(os.path.join(R, 'POSCAR'))
after_raw = read(os.path.join(R, 'xtbopt.poscar'))

v_raw = after_raw.get_volume()
print(f'  xtbopt.poscar 를 그대로 읽으면 셀부피 {v_raw:.1f} A^3')
print(f'  xtb 로그의 마지막 사이클      셀부피 7548.5 A^3')
print(f'  비 {v_raw/7548.5:.4f}   (1 Bohr/1 A)^3 = {(1/BOHR)**3:.4f}')

# 격자만 Bohr -> Angstrom. 분율좌표는 건드리지 않는다.
after = after_raw.copy()
after.set_cell(after_raw.get_cell() * BOHR, scale_atoms=True)
print(f'\n  단위 보정 후 셀부피 {after.get_volume():.1f} A^3'
      f'  (로그와 차이 {abs(after.get_volume()-7548.5):.1f})')

st0, _ = report(before, '이완 전')
st1, dmin1 = report(after, '이완 후 (Bohr 보정)')

write(os.path.join(R, 'base_relaxed_gfnff.cif'), after)
code = judge(st0, st1, before.get_volume(), after.get_volume(), dmin1)

print(f'\n{"="*70}')
print('  주의: ④ 는 우리가 **애초에 원하지 않았던** 자유도입니다.')
print('  v3 방침은 "원자만 이완, 셀은 실험값 고정" 인데 xtb --opt 는 주기계에서')
print('  격자까지 풉니다. 그러니 ④ 의 실패는 GFN-FF 의 결격이 아니라')
print('  **실행 조건이 방침과 달랐다**는 뜻입니다. ①②③⑤ 가 판정의 핵심입니다.')
sys.exit(code)
