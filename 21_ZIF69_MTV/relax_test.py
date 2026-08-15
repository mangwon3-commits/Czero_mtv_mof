"""모체 이완 방법 시험 — v3 의 최대 불확실성을 오늘 안에 줄인다.

[왜 이 시험이 값진가]
    AUDIT_20260814.md 6절이 사전 등록 기준에 따라 **v3 재구축**을 판정했습니다.
    그런데 지금 **주기 구조를 이완시킬 수단이 없습니다.**

        UFF4MOF (LAMMPS)  수렴하지 않음. 17종 전부 상한에 걸리고 진동
        DFT               설치 안 됨. 환경 구축 + 30종은 주 단위
        xtb GFN-FF/GFN0   주기 계산은 되지만 Co/Zn MOF 에서 검증 안 해 봄

    SCHEDULE.md 가 계산한 대로, **이 방법이 정해지느냐가 8월이냐 10월이냐를
    가릅니다.** 되면 낙관, 안 되면 오늘부터 대안을 찾습니다. 어느 쪽이든
    며칠짜리 불확실성이 사라집니다.

[사전 등록 판정 기준 — 돌리기 전에 적는다]
    이완의 목적은 "구조를 예쁘게" 가 아니라 **1절에서 진단한 왜곡을 고치는 것**
    입니다. 그러니 그 왜곡이 실제로 줄었는지로 판정합니다.

      ① C–H 가 0.949 -> 1.05~1.12 로 이동       (필수. 이게 안 되면 실패)
      ② 벤조 C–C 폭이 0.192 -> 0.08 미만으로 축소 (필수)
      ③ Zn–N 이 1.90~2.10 안에 유지            (필수. 벗어나면 골격이 깨진 것)
      ④ 셀 부피 변화 15% 이내                   (필수. 넘으면 상이 바뀐 것)
      ⑤ 최소 원자간 거리 > 0.9 Å                (필수)

    ①②를 만족하고 ③④⑤가 깨지지 않으면 **채택**.
    ①이나 ②만 만족하면 **조건부** — 방법은 살리되 파라미터를 조정.
    ③④⑤ 중 하나라도 깨지면 **폐기** — 그 방법은 이 계열에 못 씁니다.

[왜 모체 하나로 먼저 하나]
    30종을 다 돌린 뒤 실패를 알면 그 시간이 통째로 날아갑니다.
    모체 1종은 몇 분~몇십 분이고, 판정에 필요한 정보는 다 나옵니다.
"""
import argparse
import collections
import os
import subprocess
import sys
import time

import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
SPECTRA = '/home/mangwon1/miniconda3/envs/spectra/bin'
COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'Cl': 1.02, 'Zn': 1.22,
       'S': 1.05, 'F': 0.57, 'Br': 1.20, 'Co': 1.26}

# (원소쌍, 이상값, 기준). None 이면 폭만 본다.
TARGETS = {('C', 'H'): 1.083, ('C', 'C'): 1.39, ('C', 'N'): 1.34,
           ('N', 'Zn'): 1.99, ('C', 'Cl'): 1.74, ('N', 'O'): 1.22}


def bond_stats(atoms):
    syms = sorted(set(atoms.get_chemical_symbols()))
    cut = {(a, b): 1.25 * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j, d = neighbor_list('ijd', atoms, cut)
    s = atoms.get_chemical_symbols()
    out = collections.defaultdict(list)
    for a, b, dd in zip(i, j, d):
        if a < b:
            out[tuple(sorted((s[a], s[b])))].append(float(dd))
    return {k: np.array(v) for k, v in out.items()}


def report(atoms, label):
    st = bond_stats(atoms)
    print(f'\n  [{label}]  원자 {len(atoms)}  '
          f'셀부피 {atoms.get_volume():.1f} A^3')
    print(f'    {"결합":>7} {"개수":>5} {"최소":>7} {"중앙":>7} {"최대":>7} '
          f'{"폭":>7} {"이상값":>7}')
    for k in sorted(st, key=lambda x: -len(st[x])):
        v = st[k]
        ideal = TARGETS.get(k)
        print(f'    {k[0]+"-"+k[1]:>7} {len(v):>5} {v.min():>7.3f} '
              f'{np.median(v):>7.3f} {v.max():>7.3f} {v.max()-v.min():>7.3f} '
              f'{ideal if ideal else "-":>7}')
    dmin = float(neighbor_list('d', atoms, 1.3).min())
    print(f'    최소 원자간 거리 {dmin:.3f} A')
    return st, dmin


def judge(st0, st1, v0, v1, dmin1):
    print(f'\n{"="*70}\n  사전 등록 기준으로 판정\n{"="*70}')
    ok = {}

    ch = st1.get(('C', 'H'))
    ok['① C-H 가 1.05~1.12 로'] = ch is not None and 1.05 <= np.median(ch) <= 1.12
    print(f'    ① C-H  {np.median(st0[("C","H")]):.3f} -> '
          f'{np.median(ch):.3f}   {"통과" if ok["① C-H 가 1.05~1.12 로"] else "실패"}')

    w0 = st0[('C', 'C')].max() - st0[('C', 'C')].min()
    w1 = st1[('C', 'C')].max() - st1[('C', 'C')].min() if ('C', 'C') in st1 else 9
    ok['② 벤조 C-C 폭 < 0.08'] = w1 < 0.08
    print(f'    ② C-C 폭  {w0:.3f} -> {w1:.3f}   '
          f'{"통과" if ok["② 벤조 C-C 폭 < 0.08"] else "실패"}')

    zn = st1.get(('N', 'Zn'))
    ok['③ Zn-N 1.90~2.10'] = zn is not None and zn.min() > 1.90 and zn.max() < 2.10
    print(f'    ③ Zn-N  {zn.min():.3f}~{zn.max():.3f}   '
          f'{"통과" if ok["③ Zn-N 1.90~2.10"] else "실패"}' if zn is not None
          else '    ③ Zn-N  없음   실패')

    dv = abs(v1 - v0) / v0 * 100
    ok['④ 셀부피 변화 < 15%'] = dv < 15
    print(f'    ④ 셀부피 {v0:.0f} -> {v1:.0f} ({dv:+.1f}%)   '
          f'{"통과" if ok["④ 셀부피 변화 < 15%"] else "실패"}')

    ok['⑤ 최소거리 > 0.9'] = dmin1 > 0.9
    print(f'    ⑤ 최소거리 {dmin1:.3f}   '
          f'{"통과" if ok["⑤ 최소거리 > 0.9"] else "실패"}')

    must = ok['③ Zn-N 1.90~2.10'] and ok['④ 셀부피 변화 < 15%'] and ok['⑤ 최소거리 > 0.9']
    fix = ok['① C-H 가 1.05~1.12 로'] and ok['② 벤조 C-C 폭 < 0.08']
    print()
    if not must:
        print('  판정: **폐기** — 골격이 깨졌습니다. 이 방법은 이 계열에 못 씁니다.')
        return 2
    if fix:
        print('  판정: **채택** — 왜곡이 고쳐졌고 골격도 살아 있습니다. v3 를 이 방법으로.')
        return 0
    print('  판정: **조건부** — 골격은 살았으나 왜곡이 덜 고쳐졌습니다.')
    print('        파라미터를 조정해 재시도하거나 다른 방법을 봅니다.')
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cif', default=os.path.join(HERE, 'charged_v2', 'base_DDEC6.cif'))
    ap.add_argument('--method', default='gfnff', choices=['gfnff', 'gfn0'])
    ap.add_argument('--out', default=os.path.join(HERE, 'relax_test'))
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    atoms0 = read(a.cif)
    st0, _ = report(atoms0, f'이완 전  {os.path.basename(a.cif)}')
    v0 = atoms0.get_volume()

    # xtb 는 POSCAR 를 읽으면 주기 경계를 자동 인식합니다.
    pos = os.path.join(a.out, 'POSCAR')
    write(pos, atoms0, format='vasp', direct=True, sort=True)

    flag = '--gfnff' if a.method == 'gfnff' else '--gfn 0'
    # [세그폴트의 진짜 원인 — 2026-08-15]
    #   첫 시도가 즉시 SIGSEGV 로 죽어 "GFN-FF 는 이 계열에 못 쓴다" 로 판정할
    #   뻔했습니다. 원인은 **스택 한도 8 MB** 였습니다. xtb 는 큰 배열을 스택에
    #   잡아 600원자 주기계에서 넘칩니다. 풀어 주니 싱글포인트가 19초에
    #   정상 종료했습니다.
    #   **도구 설정 문제를 물질의 성질로 오독할 뻔한 사례**라 여기 적어 둡니다.
    env = ('ulimit -s unlimited 2>/dev/null || ulimit -s 65536; '
           'export OMP_STACKSIZE=4G OMP_NUM_THREADS=2 MKL_NUM_THREADS=2; ')
    cmd = f'{env} nice -n 19 {SPECTRA}/xtb POSCAR {flag} --opt --cycles 500'
    print(f'\n  실행: {cmd}\n  (nice 19 — 수분 v2 에 양보합니다)')
    t0 = time.time()
    r = subprocess.run(cmd, shell=True, cwd=a.out, capture_output=True, text=True)
    el = time.time() - t0
    open(os.path.join(a.out, f'xtb_{a.method}.log'), 'w').write(r.stdout + r.stderr)
    print(f'  경과 {el/60:.1f} 분, 종료코드 {r.returncode}')

    tail = (r.stdout + r.stderr).strip().splitlines()[-12:]
    if 'normal termination' not in (r.stdout + r.stderr):
        print('  !! 정상 종료가 아닙니다:')
        for ln in tail:
            print('      ' + ln)
        return 3

    outf = None
    for cand in ('xtbopt.poscar', 'xtbopt.POSCAR', 'xtbopt.xyz'):
        p = os.path.join(a.out, cand)
        if os.path.exists(p):
            outf = p
            break
    if outf is None:
        print(f'  !! 이완 결과 파일을 못 찾음. 폴더: {os.listdir(a.out)}')
        return 3

    atoms1 = read(outf)
    st1, dmin1 = report(atoms1, f'이완 후  {a.method}')
    write(os.path.join(a.out, f'base_relaxed_{a.method}.cif'), atoms1)
    return judge(st0, st1, v0, atoms1.get_volume(), dmin1)


if __name__ == '__main__':
    sys.exit(main())
