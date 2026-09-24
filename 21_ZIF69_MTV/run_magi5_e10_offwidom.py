# -*- coding: utf-8 -*-
"""MAGI-005 E-10 — 전하 OFF 확장 Widom 20작업(가설 E-3-F1 시험). 랩탑(Melchior) 몫.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop E-10 (master d68d841b, 자료 0건 시점 예측 고정).
    A 군(순수 N 아졸레이트형 3D) 중앙 ln S_OFF/ln S_ON ≥ 0.8 · B 군(O 를 가진 3D 상위) 중앙 ≤ 0.6 · 구조별 0.6~0.8 판정 불가.
판정문은 종합자가 씁니다 — 값과 표지만 냅니다.

자는 E-1 과 **같습니다** — `run_magi5_offwidom.py` 를 import 해 대상·출력·실행 뿌리만 바꿉니다
(run_one_off · header_gate · md5_gate · 12 s 착수 간격 · seed 감사 그대로). ON 값은 `core_pop_annotated.json`(master) 에서 읽습니다.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_magi5_offwidom as M  # noqa: E402

SETS = {
    'A': ['2022_Cd__nuc_3_FSR_1', '2024_Zn__lig_3_ASR_1', '2024_Zn__srs_3_ASR_1',
          '2020_Ag__pts_3_ASR_1', '2014_Cu__bcu_3_ASR_2'],
    'B': ['2019_Zn__pcu_3_ASR_6', '2017_Zn__dia_3_FSR_1', '2018_Cd__dia_3_ASR_5',
          '2019_Zn__pcu_3_ASR_1', '2021_Co__dia_3_ASR_1'],
}


def targets():
    ann = json.load(open(os.path.join(HERE, 'core_pop_annotated.json'), encoding='utf-8'))
    rows = ann.get('rows', ann) if isinstance(ann, dict) else ann
    rows = rows if isinstance(rows, list) else list(rows.values())
    by = {r['file']: r for r in rows}
    out = []
    # LPT: 원자 수 × 셀수가 큰 것부터 — 여기서는 작업 20개·워커 8 이라 순서 영향이 작아 파일 순서대로 둔다(비 = 최장/합÷워커 작음).
    for s, names in SETS.items():
        for n in names:
            r = by[n + '.cif']
            out.append({
                'name': n, 'cif': os.path.join(HERE, 'core_pop_cifs', n + '.cif'), 'key': r['key'], 'dim': r.get('dim'),
                'identity': '미확인(CoRE 행)',
                'identity_note': (f"annotated: formula {r.get('formula')} · topo {r.get('topo')} · metal {r.get('metal')} · "
                                  f"flexible {r.get('flexible')} · anion_removed {r.get('anion_removed')} · LCD {r.get('LCD')} · PLD {r.get('PLD')}"),
                'on_ref': {'src': 'core_pop_annotated.json', 'KH_CO2': r['KH_CO2'], 'KH_CO2_err': r['KH_CO2_err'],
                           'KH_N2': r['KH_N2'], 'KH_N2_err': r['KH_N2_err'], 'dU_CO2': r.get('dU_CO2')},
                'extra': {'set': s},
            })
    return out


if __name__ == '__main__':
    M.TARGETS = targets()
    M.RUNS = os.path.join(HERE, 'magi5_e10_runs')
    M.OUT = os.path.join(HERE, f'results_magi5_e10_offwidom_{M.MACHINE}.json')
    M.TEST = 'MAGI-005 E-10 전하 OFF 확장 Widom (가설 E-3-F1)'
    M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop E-10'
    M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §laptop E-10 예측(A 중앙 ≥ 0.8 · B 중앙 ≤ 0.6)'
    sys.exit(M.main())
