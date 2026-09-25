# -*- coding: utf-8 -*-
"""E-18 셀 자유 이완 도구 — 관문 ⑤ 의 LAMMPS UFF4MOF box/relax 경로를 **구조 산출용**으로 재사용.

등록: `ASSIGN_MAGI5B_20260925.md §HKHOME 3차 E-18`(자료 0건) · 사용자 결정 5번(`MAGI5_USER_DECISIONS_20260925.md`).
`risk_screen.run_one` 을 **수정 없이** import 해 전역만 바꾼다(STRUCT = 스테이징, WORK = lmp_e18, 바깥 루프 상한 50).
관문 ⑤ 결과 파일(risk_results_*.json)은 쓰지 않는다 — 09-25 01:51 관문 ⑤ 사슬이 추적 파일을 덮어쓴 일의 재발 방지.

검증 관문(먼저): CALF-20 이완 셀이 실험 셀(CCDC 2084733, 입력 CIF 셀) 대비 a·b·c 각 ≤ 3 % · 부피 ≤ 5 %.
"""
import json, os, shutil, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import risk_screen as rs                      # noqa: E402
from ase.io import read, write                # noqa: E402

TAGS = {
    'calf20':   'external_cif/CALF20_Zn2tz2ox_guestfree_P1.cif',
    'mof16c11': 'external_cif/IISERPMOF16_ZnDamtzHCOO_ordered_P1.cif',
    'mof16c12': 'external_cif/IISERPMOF16_ZnDamtzHCOO_orderedC12_P1.cif',
}
STAGE = os.path.join(HERE, 'e18_stage'); OUT = os.path.join(HERE, 'results_e18_cellrelax_hkhome.json')
rs.STRUCT = STAGE; rs.WORK = os.path.join(HERE, 'lmp_e18'); rs.OUTER_LOOP_CAP = 50


def cellpar_per_rep(before, after):
    """lammps-interface 가 복제한 초격자를 축별 정수배로 나눠 원 셀 환산."""
    cb, ca = before.cell.cellpar(), after.cell.cellpar()
    reps = [max(1, int(round(ca[i] / cb[i]))) for i in range(3)]
    per = [ca[i] / reps[i] for i in range(3)] + list(ca[3:])
    vol = after.get_volume() / np.prod(reps)
    return reps, per, vol


if __name__ == '__main__':
    tags = sys.argv[1:] or ['calf20']
    os.makedirs(STAGE, exist_ok=True); os.makedirs(rs.WORK, exist_ok=True)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for t in tags:
        src = os.path.join(HERE, TAGS[t]); shutil.copy(src, os.path.join(STAGE, f'ZIF69_{t}.cif'))
        before = read(src)
        name, m0, m1, st = rs.run_one(t)
        row = {'tag': t, 'src': TAGS[t], 'status': st, 'zeo_before': m0, 'zeo_after': m1}
        ed, loops = rs.final_ediff(t); row['final_EDiff'] = ed; row['outer_loops'] = loops
        dat = os.path.join(rs.WORK, t, f'min_{t}.data')
        if st == 'ok' and os.path.exists(dat):
            after = read(dat, format='lammps-data', style='full')
            rep = max(1, len(after) // len(before))
            after.set_chemical_symbols(list(before.get_chemical_symbols()) * rep)
            reps, per, vol = cellpar_per_rep(before, after)
            cb = before.cell.cellpar()
            row.update({'reps': reps, 'cell_before': [round(x, 4) for x in cb], 'cell_after_per_cell': [round(x, 4) for x in per],
                        'd_abc_pct': [round(100 * (per[i] - cb[i]) / cb[i], 2) for i in range(3)],
                        'd_angles_deg': [round(per[i] - cb[i], 2) for i in range(3, 6)],
                        'vol_before': round(before.get_volume(), 2), 'vol_after_per_cell': round(vol, 2),
                        'd_vol_pct': round(100 * (vol - before.get_volume()) / before.get_volume(), 2)})
            out_cif = os.path.join(HERE, 'relax_e18', f'{t}_uff4mof_cellrelaxed.cif'); os.makedirs(os.path.dirname(out_cif), exist_ok=True)
            write(out_cif, after); row['out_cif'] = os.path.relpath(out_cif, HERE)
            if t == 'calf20':
                ok = all(abs(x) <= 3.0 for x in row['d_abc_pct']) and abs(row['d_vol_pct']) <= 5.0
                row['validation_gate'] = {'rule': 'a,b,c ≤ 3 % · V ≤ 5 % vs 실험 셀(CCDC 2084733)', 'pass': ok}
        res[t] = row
        json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(json.dumps(row, ensure_ascii=False)[:900], flush=True)
