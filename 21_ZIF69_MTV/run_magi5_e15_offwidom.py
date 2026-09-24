# -*- coding: utf-8 -*-
"""MAGI-005 E-15 — CoRE 열역학 상위군의 G(골격 전하 OFF Widom). Junseok 몫.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §Junseok 5차 ② (2026-09-25 08:06, 자료 0건 — 예측 (1)~(4) 고정).
    (1) 3D 12행 G 중앙 ≥ 2 (기각 < 1.5) · (2) ρ(G, S_ON) 46행 ≥ 0.4 (기각 < 0, 부트스트랩 병기)
    (3) ASR/FSR 짝(같은 골격, anion_removed 없음) G 가 1.5 단위 안 (기각: 짝의 1/3 넘게 밖) · (4) 서술: 2D 중앙 G 대 3D 중앙 G.
판정문은 종합자가 씁니다 — 값과 표지만 냅니다.

자는 E-1·E-10 과 **같습니다** — `run_magi5_offwidom.py` 를 import 해 대상·출력·실행 뿌리·워커만 바꿉니다
(run_one_off · header_gate(골격 전하 비영 0 · LJ) · md5_gate · finished · 착수 간격 · seed 감사 그대로; 러너 파일은 안 고침).
대상 = core_pop_annotated.json 에서 S ≥ 65.2 · PLD ≥ 3.64 · E-1/E-10 OFF 없음 = 46행(3D 12 · 2D 34). S_ON = annotated 의 같은 자 값.
LPT = N_super(원자 수 × unit_cells()) 내림차순. CIF 는 core_pop_cifs.zip 에서 core_pop_cifs/(gitignore)로 꺼냄.
"""
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_magi5_offwidom as M  # noqa: E402
import run_aryl_gcmc as rg      # noqa: E402
from ase.io import read         # noqa: E402

S_MIN, PLD_MIN = 65.2, 3.64
E1 = {'2010_Zn__pts_3_ASR_1', '2012_Co__dia_3_ASR_3'}
E10 = {'2022_Cd__nuc_3_FSR_1', '2024_Zn__lig_3_ASR_1', '2024_Zn__srs_3_ASR_1', '2020_Ag__pts_3_ASR_1', '2014_Cu__bcu_3_ASR_2',
       '2019_Zn__pcu_3_ASR_6', '2017_Zn__dia_3_FSR_1', '2018_Cd__dia_3_ASR_5', '2019_Zn__pcu_3_ASR_1', '2021_Co__dia_3_ASR_1'}


def targets():
    ann = json.load(open(os.path.join(HERE, 'core_pop_annotated.json'), encoding='utf-8'))
    rows = ann.get('rows', ann) if isinstance(ann, dict) else ann
    rows = rows if isinstance(rows, list) else list(rows.values())
    z = zipfile.ZipFile(os.path.join(HERE, 'core_pop_cifs.zip'))
    cdir = os.path.join(HERE, 'core_pop_cifs')
    os.makedirs(cdir, exist_ok=True)
    out = []
    for r in rows:
        n = r['file'].replace('.cif', '')
        if not (r.get('KH_CO2') and r.get('KH_N2')):
            continue
        s_on = r['KH_CO2'] / r['KH_N2']
        if s_on < S_MIN or (r.get('PLD') or 0) < PLD_MIN or n in E1 | E10:
            continue
        cif = os.path.join(cdir, n + '.cif')
        if not os.path.exists(cif):
            open(cif, 'wb').write(z.read(n + '.cif'))
        at = read(cif)
        uc = rg.unit_cells(at)
        n_super = len(at) * uc[0] * uc[1] * uc[2]
        out.append({
            'name': n, 'cif': cif, 'key': r['key'], 'dim': r.get('dim'),
            'identity': '미확인(CoRE 행)',
            'identity_note': (f"annotated: formula {r.get('formula')} · topo {r.get('topo')} · metal {r.get('metal')} · "
                              f"flexible {r.get('flexible')} · anion_removed {r.get('anion_removed')} · LCD {r.get('LCD')} · PLD {r.get('PLD')}"),
            'on_ref': {'src': 'core_pop_annotated.json', 'KH_CO2': r['KH_CO2'], 'KH_CO2_err': r['KH_CO2_err'],
                       'KH_N2': r['KH_N2'], 'KH_N2_err': r['KH_N2_err'], 'dU_CO2': r.get('dU_CO2')},
            'extra': {'set': f"{r.get('dim')}D", 'series': r.get('series'), 'asr_fsr_pair': r.get('asr_fsr_pair'),
                      'anion_removed': r.get('anion_removed'), 'L': r.get('L'), 'PLD': r.get('PLD'), 'LCD': r.get('LCD'),
                      'S_ON_annotated': r.get('selectivity'), 'n_atoms': len(at), 'unit_cells': list(uc), 'N_super': n_super},
            '_n_super': n_super,
        })
    out.sort(key=lambda t: -t['_n_super'])            # LPT — 큰 상자 먼저
    for t in out:
        t.pop('_n_super')
    return out


if __name__ == '__main__':
    T = targets()
    n3 = sum(t['dim'] == 3 for t in T)
    print(f'E-15 대상 {len(T)}행 (3D {n3} · 2D {len(T) - n3}) · LPT 첫 셋 {[(t["name"], t["extra"]["N_super"]) for t in T[:3]]} · '
          f'마지막 {T[-1]["name"]} {T[-1]["extra"]["N_super"]}', flush=True)
    if len(T) != 46 or n3 != 12:
        print('!! 대상 수가 배정문(46 = 3D 12 · 2D 34)과 다름 — 착수 안 함', flush=True)
        sys.exit(2)
    M.TARGETS = T
    M.MACHINE = 'junseok'
    M.WORKERS = 10
    M.RUNS = os.path.join(HERE, 'magi5_e15_runs')
    M.OUT = os.path.join(HERE, 'results_magi5_e15_offwidom_junseok.json')
    M.TEST = 'MAGI-005 E-15 CoRE 열역학 상위군 전하 OFF Widom (G)'
    M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §Junseok 5차 ②'
    M.REG_REF = ('ASSIGN_MAGI5B_20260925.md §Junseok 5차 ② 예측: (1) 3D G 중앙 ≥ 2 · (2) ρ(G,S_ON) ≥ 0.4 · '
                 '(3) ASR/FSR 짝 G 1.5 단위 안 · (4) 2D 대 3D 서술')
    sys.exit(M.main())
