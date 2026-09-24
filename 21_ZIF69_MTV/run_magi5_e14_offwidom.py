# -*- coding: utf-8 -*-
"""MAGI-005 E-14 — 우리 v3 조성 27종의 골격 전하 OFF Widom(CO₂·N₂) → G = S_ON/S_OFF 지도. 데스크탑(HKHOME) 몫.

등록: `ASSIGN_MAGI5B_20260925.md §HKHOME 2차`(자료 0건). 자는 E-1 과 같다 — `run_magi5_offwidom.py` 를 import 해
대상·출력·실행 뿌리만 바꾼다(E-10 러너와 같은 방식). S_ON 은 results_v3.json 의 같은 자 Widom 값(행에 출처).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_magi5_offwidom as M  # noqa: E402

EXCLUDE = {'mslm075', 'saIm075', 'saIm100',   # 관문 탈락(risk_results_v3.json pass False)
           'saIm050'}                          # E-1 에서 OFF 완주 — 값 재사용


def targets():
    v3 = json.load(open(os.path.join(HERE, 'results_v3.json'), encoding='utf-8'))['rows']
    rg3 = json.load(open(os.path.join(HERE, 'risk_results_v3.json'), encoding='utf-8'))
    gate = {r['name']: r.get('pass') for r in rg3['rows'] if isinstance(r, dict)}
    out = []
    for r in v3:
        n = r['name']
        if n in EXCLUDE:
            continue
        if gate.get(n) is not True:
            continue
        out.append({'name': n + '_DDEC6', 'cif': os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'), 'key': n, 'dim': 3,
                    'identity': '우리 v3 조성(ZIF-69 gme)', 'identity_note': f"group {r.get('group')} · frac {r.get('frac')} · LCD {r.get('LCD')} · PLD {r.get('PLD')}",
                    'on_ref': {'src': 'results_v3.json', 'KH_CO2': r['KH_CO2'], 'KH_CO2_err': r['KH_CO2_err'],
                               'KH_N2': r['KH_N2'], 'KH_N2_err': r['KH_N2_err'], 'dU_CO2': None},
                    'extra': {'group': r.get('group'), 'frac': r.get('frac')}})
    return out


if __name__ == '__main__':
    M.TARGETS = targets()
    M.RUNS = os.path.join(HERE, 'magi5_e14_runs')
    M.OUT = os.path.join(HERE, f'results_magi5_e14_offwidom_{M.MACHINE}.json')
    M.TEST = 'MAGI-005 E-14 우리 v3 조성 G 지도(전하 OFF Widom)'
    M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 2차 E-14'
    M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 2차 예측 (1)~(5)'
    print(f'대상 {len(M.TARGETS)}', flush=True)
    sys.exit(M.main())
