# -*- coding: utf-8 -*-
"""MAGI-005 E-24 후속 — 설계 후보 Zn(bib)(bdtdc)-4,8-(CH₃)₂ 의 작동점 S_mix 3씨앗 (E-24b ②)(E-23 과 같은 자). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 14차 E-24b ②.
run_tj1_mix.py(수정 없이) import — E-23 데스크탑 세트의 형판 3씨앗과 같은 방식(같은 CIF, 실행 폴더만 _s1~_s3, 착수 간격 = run_one 의 idx×15 s)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

M.MACHINE = 'desktop'
M.WORKERS = int(os.environ.get('E24MIX_WORKERS', '3'))
M.RUNS = os.path.join(HERE, 'e24b_mix_runs')
M.OUT = os.path.join(HERE, 'results_e24b_mix_desktop.json')
M.TEST = 'MAGI-005 E-24 후속 — Zn(bib)(bdtdc)-4,8-(CH3)2 작동점 S_mix'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 13차(가)'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 13차(가) (3) 성립 뒤 후속 · E-23 최종 1위 규칙 편입'
S_ON, S_ON_ERR = 154.07, 0.0     # 아래 main 전에 파일에서 읽어 덮어씀


def targets():
    t = []
    for k in (1, 2, 3):
        t.append({'name': f'e24_ch3_100_s{k}', 'cif': os.path.join(HERE, 'charged_v3', 'e24_ch3_100_DDEC6.cif'), 'group': '형판 설계(비-ZIF, 우리 앞단)',
                  'dim': 3, 'S_Henry': S_ON, 'S_Henry_err': S_ON_ERR, 'S_Henry_src': 'E-24 results_magi5_e3_e24_ch3_100_widom_hkhome.json ON',
                  'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return t


import json as _j
_d = _j.load(open(os.path.join(HERE, 'results_magi5_e3_e24_ch3_100_widom_hkhome.json')))
_on = [r for r in _d['rows'] if r['charges'] == 'on'][0]
S_ON, S_ON_ERR = _on['selectivity'], _on['selectivity_err']
M.targets = targets
if __name__ == '__main__':
    sys.exit(M.main())
