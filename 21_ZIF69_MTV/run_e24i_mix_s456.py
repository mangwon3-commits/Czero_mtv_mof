# -*- coding: utf-8 -*-
"""E-24i CN·Br 작동점 S_mix **추가 3씨앗(_s4~_s6)** — `run_e24i_mix.py` 를 그대로 import 하고 이름·실행 폴더·출력만 분리.
등록: 24_DISCUSSION_WORKFLOW/E24I_SEEDS_REGISTRATION_20260929.md (자료 0건 · 판정 규칙 d ≥ 1.5 단위 유지 여부).
기존 3씨앗 결과 파일(results_e24i_<tag>_mix_<machine>.json)은 건드리지 않음. 환경: E24G_TAG · E24G_MACHINE · E24MIX_WORKERS (원본과 같음)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_e24i_mix as R          # noqa: E402  (env E24G_TAG 필요; S_ON 파일 없으면 자리 채움 1.0 — 비 인용 금지)
from ase.io import read           # noqa: E402
M = R.M; TAG = R.TAG
M.RUNS = os.path.join(HERE, f'e24i_mix_runs_{TAG}_s456')
M.OUT = os.path.join(HERE, f'results_e24i_{TAG}_mix_s456_{M.MACHINE}.json')
M.TEST = f'E-24i 추가 3씨앗(_s4~_s6) — {TAG} 작동점 S_mix (discussion_workflow 20260929-1521 열린 결정 2)'
M.ASSIGN_REF = '24_DISCUSSION_WORKFLOW/E24I_SEEDS_REGISTRATION_20260929.md'
M.REG_REF = '같은 파일 — 판정 규칙 d = (CN̄₆ − Br̄₆)/√(e_CN²+e_Br²), e = ±̄/√6; d ≥ 1.5 유지 / < 1.5 공동 1위'


def targets():
    t = []
    for k in (4, 5, 6):
        t.append({'name': f'{TAG}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{TAG}_DDEC6.cif'), 'group': '형판 설계(비-ZIF, 우리 앞단)',
                  'dim': 3, 'S_Henry': R.S_ON, 'S_Henry_err': R.S_ON_ERR, 'S_Henry_src': R._SRC, 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return t


M.targets = targets
if __name__ == '__main__':
    sys.exit(M.main())
