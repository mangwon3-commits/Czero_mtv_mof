# -*- coding: utf-8 -*-
"""E-24 관문 ⑤ — 형판 Zn(bib)(bdtdc) 4,8-치환 설계 후보(−CH₃ · −C≡N · −F). run_e22_gate5.py 와 같은 규칙(사용자 결정 4 (다) 치환 조성 갈래):
기준 LCD = e22_parent 를 같은 UFF4MOF 처리한 뒤 LCD — `results_e22b_gate5_hkhome.json` 의 값(5.24089)을 그대로 읽음(모체 재계산 안 함).
`risk_screen.run_one` 무수정 import, 판정식 risk_screen.py:414~423 그대로. 추적 파일 risk_results_* 안 씀. **RASPA 가 도는 기기에서 띄우지 말 것**(Zeo++ — CLAUDE.md §5).
사용: python run_e24_gate5.py  → results_e24_gate5_<host>.json"""
import json, os, shutil, socket, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import risk_screen as rs   # noqa: E402
REF = json.load(open(os.path.join(HERE, 'results_e22b_gate5_hkhome.json')))['rows']['e22_parent']['after']['LCD']
STAGE = os.path.join(HERE, 'e24_stage'); rs.STRUCT = STAGE; rs.WORK = os.path.join(HERE, 'lmp_e24')
OUT = os.path.join(HERE, f'results_e24_gate5_{socket.gethostname().lower()}.json')
TAGS = ['e24_ch3_100', 'e24_cn_100', 'e24_f_100']
if __name__ == '__main__':
    os.makedirs(STAGE, exist_ok=True); os.makedirs(rs.WORK, exist_ok=True)
    res = {'rule': 'risk_screen.py:414~423, LCD_ref = e22_parent 같은 처리 뒤 LCD(사용자 결정 4 (다)) — results_e22b_gate5_hkhome.json', 'LCD_ref_family': REF, 'rows': {}}
    for t in TAGS:
        shutil.copy(os.path.join(HERE, 'relax_tnf', f'{t}_relaxed.cif'), os.path.join(STAGE, f'ZIF69_{t}.cif'))
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
