# -*- coding: utf-8 -*-
"""MAGI-005 E-21b — 작동점 벌점 비(S_mix/S_Henry)의 씨앗 산포 + sa25nb75. Junseok.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §Junseok 12차(14:57, 자료 0건). 예측·기각은 그 원문 그대로 — 이 러너는 값과 표지만. 판정은 종합자.
자: T-J1′ 과 동일 — `run_tj1_mix.py`(수정 없이)를 import 해 대상·실행 폴더·출력만 바꿈(E-21 `run_e21_mix.py` 방식). 0.15/0.85 · 1 bar · 298 K ·
    5,000+15,000 · 완주 표지 + 두 성분 적재 각 1줄 + 반환코드 0 · LPT(N_super) · 착수 간격 15 s(씨앗).
대상: mslm050 새 씨앗 2 · saIm050 새 씨앗 2 · sa25nb75 1 = 5작업. 같은 조성 반복은 실행 폴더(mix_<이름>)가 겹치지 않게 이름에 _s2 · _s3
      (T-J1′ laptop 값 = s1). S_Henry 는 run_tj1_mix.targets() 그대로(results_v3; sa25nb75 는 v3 에 없어 results_v4mix) — T-J1′ 과 같은 분모.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402

M.OURS = ['mslm050', 'saIm050', 'sa25nb75']
M.CORE = []
M.ONLY_EXTRA = False
M.MACHINE = 'junseok'
M.WORKERS = int(os.environ.get('E21B_WORKERS', '5'))
M.RUNS = os.path.join(HERE, 'e21b_mix_runs')
M.OUT = os.path.join(HERE, 'results_e21b_mix_junseok.json')
M.TEST = 'MAGI-005 E-21b 작동점 벌점 비(S_mix/S_Henry)의 씨앗 산포 + sa25nb75'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §Junseok 12차'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §Junseok 12차 예측 (1)(2)(3) — 반복 비 대 T-J1′(mslm050 0.676 · saIm050 0.643) 1.5 단위(S_mix ± 기준)'
REPEATS = (('mslm050', 's2'), ('mslm050', 's3'), ('saIm050', 's2'), ('saIm050', 's3'), ('sa25nb75', None))
_targets = M.targets


def targets():
    base = {x['name']: x for x in _targets()}
    t = []
    for n, s in REPEATS:
        x = dict(base[n])
        x['name'] = f'{n}_{s}' if s else n
        t.append(x)
    return sorted(t, key=lambda x: -x['N_super'])            # LPT — run_tj1_mix 와 같음


M.targets = targets     # M.main() 은 모듈 전역 targets 를 부르므로 이것이 쓰임

if __name__ == '__main__':
    if os.environ.get('E21B_DRY'):
        for x in M.targets():
            e = x['S_Henry_err']
            print(f"{x['name']:12s} N_super {x['N_super']:6d} 셀 {x['unit_cells']} S_Henry {x['S_Henry']:.2f} ± {e if e is None else round(e, 2)} "
                  f"({x['S_Henry_src']}) L {x['L']:.3f} cif {os.path.relpath(x['cif'], HERE)} 존재 {os.path.exists(x['cif'])}")
        print('OUT', M.OUT, '· RUNS', M.RUNS, '· WORKERS', M.WORKERS, '· MACHINE', M.MACHINE, '· RUNS 존재', os.path.exists(M.RUNS),
              '· OUT 존재', os.path.exists(M.OUT))
        sys.exit(0)
    sys.exit(M.main())
