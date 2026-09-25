# -*- coding: utf-8 -*-
"""E-22b 관문 ⑤ — Zn(bib)(bdtdc) 계열(사용자 결정 4 (다) 치환 조성 갈래: 기준 = 무치환 모체 e22_parent 를 같은 처리한 뒤 LCD). `risk_screen.run_one` 무수정 import, 판정식은 risk_screen.py:414~423 그대로
(PLD 전 > 3.3 · LCD 감소(ZIF-69 모체 7.63144 대비) < 20 % · AV/셀 > 20 · 최소거리 후 > 0.7). 바깥 루프 상한 12(관문 정의 그대로).
추적 파일 risk_results_v3sub.json 을 쓰지 않는다(09-25 01:51 덮어쓰기 재발 방지) — 출력 results_e14d_gate5_hkhome.json."""
import json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import risk_screen as rs   # noqa: E402
REF = 7.63144
STAGE = os.path.join(HERE, 'e22_stage'); rs.STRUCT = STAGE; rs.WORK = os.path.join(HERE, 'lmp_e22')
OUT = os.path.join(HERE, 'results_e22b_gate5_hkhome.json')
if __name__ == '__main__':
    os.makedirs(STAGE, exist_ok=True); os.makedirs(rs.WORK, exist_ok=True)
    res = json.load(open(OUT)) if os.path.exists(OUT) else {'rule': 'risk_screen.py:414~423, LCD_ref = e22_parent 같은 처리 뒤 LCD(사용자 결정 4 (다)), OUTER_LOOP_CAP 12', 'rows': {}}
    global REF
    for t in ['e22_parent', 'e22_no2_050', 'e22_no2_100']:          # 모체 먼저 — 그 이완 후 LCD 가 기준
        if res['rows'].get(t, {}).get('status') == 'ok':
            if t == 'e22_parent': REF = res['rows'][t]['after']['LCD']
            continue
        shutil.copy(os.path.join(HERE, 'relax_tnf', f'{t}_relaxed.cif'), os.path.join(STAGE, f'ZIF69_{t}.cif'))
        n, m0, m1, st = rs.run_one(t)
        row = {'status': st, 'before': m0, 'after': m1}
        if t == 'e22_parent' and st == 'ok' and m1 and m1.get('LCD'):
            REF = m1['LCD']; res['LCD_ref_family'] = REF
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
