# -*- coding: utf-8 -*-
"""MAGI-005 E-24g · E-24h 후속 — 새 치환체의 작동점 S_mix 3씨앗(E-23 · E-24d 와 같은 자). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차 후속.
`run_e24d_mix.py` 사본 — 바꾼 것: 대상(E24G_TAG) · 실행 폴더 · 출력 이름 · 기록 문구. 차단 없는 구조 전용(주머니 있는 구조는 막음 드라이버). 그 원문 첫 줄:
MAGI-005 E-24d — −Cl 의 작동점 S_mix 3씨앗(E-23 과 같은 자).
run_tj1_mix.py(수정 없이) import — E-23 데스크탑 세트의 형판 3씨앗과 같은 방식(같은 CIF, 실행 폴더만 _s1~_s3, 착수 간격 = run_one 의 idx×15 s)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

TAG = os.environ['E24G_TAG']
M.MACHINE = os.environ.get('E24G_MACHINE', 'laptop2')
M.WORKERS = int(os.environ.get('E24MIX_WORKERS', '3'))
M.RUNS = os.path.join(HERE, f'e24g_mix_runs_{TAG}')
M.OUT = os.path.join(HERE, f'results_e24g_{TAG}_mix_{M.MACHINE}.json')
M.TEST = f'MAGI-005 E-24g 후속 — {TAG} 작동점 S_mix'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 21차 후속'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 21차 판정의 뜻 · E-23 최종 1위 규칙 편입'
S_ON, S_ON_ERR = 128.33, 0.0     # 아래 main 전에 파일에서 읽어 덮어씀


def targets():
    t = []
    for k in (1, 2, 3):
        t.append({'name': f'{TAG}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{TAG}_DDEC6.cif'), 'group': '형판 설계(비-ZIF, 우리 앞단)',
                  'dim': 3, 'S_Henry': S_ON, 'S_Henry_err': S_ON_ERR, 'S_Henry_src': f'E-24g results_magi5_e3_{TAG}_widom_hkhome.json ON',
                  'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return t


import json as _j
_d = _j.load(open(os.path.join(HERE, f'results_magi5_e3_{TAG}_widom_hkhome.json')))
_on = [r for r in _d['rows'] if r['charges'] == 'on'][0]
S_ON, S_ON_ERR = _on['selectivity'], _on['selectivity_err']
M.targets = targets
if __name__ == '__main__':
    sys.exit(M.main())
