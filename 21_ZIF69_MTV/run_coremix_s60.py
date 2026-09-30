# -*- coding: utf-8 -*-
"""CoRE 3D 상위 21행(관문 통과 · S_Henry ≥ 60)의 작동점 S_mix — `run_tj1_mix.py` 를 import 하고 대상·폴더·출력만 교체.
등록: 23_SCREENING/COREMIX_REGISTRATION_20260930.md (자료 0건). 프로토콜·완주 판정은 러너 그대로(T-J1′ 와 동일).
환경: TJ1_MACHINE · TJ1_WORKERS (원본과 같음)."""
import csv, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M          # noqa: E402
from ase.io import read          # noqa: E402
import json                      # noqa: E402
M.RUNS = os.path.join(HERE, 'coremix_s60_runs')
M.OUT = os.path.join(HERE, f'results_coremix_s60_{M.MACHINE}.json')
M.TEST = 'CoRE 3D 상위 21행(관문 통과 · S_Henry ≥ 60) 작동점 S_mix — 1단계 1씨앗'
M.ASSIGN_REF = '23_SCREENING/COREMIX_REGISTRATION_20260930.md'
CSV = os.path.join(HERE, '..', '23_SCREENING', 'final_ranking_20260930.csv')


def targets():
    ann = {r['key']: r for r in json.load(open(os.path.join(HERE, 'core_pop_annotated.json')))['rows']}
    sel = [r for r in csv.DictReader(open(CSV, encoding='utf-8'))
           if not r['excluded'] and r['type'] == 'CoRE' and r['dim'] == '3' and float(r['S']) >= 60]
    assert len(sel) == 21, len(sel)
    t = []
    for r in sel:
        a = ann[r['name']]; n = a['file'][:-4]
        S = a['KH_CO2'] / a['KH_N2']
        Se = S * math.hypot(a['KH_CO2_err'] / a['KH_CO2'], a['KH_N2_err'] / a['KH_N2'])
        t.append({'name': n, 'cif': os.path.join(HERE, 'core_pop_cifs', a['file']), 'group': 'CoRE 3D S≥60(CoRE 앞단)', 'dim': a.get('dim'),
                  'S_Henry': S, 'S_Henry_err': Se, 'S_Henry_src': 'core_pop_annotated.json(§AV Widom, ± K_H 전파)',
                  'L': a.get('L'), 'L_src': 'core_pop_annotated.json L', 'flexible': a.get('flexible')})
    for x in t:
        at = read(x['cif']); uc = M.rg.unit_cells(at); x['unit_cells'] = uc; x['N_super'] = len(at) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])            # LPT


M.targets = targets
if __name__ == '__main__':
    sys.exit(M.main())
