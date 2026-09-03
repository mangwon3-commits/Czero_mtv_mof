"""모체 이완 — **원자만, 셀은 실험값 고정.** v3 방침 그대로.

[왜 다시 하나 — 1차 시험이 무엇을 재고 무엇을 못 쟀나]
    08-15 밤에 `relax_test.py` 로 GFN-FF 를 4시간 39분 돌렸습니다. 결과:

        ① C-H  0.949 -> 1.077   통과 (중성자 1.083 과 0.6% 차이)
        ② C-C 폭 0.192 -> 0.059  통과
        ③ Zn-N  1.940~2.386     실패 (상한 2.10 초과)
        ④ 셀부피 -34.0%          실패
        ⑤ 최소거리 1.070         통과

    사전 등록 규칙대로 **그 실행의 판정은 폐기**입니다. 규칙을 결과를 보고
    고치지는 않습니다.

    다만 그 실행은 **우리 방침과 다른 것을 쟀습니다.** `xtb --opt` 는 주기계에서
    격자까지 함께 풉니다. 우리 방침(Part 0-D 7-2, 기관 요청서 3절)은 처음부터
    **원자 위치만 이완하고 셀은 X선 실험값에 고정**입니다. 격자가 34% 수축하면
    골격이 눌리므로 ③ 의 실패는 ④ 의 결과일 가능성이 큽니다 -- Zn-N 이 96 쌍에서
    98 쌍으로 늘어난 것이 눌림의 흔적입니다.

    그래서 이것은 **재시도가 아니라 다른 시험**입니다.

[이 시험의 판정 기준 — 돌리기 전에 등록한다]
    ④ 는 셀을 고정하므로 정의상 만족되어 판정에서 뺍니다. 나머지는 그대로.

      ① C-H 중앙값 1.05~1.12          (필수)
      ② 벤조 C-C 폭 < 0.08            (필수)
      ③ Zn-N 전부 1.90~2.10 안        (필수)
      ⑤ 최소 원자간 거리 > 0.9 A      (필수)

    ①②③⑤ 전부 통과해야 **채택**.
    **③ 이 또 실패하면 GFN-FF 는 이 계열에서 최종 폐기**합니다 -- 셀을 고정했는데도
    금속 배위가 깨진다면 그건 눌림 탓이 아니라 힘장 탓입니다. 그때는 기관 DFT 가
    유일한 길이 되고, 요청서를 철회하지 않습니다.

[왜 xtb 를 직접 못 쓰고 ASE 를 끼우나]
    xtb 에는 주기계에서 격자만 고정하는 옵션이 없습니다. 그래서 xtb 는
    **힘 계산기로만** 쓰고, 움직이는 일은 ASE 최적화기에 맡깁니다. 셀을
    자유도에 넣지 않으면(UnitCellFilter 를 쓰지 않으면) 셀은 정의상 고정입니다.

[두 번 걸린 함정 — 여기 적어 둔다]
    1. 세그폴트는 물질이 아니라 **스택 한도 8 MB** 였습니다.
    2. "셀부피 4.45배 팽창" 은 물질이 아니라 **단위**였습니다. xtb 가 쓴
       `xtbopt.poscar` 의 격자는 Bohr 인데 ASE 가 Angstrom 으로 읽었습니다
       (50939.7 / 7548.5 = 6.7483 = 1.8897^3). 실제로는 34% 수축이었습니다.
    두 번 다 도구 설정을 물질의 성질로 오독할 뻔했습니다. 그래서 이 스크립트는
    **xtb 로그의 에너지와 ASE 가 본 에너지를 매 단계 대조**합니다.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.io import read, write
from ase.optimize import FIRE
from ase.units import Bohr, Hartree

HERE = os.path.dirname(os.path.abspath(__file__))
# [2026-09-03] 데스크탑 절대경로가 박혀 있어 laptop2 가 못 썼습니다(ASSIGN_20260903 §1-4b).
# 다른 기기는 XTB_BIN 환경변수로 덮습니다. 기본값은 데스크탑 그대로.
XTB = os.environ.get('XTB_BIN', '/home/mangwon1/miniconda3/envs/spectra/bin/xtb')

# xtb 는 스택에 큰 배열을 잡습니다. 600원자 주기계에서 8 MB 한도를 넘습니다.
PRE = ('ulimit -s unlimited 2>/dev/null || ulimit -s 65536; '
       'export OMP_STACKSIZE=4G OMP_NUM_THREADS={n} MKL_NUM_THREADS={n}; ')


class XTBGrad(Calculator):
    """xtb 를 파일 기반 힘 계산기로 쓴다. 셀은 넘기되 절대 움직이지 않는다."""

    implemented_properties = ['energy', 'forces']

    def __init__(self, workdir, method='gfnff', nthreads=4, **kw):
        Calculator.__init__(self, **kw)
        self.workdir = workdir
        self.method = method
        self.nthreads = nthreads
        self.ncalls = 0
        self.seconds = 0.0
        os.makedirs(workdir, exist_ok=True)

    def calculate(self, atoms=None, properties=None, system_changes=all_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        wd = self.workdir
        # gradient 는 xtb 가 이어 붙이므로 지웁니다.
        #
        # gfnff_topo 도 **반드시** 지웁니다. 이것을 남겨 두면 xtb 가 재사용하는데,
        # 원자가 움직인 뒤에는 그 위상이 낡아서 **NaN 기울기**를 돌려줍니다.
        # 같은 좌표를 깨끗한 폴더에서 다시 계산해 확인했습니다:
        #     낡은 위상 재사용 -> E = -114.898 Eh, |dE/dxyz| = NaN
        #     위상 새로 생성   -> E = -123.948 Eh, |dE/dxyz| = 2.161
        # 좌표는 한 글자도 같습니다. 차이는 위상 파일 하나뿐이었습니다.
        for f in ('gradient', 'energy', 'gfnff_topo', 'charges', 'xtbrestart'):
            p = os.path.join(wd, f)
            if os.path.exists(p):
                os.remove(p)

        # [방어] 좌표가 NaN 이면 여기서 멈춥니다. 첫 시도에서 NaN 좌표가
        # xtb 로 넘어가 "HB 결합 4271만 개" 라는 헛소리와 LAPACK 실패로
        # 나타났습니다. 원인은 힘이었는데 증상은 xtb 쪽에서 났습니다.
        if not np.isfinite(self.atoms.positions).all():
            raise RuntimeError('좌표에 NaN/inf — 직전 단계의 힘이 발산했습니다')
        # sort=False: 우리가 이미 종별로 정렬해 두었으므로 순서가 어긋나지
        # 않아야 합니다. 정렬을 여기서 또 하면 gradient 와 짝이 틀어집니다.
        write(os.path.join(wd, 'POSCAR'), self.atoms, format='vasp',
              direct=True, sort=False)

        flag = '--gfnff' if self.method == 'gfnff' else '--gfn 0'
        cmd = (PRE.format(n=self.nthreads) +
               f'nice -n 19 {XTB} POSCAR {flag} --grad > xtb_step.log 2>&1')
        t0 = time.time()
        r = subprocess.run(cmd, shell=True, cwd=wd)
        self.seconds += time.time() - t0
        if r.returncode != 0:
            raise RuntimeError(f'xtb 종료코드 {r.returncode} — xtb_step.log 확인')

        e, g = self._read_gradient(os.path.join(wd, 'gradient'), len(self.atoms))
        if not np.isfinite(g).all():
            raise RuntimeError('xtb 가 NaN 기울기를 돌려줬습니다')
        gmax = np.abs(g).max() * Hartree / Bohr
        if gmax > 50.0:
            raise RuntimeError(
                f'최대 힘 {gmax:.1f} eV/A — 물리적으로 불가능합니다. '
                '위상 파일이나 원자 순서가 어긋났을 가능성이 큽니다.')
        self.ncalls += 1
        self.results['energy'] = e * Hartree
        self.results['forces'] = -g * Hartree / Bohr

    @staticmethod
    def _read_gradient(path, natoms):
        with open(path) as fh:
            lines = [ln.rstrip('\n') for ln in fh]
        # 마지막 cycle 블록만 씁니다.
        starts = [i for i, ln in enumerate(lines) if 'cycle =' in ln]
        if not starts:
            raise RuntimeError(f'{path} 에 cycle 블록이 없습니다')
        i0 = starts[-1]
        energy = float(lines[i0].split('SCF energy =')[1].split()[0])
        # cycle 줄 다음: 좌표 natoms 줄, 그 다음 기울기 natoms 줄
        gl = lines[i0 + 1 + natoms: i0 + 1 + 2 * natoms]
        if len(gl) != natoms:
            raise RuntimeError(f'기울기 줄 {len(gl)}개, 원자 {natoms}개 — 불일치')
        g = np.array([[float(x.replace('D', 'E').replace('d', 'E'))
                       for x in ln.split()[:3]] for ln in gl])
        return energy, g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cif', default=os.path.join(HERE, 'charged_v2', 'base_DDEC6.cif'))
    ap.add_argument('--method', default='gfnff', choices=['gfnff', 'gfn0'])
    ap.add_argument('--out', default=os.path.join(HERE, 'relax_fixcell'))
    ap.add_argument('--fmax', type=float, default=0.05)   # eV/A
    ap.add_argument('--steps', type=int, default=600)
    ap.add_argument('--nthreads', type=int, default=4)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    sys.path.insert(0, HERE)
    from relax_test import report, TARGETS  # noqa: F401

    atoms = read(a.cif)
    # 종별로 한 번 정렬해 두고, 이후 순서를 절대 바꾸지 않습니다.
    order = np.argsort(atoms.get_chemical_symbols(), kind='stable')
    atoms = atoms[order]
    cell0 = atoms.get_cell().copy()
    v0 = atoms.get_volume()
    st0, _ = report(atoms, f'이완 전  {os.path.basename(a.cif)}')

    # [하지 말 것] 1차 시험의 gfnff_topo(155 MB)를 복사해 재사용하려 했습니다.
    # "위상을 고정하면 이완 중 결합이 끊기지 않는다" 는 생각 자체는 맞지만,
    # 그 파일은 **다른 원자 순서**로 만들어진 것이었습니다. relax_test 는
    # ASE 의 sort=True(np.argsort 기본 quicksort, 불안정)로, 여기서는
    # kind='stable' 로 정렬하므로 같은 원소 안의 순서가 다를 수 있습니다.
    # 그 결과 힘이 헛나왔고 FIRE 가 구조를 NaN 으로 날려 버렸습니다.
    # xtb 가 매번 자기 POSCAR 에서 위상을 새로 잡게 둡니다.
    calc = XTBGrad(a.out, method=a.method, nthreads=a.nthreads)
    atoms.calc = calc

    traj = os.path.join(a.out, f'relax_{a.method}.traj')
    # maxstep 0.1: 한 단계에 원자가 0.1 A 넘게 못 움직입니다. 힘이 헛나와도
    # 구조가 한 번에 날아가지 않고, 위의 방어 검사에 걸립니다.
    opt = FIRE(atoms, trajectory=traj, maxstep=0.1,
               logfile=os.path.join(a.out, 'opt.log'))

    t0 = time.time()
    print(f'\n  FIRE 시작 — fmax {a.fmax} eV/A, 최대 {a.steps} 단계, '
          f'{a.nthreads} 스레드, nice 19')
    print(f'  셀 고정: {cell0.lengths().round(3)} / {cell0.angles().round(2)}도')
    try:
        opt.run(fmax=a.fmax, steps=a.steps)
    except KeyboardInterrupt:
        print('  중단됨 — 지금까지의 구조로 판정합니다')
    el = time.time() - t0
    print(f'  경과 {el/60:.1f} 분, xtb 호출 {calc.ncalls}회, '
          f'단계당 {el/max(calc.ncalls,1):.1f} 초')

    # 셀이 정말 안 움직였는지 확인합니다. 안 움직이는 게 이 시험의 전제입니다.
    dcell = float(np.abs(atoms.get_cell() - cell0).max())
    print(f'  셀 변화 최대 성분 {dcell:.2e} A  '
          f'{"(고정 확인)" if dcell < 1e-9 else "!! 셀이 움직였습니다"}')

    write(os.path.join(a.out, f'base_relaxed_{a.method}_fixcell.cif'), atoms)
    st1, dmin1 = report(atoms, f'이완 후  {a.method} (셀 고정)')

    print(f'\n{"="*70}\n  사전 등록 기준 (셀 고정판 — ④ 는 정의상 만족)\n{"="*70}')
    ch = np.median(st1[('C', 'H')])
    o1 = 1.05 <= ch <= 1.12
    w1 = st1[('C', 'C')].max() - st1[('C', 'C')].min()
    o2 = w1 < 0.08
    zn = st1[('N', 'Zn')]
    o3 = zn.min() > 1.90 and zn.max() < 2.10
    o5 = dmin1 > 0.9
    print(f'    ① C-H   {np.median(st0[("C","H")]):.3f} -> {ch:.3f}'
          f'          {"통과" if o1 else "실패"}')
    print(f'    ② C-C 폭 {st0[("C","C")].max()-st0[("C","C")].min():.3f} -> {w1:.3f}'
          f'          {"통과" if o2 else "실패"}')
    print(f'    ③ Zn-N  {zn.min():.3f}~{zn.max():.3f}  ({len(zn)}쌍)'
          f'   {"통과" if o3 else "실패"}')
    print(f'    ④ 셀부피 {v0:.0f} (고정)               해당없음')
    print(f'    ⑤ 최소거리 {dmin1:.3f}                 {"통과" if o5 else "실패"}')
    print()
    if o1 and o2 and o3 and o5:
        print('  판정: **채택** — v3 는 이 방법으로. 기관 DFT 요청은 철회합니다.')
        return 0
    if not o3:
        print('  판정: **최종 폐기** — 셀을 고정했는데도 금속 배위가 깨집니다.')
        print('        눌림 탓이 아니라 힘장 탓입니다. 기관 DFT 가 유일한 길입니다.')
        return 2
    print('  판정: **조건부** — 골격은 살았으나 왜곡이 덜 고쳐졌습니다.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
