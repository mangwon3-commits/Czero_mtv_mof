"""v3 — 30종 전부를 셀 고정으로 이완한다. 모체에서 통과한 방법 그대로.

[왜 지금 이것을 도나]
    `relax_fixcell.py` 가 모체에서 사전 등록 기준 넷을 전부 통과했습니다.

        (1) C-H   0.949 -> 1.077  (중성자 1.083)
        (2) C-C 폭 0.192 -> 0.050
        (3) Zn-N  1.983~2.010  96쌍 그대로
        (5) 최소거리 1.074
        셀 변화 0.00e+00 A -- 정확히 고정

    23.1분 / 95단계였습니다. **30종이면 감당됩니다.** SCHEDULE.md 가 "8월이냐
    10월이냐를 가른다" 고 적었던 그 불확실성이 사라졌습니다.

[왜 모체만 이완하고 나머지는 힘장으로 얹지 않나]
    기관 요청서에는 그렇게 적었습니다. DFT 를 쓸 때는 그 방법이 표준입니다 --
    모체 하나에 5,000 core-hour 가 드니 30종은 불가능하기 때문입니다.
    그런데 GFN-FF 는 한 종에 30분입니다. **비용 제약이 사라졌으므로 타협할
    이유가 없습니다.** 치환기 자체의 기하도 빌더가 이상값으로 놓은 것이라
    같이 고쳐집니다. 모체에서 C-Cl 폭이 0.309 -> 0.000 으로 간 것이 그 예입니다.

[각 구조마다 판정을 기록한다 -- 통과했으리라 믿지 않는다]
    30종을 돌리고 "다 됐습니다" 라고 하면, 그중 하나가 깨져도 v3 GCMC 90건을
    다 돌린 뒤에나 알게 됩니다. 08-14 의 부착 원자 결함이 정확히 그런 식으로
    몇 주를 잡아먹었습니다. 그래서 **구조마다 (1)(2)(3)(5)를 재서 JSON 에
    남기고**, 하나라도 실패하면 이름을 찍습니다.

[동시 실행 수]
    워커 3 x 스레드 2 = 6코어, nice 19. RASPA 수분 v2 두 건이 아직 돌므로
    그쪽에 양보합니다. boost.sh 의 규칙대로 nice 19 는 남는 CPU 만 받습니다.
"""
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
from ase.io import read, write
from ase.optimize import FIRE

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relax_fixcell import XTBGrad          # noqa: E402
from relax_criteria import bonds as bond_stats   # noqa: E402

SRC = os.path.join(HERE, 'structures_v2')
OUT = os.path.join(HERE, 'relax_v3')
RESULT = os.path.join(HERE, 'relax_v3_results.json')
FMAX = 0.05
STEPS = 800


# [2026-08-16] 판정은 relax_criteria.py 한 군데에만 둡니다.
#   여기 있던 판본이 방향족 C-C 와 sp3 C-C 를 한 통에 넣어 ZIF69_cf3Im075 를
#   헛되이 "실패" 로 찍었습니다. 구조는 멀쩡했고 검사기가 틀렸습니다.
#   그 배치 실행이 남긴 relax_v3_results.json 의 pass 값은 믿지 말고,
#   **judge_relax_v3.py 가 다시 재서 만든 relax_v3_judged.json 을 보세요.**
from relax_criteria import bonds as bond_stats2, evaluate, min_distance  # noqa: E402


def criteria(st0, st1, dmin1, cell_moved):
    return evaluate(st0, st1, dmin1, cell_moved)


def one(cif):
    name = os.path.basename(cif).replace('.cif', '')
    wd = os.path.join(OUT, name)
    dst = os.path.join(OUT, f'{name}_relaxed.cif')
    if os.path.exists(dst):
        return {'name': name, 'skipped': True}

    t0 = time.time()
    atoms = read(cif)
    order = np.argsort(atoms.get_chemical_symbols(), kind='stable')
    atoms = atoms[order]
    cell0 = atoms.get_cell().copy()
    st0 = bond_stats(atoms)

    calc = XTBGrad(wd, method='gfnff', nthreads=2)
    atoms.calc = calc
    opt = FIRE(atoms, trajectory=os.path.join(wd, 'relax.traj'), maxstep=0.1,
               logfile=os.path.join(wd, 'opt.log'))
    try:
        opt.run(fmax=FMAX, steps=STEPS)
        err = None
    except Exception as e:                                  # noqa: BLE001
        err = f'{type(e).__name__}: {e}'

    moved = float(np.abs(atoms.get_cell() - cell0).max())
    st1 = bond_stats(atoms)
    from ase.neighborlist import neighbor_list
    d = neighbor_list('d', atoms, 1.3)
    dmin = float(d.min()) if len(d) else float('inf')

    ok, num = criteria(st0, st1, dmin, moved)
    write(dst, atoms)
    # 궤적과 위상 찌꺼기는 남기지 않습니다. C: 여유가 5 GB 뿐입니다.
    for f in ('gfnff_topo', 'POSCAR', 'gradient', 'energy', 'charges', 'xtbrestart'):
        p = os.path.join(wd, f)
        if os.path.exists(p):
            os.remove(p)

    row = {'name': name, 'skipped': False, 'error': err,
           'steps': calc.ncalls, 'minutes': round((time.time() - t0) / 60, 1),
           'fmax_reached': float(np.abs(atoms.get_forces()).max())
           if err is None else None,
           'pass': all(ok.values()), 'criteria': ok, **num}
    print(f"  [{'통과' if row['pass'] else '실패'}] {name:16s} "
          f"{row['minutes']:5.1f}분 {calc.ncalls:4d}단계  "
          f"C-H {num['CH_after']:.3f}  C-C폭 {num['aromCC_width_after']:.3f}  "
          f"Zn-N {num['ZnN_min']:.3f}~{num['ZnN_max']:.3f}", flush=True)
    return row


def main():
    os.makedirs(OUT, exist_ok=True)
    cifs = sorted(f for f in os.listdir(SRC) if f.endswith('.cif'))
    cifs = [os.path.join(SRC, f) for f in cifs]
    print(f'  구조 {len(cifs)}종, 워커 3 x 스레드 2, nice 19', flush=True)
    print(f'  기준: C-H 1.05~1.12 / C-C폭 <0.08 / Zn-N 1.90~2.10 / '
          f'최소거리 >0.9 / 셀 고정\n', flush=True)

    t0 = time.time()
    # [2026-08-17] pool.map 이 아니라 imap_unordered(chunksize=1) 입니다.
    #
    #   pool.map 은 작업을 미리 **덩어리로 잘라 배분**합니다. 30종 / 워커 3 이면
    #   chunksize 가 3 이라 인덱스 27~29 가 한 덩어리로 묶입니다. 이어받기로
    #   대부분을 건너뛰고 **느린 것 세 개만 남았을 때** 그 배분이 최악이 됩니다 --
    #   saIm075 와 saIm100 이 같은 덩어리(워커 0)에 들어가 순차로 돌고, 워커 하나는
    #   통째로 놉니다. 한 종에 2~3시간이므로 5시간이 될 일이 2.5시간으로 끝날 수
    #   있었습니다.
    #
    #   chunksize=1 로 하나씩 나눠 주면 노는 워커가 바로 다음 것을 집습니다.
    #   결과 순서가 섞이지만 이름으로 판정하므로 상관없습니다.
    with mp.Pool(3) as pool:
        rows = list(pool.imap_unordered(one, cifs, chunksize=1))

    bad = [r['name'] for r in rows if not r.get('skipped') and not r.get('pass')]
    json.dump({'fmax': FMAX, 'steps_cap': STEPS,
               'method': 'GFN-FF, cell fixed, FIRE',
               'wall_hours': round((time.time() - t0) / 3600, 2),
               'failed': bad, 'rows': rows},
              open(RESULT, 'w'), indent=1, ensure_ascii=False)

    print(f'\n  전체 {(time.time()-t0)/3600:.2f} 시간')
    if bad:
        print(f'  !! 기준 미달 {len(bad)}종: {" ".join(bad)}')
        print('     이 구조들은 v3 GCMC 에 넣기 전에 개별로 봐야 합니다.')
        return 1
    print(f'  전 {len(rows)}종 통과. 다음: PACMAN 전하 -> charged_v3 -> GCMC 90')
    return 0


if __name__ == '__main__':
    sys.exit(main())
