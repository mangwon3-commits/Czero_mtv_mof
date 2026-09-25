# -*- coding: utf-8 -*-
"""MAGI-005 E-14c — 배치 산포 속 G: sa50nb50 대 saIm050 앙상블 각 5 실현의 전하 OFF Widom 20작업. laptop2(Balthasar) 몫.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop2 4차 (자료 0건 시점 예측 고정).
    (1) 배치 평균 G(sa50nb50) − G(saIm050) ≥ 1.5 배치 단위(분모 = 두 군 실현 SD 의 합성) — 기각 < 1.5
    (2) G 의 실현 간 CV < S_ON 의 CV (두 군 모두) — 기각: 한 군이라도 G CV ≥ S_ON CV
판정문은 종합자가 씁니다 — 값과 표지만 냅니다.

자는 E-1·E-10 과 **같습니다** — `run_magi5_offwidom.py` 를 import 해 대상·출력·실행 뿌리만 바꿉니다
(run_one_off · header_gate · md5_gate · 착수 간격 · seed 감사 그대로). ON 값은 `results_v3ens_mix10.json` 의 같은 이름 행(같은 자 Widom).
실현 0(원판)은 여기서 돌리지 않습니다 — E-14b(sa50nb50)·E-1(saIm050) 값을 판정 때 더해 각 n = 6.
    ⚠ 실현 0 의 OFF 방식: E-1 은 이 러너(UseChargesFromCIFFile no), E-14b 는 run_magi5_widom.py(CIF 전하 0 사본) — 두 방식은
      골격–흡착질 정전기 0 이라는 같은 자(각 파일 머리 설명)이지만 **다른 코드 경로**라 행에 병기합니다.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_magi5_offwidom as M  # noqa: E402

SETS = {
    'sa50nb50': ['sa50nb50e1', 'sa50nb50e2', 'sa50nb50e3', 'sa50nb50e4', 'sa50nb50e5'],
    'saIm050': ['saIm050e1', 'saIm050e2', 'saIm050e3', 'saIm050e4', 'saIm050e5'],
}
RISK = {'sa50nb50': 'risk_results_v3ens50nb50.json', 'saIm050': 'risk_results_v3ens0500.json'}


def _rows(path):
    d = json.load(open(os.path.join(HERE, path), encoding='utf-8'))
    rows = d.get('rows', d) if isinstance(d, dict) else d
    return rows if isinstance(rows, list) else list(rows.values())


def _gate(set_name, n):
    """관문 ⑤ 표지 — risk 파일의 같은 이름 행(없으면 '미확인'). status 는 계산 표지(CLAUDE.md §2) — 막지 않고 적기만."""
    try:
        for r in _rows(RISK[set_name]):
            if json.dumps(r, ensure_ascii=False).find(f'"{n}') >= 0 or r.get('name') == n:
                return {k: r.get(k) for k in ('name', 'pass', 'LCD', 'LCD_drop_pct', 'status') if k in r}
    except Exception as e:  # noqa: BLE001
        return {'error': str(e)[:120]}
    return '미확인'


def targets():
    by = {r['name']: r for r in _rows('results_v3ens_mix10.json')}
    out = []
    for s, names in SETS.items():
        for k, n in enumerate(names, 1):
            r = by[n]
            out.append({
                'name': f'{n}_DDEC6', 'cif': os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), 'key': n, 'dim': 3,
                'identity': f'우리 v3 앙상블 실현({s} e{k}, ZIF-69 gme)',
                'identity_note': f'관문 ⑤ 표지 {RISK[s]}: {_gate(s, n)}',
                'on_ref': {'src': 'results_v3ens_mix10.json', 'KH_CO2': r['KH_CO2'], 'KH_CO2_err': r['KH_CO2_err'],
                           'KH_N2': r['KH_N2'], 'KH_N2_err': r['KH_N2_err'], 'dU_CO2': None,
                           'Qst_CO2_rt_corrected': r.get('Qst_CO2_rt_corrected'),
                           'selectivity': r.get('selectivity'), 'selectivity_err': r.get('selectivity_err')},
                'extra': {'set': s, 'realization': k},
            })
    return out


if __name__ == '__main__':
    M.TARGETS = targets()
    M.RUNS = os.path.join(HERE, 'magi5_e14c_runs')
    M.OUT = os.path.join(HERE, f'results_magi5_e14c_offwidom_{M.MACHINE}.json')
    M.TEST = 'MAGI-005 E-14c 배치 산포 속 G (sa50nb50 대 saIm050, 전하 OFF Widom)'
    M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop2 4차 E-14c'
    M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §laptop2 4차 예측((1) 배치 평균 G 차 ≥ 1.5 배치 단위 · (2) G CV < S_ON CV)'
    if '--dry' in sys.argv:
        for t in M.TARGETS:
            print(t['name'], os.path.exists(t['cif']), t['extra'], round(t['on_ref']['selectivity'], 2), t['identity_note'][:110])
        sys.exit(0)
    sys.exit(M.main())
