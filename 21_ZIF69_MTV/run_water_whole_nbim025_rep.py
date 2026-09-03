"""s_rep 러너 축 가름 — laptop2 에서 nbIm025 RH0 을 **통짜 러너로 4회** (ASSIGN_20260903 §7).

[왜]
    laptop2 의 nbIm025 RH0 실행 간 산포(분할 러너, n=4)는 s_rep 0.00168 로
    다른 세 기기(0.0079~0.0084, 서로 다른 기기·러너·조성)의 1/5 입니다.
    후보는 러너·기기·우연 셋인데, 기기 간 비교는 자(절대 SD / CV / √N)를
    바꾸면 유의성이 갈려 자료가 자를 정하지 못합니다(laptop2 09-03 보고).

    **같은 기기·같은 조성·같은 로딩**에서 분할 대 통짜를 대면 세 자가 전부
    같은 답을 냅니다 — 자 논쟁을 우회하는 유일한 설계입니다. 그래서 laptop2
    에서 통짜로 4회 더 돕니다. 기기와 조성을 고정하고 러너 축만 움직입니다.

[무엇도 바꾸지 않습니다]
    run_water.py **그대로**(통짜: 초기화 5,000 + 생산 15,000 한 실행). 힘장·물
    정의(TIP5P-Ew 5자리)·CO2 모델·분압·컷오프·Ewald 전부 불변. 대상 1종, RH 1점.
    동시성 1 — 분할 4회 중 3회가 동시성 1 이었으므로 맞춥니다(원본 1회는 2).

[반복을 어떻게 분리하나]
    반복마다 결과·실행 폴더를 r1..r4 로 나눕니다. 같은 폴더면 run_water 의
    이어받기가 두 번째부터 전부 cached 로 회수해 **한 번만 돌고 4회로 보입니다.**
    폴더를 나누면 그 함정이 없고, 죽어도 각 r 이 독립으로 이어받습니다.

[판정 — 수를 보기 전에 고정, ASSIGN_20260903 §7-3]
    F = s²(통짜, dof 3) / s²(분할, dof 3)     분할 s_rep = 0.001678 (COMMS/laptop2.md 08-29)
    양측 5%:  F(0.975,3,3) = 15.44   F(0.025,3,3) = 0.0648

사용:
    RASPA_DIR=$HOME/RASPA/simulations python run_water_whole_nbim025_rep.py --rep 1
    python run_water_whole_nbim025_rep.py --summary
"""
import argparse
import json
import os
import shutil
import sys
from statistics import mean, stdev

HERE_REAL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE_REAL)

import run_water as rw                                        # noqa: E402

TAG = 'nbIm025'
N_REP = 4
ROOT = os.path.join(HERE_REAL, 'v3_water_srep_whole')
# 분할 러너 4회 — COMMS/laptop2.md 2026-08-29 보고 ① 의 로딩(mol/kg). 원본(동시성 2) + R1~R3.
SPLIT = [0.7951, 0.7980, 0.7949, 0.7978]
F_HI, F_LO = 15.44, 0.0648        # F(0.975,3,3), F(0.025,3,3)


def setup(rep):
    out = os.path.join(ROOT, f'r{rep}')
    os.makedirs(out, exist_ok=True)
    rw.HERE = out
    rw.CHARGED = os.path.join(HERE_REAL, 'charged_v3')
    rw.RUNS = os.path.join(HERE_REAL, 'water_runs_srep_whole', f'r{rep}')
    rw.WATER_DEF = os.path.join(HERE_REAL, '..', '19_WaterCompetition', 'water.def')
    rw.MAX_WORKERS = 1
    rw.RH_LIST = [0.0]
    rw.TARGETS = [(TAG, 'NO2 25% — s_rep 러너 축 가름, 통짜 반복')]
    return out


def run(rep):
    out = setup(rep)
    print(f'통짜 반복 r{rep}/{N_REP} — {TAG} RH0   결과 {out}', flush=True)
    if len(rw.TARGETS) != 1 or rw.RH_LIST != [0.0] or rw.MAX_WORKERS != 1:
        print('  !! 범위가 어긋납니다. 중단.', flush=True)
        return 1
    if not os.path.exists(os.path.join(rw.CHARGED, TAG + '_DDEC6.cif')):
        print('  !! 전하 CIF 없음', flush=True)
        return 1
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if nsite != 5:
        print(f'  !! 물 정의 사이트 {nsite} (5 여야 함). 중단.', flush=True)
        return 1
    rc = rw.main()
    src = os.path.join(out, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        shutil.copy(src, os.path.join(out, f'water_results_{tag}.json'))
    return rc


def summary():
    vals, errs = [], []
    for rep in range(1, N_REP + 1):
        p = os.path.join(ROOT, f'r{rep}', 'water_results.json')
        if not os.path.exists(p):
            continue
        for r in json.load(open(p, encoding='utf-8')):
            if r['name'] == TAG and r['RH'] == 0.0:
                vals.append(r['CO2_molkg'])
                errs.append(r.get('CO2_err', 0.0))
    print(f'통짜 nbIm025 RH0 — 완주 {len(vals)}/{N_REP}')
    for v, e in zip(vals, errs):
        print(f'    {v:.4f} ± {e:.4f}')
    if len(vals) < 2:
        print('  표본이 2 미만이라 s_rep 없음')
        return 1
    s_whole = stdev(vals)
    s_split = stdev(SPLIT)
    print(f'  통짜  평균 {mean(vals):.4f}  s_rep {s_whole:.5f}  (n={len(vals)})')
    print(f'  분할  평균 {mean(SPLIT):.4f}  s_rep {s_split:.5f}  (n=4, COMMS/laptop2.md 08-29)')
    F = s_whole ** 2 / s_split ** 2
    print(f'  F = s²(통짜)/s²(분할) = {F:.2f}    임계 {F_LO} / {F_HI} (양측 5%, dof 3,3)')
    if len(vals) < N_REP:
        print(f'  ※ dof 가 {len(vals)-1} 이라 위 임계값(dof 3)은 그대로 못 씁니다. 완주 후 다시.')
    if F >= F_HI:
        print('  → 러너 축 확인: 통짜의 실행 간 산포가 분할보다 유의하게 큼. 기제는 별도.')
    elif F <= F_LO:
        print('  → 예상 밖(통짜가 더 작음). 별도 조사.')
    else:
        print('  → 러너로 설명 안 됨(5% 양측). 남는 후보 기기·우연. n=4 검정력 한계 병기.')
    rows = {'tag': TAG, 'runner': 'whole (run_water.py)', 'values': vals, 'ci95': errs,
            's_rep_whole': s_whole, 's_rep_split': s_split, 'split_values': SPLIT,
            'F': F, 'F_crit': [F_LO, F_HI]}
    json.dump(rows, open(os.path.join(ROOT, 'srep_whole_summary.json'), 'w',
                         encoding='utf-8'), indent=2, ensure_ascii=False)
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--rep', type=int)
    ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()
    if a.summary:
        sys.exit(summary())
    if not a.rep or not 1 <= a.rep <= N_REP:
        ap.error(f'--rep 1..{N_REP} 또는 --summary')
    sys.exit(run(a.rep))
