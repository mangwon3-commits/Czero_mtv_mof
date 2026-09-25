# -*- coding: utf-8 -*-
"""MAGI-005 E-14d — mslm050 배치 평균 G: 앙상블 5 실현의 전하 OFF Widom 10작업. laptop2(Balthasar) 몫.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop2 5차 (자료 0건 시점 예측 고정).
    (1) mslm050 배치 평균 G 가 saIm050 배치 평균 4.381(SD 0.431, E-14c n6)과 1.5 배치 단위 안 — 기각: 1.5 배치 단위 넘게 위 또는 아래
    (2) G CV < S_ON CV (E-14c 재현)
판정문은 종합자가 씁니다 — 값과 표지만 냅니다.

E-14c 래퍼(`run_magi5_e14c_offwidom.py`)와 **같은 방식** — `run_magi5_offwidom.py` 를 import 해 대상·출력·실행 뿌리만 바꿉니다.
ON 값은 `results_v3ens_mslm050.json` 의 같은 이름 행(같은 자 Widom). 실현 0(원판)은 E-14 mslm050(results_magi5_e14_offwidom_hkhome.json, G 4.69)을
판정 때 더합니다. 관문 ⑤ 는 데스크탑(`run_e14d_gate5.py`)이 돌리고 판정 전 조인합니다 — 여기서는 막지 않고 '미확인' 으로 적습니다.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_magi5_offwidom as M  # noqa: E402

NAMES = ['mslm050e1', 'mslm050e2', 'mslm050e3', 'mslm050e4', 'mslm050e5']


def _rows(path):
    d = json.load(open(os.path.join(HERE, path), encoding='utf-8'))
    rows = d.get('rows', d) if isinstance(d, dict) else d
    return rows if isinstance(rows, list) else list(rows.values())


def targets():
    by = {r['name']: r for r in _rows('results_v3ens_mslm050.json')}
    out = []
    for k, n in enumerate(NAMES, 1):
        r = by[n]
        out.append({
            'name': f'{n}_DDEC6', 'cif': os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), 'key': n, 'dim': 3,
            'identity': f'우리 v3 앙상블 실현(mslm050 e{k}, ZIF-69 gme)',
            'identity_note': '관문 ⑤ 표지: 미확인 — 데스크탑 run_e14d_gate5.py 가 돌리는 중(판정 전 조인, 탈락 실현 제외 — CLAUDE.md §2)',
            'on_ref': {'src': 'results_v3ens_mslm050.json', 'KH_CO2': r['KH_CO2'], 'KH_CO2_err': r['KH_CO2_err'],
                       'KH_N2': r['KH_N2'], 'KH_N2_err': r['KH_N2_err'], 'dU_CO2': None,
                       'Qst_CO2_rt_corrected': r.get('Qst_CO2_rt_corrected'),
                       'selectivity': r.get('selectivity'), 'selectivity_err': r.get('selectivity_err')},
            'extra': {'set': 'mslm050', 'realization': k},
        })
    return out


if __name__ == '__main__':
    M.TARGETS = targets()
    M.RUNS = os.path.join(HERE, 'magi5_e14d_runs')
    M.OUT = os.path.join(HERE, f'results_magi5_e14d_offwidom_{M.MACHINE}.json')
    M.TEST = 'MAGI-005 E-14d mslm050 배치 평균 G (전하 OFF Widom)'
    M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop2 5차 E-14d'
    M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §laptop2 5차 예측((1) saIm050 배치 평균 4.381 과 1.5 배치 단위 안 · (2) G CV < S_ON CV)'
    if '--dry' in sys.argv:
        for t in M.TARGETS:
            print(t['name'], os.path.exists(t['cif']), t['extra'], round(t['on_ref']['selectivity'], 2))
        sys.exit(0)
    sys.exit(M.main())
