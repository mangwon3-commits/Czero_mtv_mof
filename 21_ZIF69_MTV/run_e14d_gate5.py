# -*- coding: utf-8 -*-
"""E-14d 관문 ⑤ — mslm050e1~e5. `risk_screen.run_one` 무수정 import, 판정식은 risk_screen.py:414~423 그대로
(PLD 전 > 3.3 · LCD 감소(ZIF-69 모체 7.63144 대비) < 20 % · AV/셀 > 20 · 최소거리 후 > 0.7). 바깥 루프 상한 12(관문 정의 그대로).
추적 파일 risk_results_v3sub.json 을 쓰지 않는다(09-25 01:51 덮어쓰기 재발 방지) — 출력 results_e14d_gate5_hkhome.json."""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import risk_screen as rs   # noqa: E402
REF = 7.63144
STAGE = os.path.join(HERE, 'e14d_stage'); rs.STRUCT = STAGE; rs.WORK = os.path.join(HERE, 'lmp_e14d')
OUT = os.path.join(HERE, 'results_e14d_gate5_hkhome.json')
if __name__ == '__main__':
    os.makedirs(STAGE, exist_ok=True); os.makedirs(rs.WORK, exist_ok=True)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {'rule': 'risk_screen.py:414~423, LCD_ref 7.63144, OUTER_LOOP_CAP 12', 'rows': {}}
    for t in [f'mslm050e{i}' for i in range(1, 6)]:
        if res['rows'].get(t, {}).get('status') == 'ok':
            continue
        shutil.copy(os.path.join(HERE, 'relax_v3', f'ZIF69_{t}_relaxed.cif'), os.path.join(STAGE, f'ZIF69_{t}.cif'))
        n, m0, m1, st = rs.run_one(t)
        row = {'status': st, 'before': m0, 'after': m1}
        if st == 'ok' and m1 and m1.get('LCD'):
            drop = (REF - m1['LCD']) / REF * 100
            checks = {'PLD': (m0['PLD'] or 0) > rs.CO2_KINETIC, 'LCD_drop': drop < rs.LCD_DROP_LIMIT,
                      'AV': (m0.get('AV_per_cell') or 0) > rs.AV_FLOOR, 'min_dist': m1['min_dist'] > rs.MIN_DIST_LIMIT}
            row.update({'LCD_drop_pct': round(drop, 2), 'checks': checks, 'pass': all(checks.values())})
        ed, loops = rs.final_ediff(t); row['final_EDiff'] = ed; row['outer_loops'] = loops
        res['rows'][t] = row
        json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(t, st, row.get('LCD_drop_pct'), row.get('pass'), flush=True)
    res['finished'] = True; json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
