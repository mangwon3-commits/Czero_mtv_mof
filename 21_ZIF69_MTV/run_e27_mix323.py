# -*- coding: utf-8 -*-
"""MAGI-005 E-27 — 결승 후보의 작동점 S_mix 를 323 K(배가스 온도)에서. 등록 `ASSIGN_MAGI5B_20260925.md` §laptop 9차(자료 0건).
run_tj1_mix.py(수정 없이) import — 온도만 323 K 로(모듈 전역 TEMP; 입력의 ExternalTemperature 와 결과 protocol.T_K 가 이 값을 씀). 나머지(0.15/0.85 · 1 bar · 5,000+15,000 · 표지 · LPT · 착수 간격)는 T-J1′ 과 같음.
대상: 형판 모체 · 4,8-(CN)₂ · 4,8-(CH₃)₂ 각 3씨앗 + 우리 ZIF 두 조성(mslm050 · saIm050 e0) 각 1씨앗. S_Henry 칸은 **298 K 값**(비는 참고 — 온도가 다름)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

M.TEMP = 323.0
M.MACHINE = os.environ.get('E27_MACHINE', 'laptop')
M.WORKERS = int(os.environ.get('E27_WORKERS', '8'))
M.RUNS = os.path.join(HERE, 'e27_mix323_runs')
M.OUT = os.path.join(HERE, f'results_e27_mix323_{M.MACHINE}.json')
M.TEST = 'MAGI-005 E-27 결승 후보 작동점 S_mix 323 K'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop 9차'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §laptop 9차 예측 (1)~(3)'


def _son(path):
    d = json.load(open(os.path.join(HERE, path))); on = [r for r in d['rows'] if r['charges'] == 'on'][0]
    return on['selectivity'], on['selectivity_err']


def targets():
    t = []
    fam = [('e22_parent', 'e22_parent_DDEC6.cif', 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json'),
           ('e24_cn_100', 'e24_cn_100_DDEC6.cif', 'results_magi5_e3_e24_cn_100_widom_hkhome.json'),
           ('e24_ch3_100', 'e24_ch3_100_DDEC6.cif', 'results_magi5_e3_e24_ch3_100_widom_hkhome.json')]
    for n, cif, src in fam:
        s, e = _son(src)
        for k in (1, 2, 3):
            t.append({'name': f'{n}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', cif), 'group': '형판 계열(비-ZIF, 우리 앞단)', 'dim': 3,
                      'S_Henry': s, 'S_Henry_err': e, 'S_Henry_src': src + ' ON (298 K)', 'L': None, 'L_src': '—'})
    v3 = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json')))['rows']}
    for n in ('mslm050', 'saIm050'):
        t.append({'name': n, 'cif': os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'), 'group': '우리', 'dim': 3,
                  'S_Henry': v3[n]['selectivity'], 'S_Henry_err': v3[n].get('selectivity_err'), 'S_Henry_src': 'results_v3.json (298 K)', 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])


M.targets = targets
if __name__ == '__main__':
    if os.environ.get('E27_DRY'):
        for x in M.targets(): print(x['name'], x['N_super'], x['unit_cells'], round(x['S_Henry'], 2), os.path.exists(x['cif']))
        print('TEMP', M.TEMP, 'OUT', M.OUT, 'WORKERS', M.WORKERS); sys.exit(0)
    sys.exit(M.main())
