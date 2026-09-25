# -*- coding: utf-8 -*-
"""MAGI-005 E-21 — 작동점 벌점 대 G (T-J1′ 확장). laptop(Melchior).

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop 6차(14:32, 자료 0건). 예측·기각은 그 원문 그대로 — 이 러너는 값과 표지만. 판정·ρ 는 종합자.
자: T-J1′ 과 동일 — `run_tj1_mix.py` 를 import 해 대상·출력만 바꿈(E-10 방식). 0.15/0.85 · 1 bar · 298 K · 5,000+15,000 ·
    완주 표지 + 두 성분 적재 각 1줄 + 반환코드 0 · LPT(N_super) · 착수 간격 15 s.
S_Henry = results_v3.json(ms50nb50 은 v3 에 없어 results_v4mix.json) · ± 포함 → 행에 ratio_err(S_mix ± 만)와 ratio_err_with_SHenry(합성) 병기.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402

M.OURS = ['nbIm050', 'mslm025', 'saIm025', 'cf3Im075', 'fbIm100', 'ms50nb50']
M.CORE = []
M.ONLY_EXTRA = False
M.WORKERS = int(os.environ.get('E21_WORKERS', '6'))
M.RUNS = os.path.join(HERE, 'e21_mix_runs')
M.OUT = os.path.join(HERE, f'results_e21_mix_{M.MACHINE}.json')
M.TEST = 'MAGI-005 E-21 작동점 벌점 대 G (T-J1′ 확장, S_mix/S_Henry)'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop 6차'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §laptop 6차 예측(1)(2) — ρ(비, G) ≤ −0.5(n 11), 기각 ρ ≥ 0'

if __name__ == '__main__':
    if os.environ.get('E21_DRY'):
        for x in M.targets():
            print(f"{x['name']:10s} N_super {x['N_super']:6d} 셀 {x['unit_cells']} S_Henry {x['S_Henry']:.2f} ± {x['S_Henry_err']:.2f} "
                  f"({x['S_Henry_src']}) L {x['L']:.3f} cif {os.path.relpath(x['cif'], HERE)} 존재 {os.path.exists(x['cif'])}")
        print('OUT', M.OUT, '· RUNS', M.RUNS, '· WORKERS', M.WORKERS, '· RUNS 존재', os.path.exists(M.RUNS))
        sys.exit(0)
    sys.exit(M.main())
