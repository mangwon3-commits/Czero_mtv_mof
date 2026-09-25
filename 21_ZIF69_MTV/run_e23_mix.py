# -*- coding: utf-8 -*-
"""MAGI-005 E-23 — 최종 작동점 순위(배치 평균 S_mix). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 12차 + Junseok 13차(자료 0건).

자: T-J1′ 과 같음 — `run_tj1_mix.py`(수정 없이)를 import 해 대상·실행 폴더·출력만 바꿈(E-21 · E-21b 방식).
대상은 환경변수 E23_SET 로 가름:
  desktop  sa50nb50 e1~e5 + 형판 Zn(bib)(bdtdc) 우리 앞단(charged_v3/e22_parent_DDEC6.cif) 씨앗 3 (8워커)
  junseok  mslm050 e1~e5 + saIm050 e1~e5 (10워커)
S_Henry = 같은 실현의 Widom S_ON: E-14c(sa50nb50 · saIm050) · E-14d(mslm050) 실현표, 형판 = E-22b 모체.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

SET = os.environ.get('E23_SET', '')
SETS = {'desktop': (['sa50nb50'], True, 8), 'junseok': (['mslm050', 'saIm050'], False, 10)}
if SET not in SETS:
    sys.exit(f'E23_SET 은 {list(SETS)} 중 하나 — 받은 값 {SET!r}')
COMPS, WITH_TEMPLATE, W = SETS[SET]
M.MACHINE = SET
M.WORKERS = int(os.environ.get('E23_WORKERS', str(W)))
M.RUNS = os.path.join(HERE, 'e23_mix_runs')
M.OUT = os.path.join(HERE, f'results_e23_mix_{SET}.json')
M.TEST = 'MAGI-005 E-23 최종 작동점 순위(배치 평균 S_mix)'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 12차 + Junseok 13차'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 12차 + Junseok 13차 예측 (1)~(4) · 최종 1위 규칙'


def _realizations():
    out = {}
    c = json.load(open(os.path.join(HERE, 'results_magi5_e14c_offwidom_laptop2.json')))['e14c_summary']['realizations']
    d = json.load(open(os.path.join(HERE, 'results_magi5_e14d_offwidom_laptop2.json')))['e14d_summary']['realizations_mslm050']
    for comp, rows, src in (('sa50nb50', c['sa50nb50'], 'E-14c'), ('saIm050', c['saIm050'], 'E-14c'), ('mslm050', d, 'E-14d')):
        for r in rows:
            if r['realization'] == 0:
                continue                                    # e0 은 T-J1′ · E-21b 값
            out[r['name'].replace('_DDEC6', '')] = (r['S_ON'], r['S_ON_err'], f"{src} 실현표 S_ON({r['name']})")
    return out


def targets():
    rz = _realizations(); t = []
    for comp in COMPS:
        for e in range(1, 6):
            n = f'{comp}e{e}'; s, se, src = rz[n]
            t.append({'name': n, 'cif': os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'), 'group': '우리', 'dim': 3,
                      'S_Henry': s, 'S_Henry_err': se, 'S_Henry_src': src, 'L': None, 'L_src': '—(E-23 에서 안 씀)'})
    if WITH_TEMPLATE:
        for k in (1, 2, 3):
            t.append({'name': f'e22_parent_s{k}', 'cif': os.path.join(HERE, 'charged_v3', 'e22_parent_DDEC6.cif'),
                      'group': '형판(비-ZIF, 우리 앞단)', 'dim': 3, 'S_Henry': 87.80452868133223, 'S_Henry_err': 1.218371194109736,
                      'S_Henry_src': 'E-22b results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json ON', 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a)
        x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])            # LPT — run_tj1_mix 와 같음


M.targets = targets

if __name__ == '__main__':
    if os.environ.get('E23_DRY'):
        for x in M.targets():
            print(f"{x['name']:16s} N_super {x['N_super']:6d} 셀 {x['unit_cells']} S_Henry {x['S_Henry']:.2f} ± {x['S_Henry_err']:.2f} "
                  f"({x['S_Henry_src']}) cif {os.path.relpath(x['cif'], HERE)} 존재 {os.path.exists(x['cif'])}")
        print('OUT', M.OUT, '· RUNS', M.RUNS, '· WORKERS', M.WORKERS, '· RUNS 존재', os.path.exists(M.RUNS), '· OUT 존재', os.path.exists(M.OUT))
        sys.exit(0)
    sys.exit(M.main())
