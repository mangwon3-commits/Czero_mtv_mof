# -*- coding: utf-8 -*-
"""−C₂H₅ 열린 자리(e24i_c2h5_open) 323 K 막음 Widom — `e24i_bp_desktop.py`(e7acead8) 무수정 import 얇은 실행기. 2026-11-14 HKHOME.
왜: 323 K Widom(사용자 지시) 중 e24i_c2h5_open 은 통로 넷 중 둘이 닿지 않는 주머니라(구 4 · 1.65/1.82 Å) 차단 없음 값이 주머니 몫을 포함함.
    저장소 규칙(MAGI5_E22_VERDICT §15 · E-24b "판정의 뜻": 주머니가 있는 후보는 막음 Widom 뒤에만)대로 같은 온도의 막음판을 만듦.
바꾸는 것: rg.TEMP = 323 · 실행 폴더 e24i_bp_runs_323 · 결과 results_e24i_blockpockets_323_hkhome.json · 서술 참조를 같은 온도의 차단 없음 결과
(results_magi5_e3_e24i_c2h5_open_323_widom_hkhome.json)로. 입력 · 관문(막음 등식 · not-found · 'Pockets are blocked' · Simulation finished) · 막음 파일
(e24i_zeo_runs/e24i_c2h5_open/block1.65 · 1.82) 은 원판 그대로. 기계적 사실뿐 — 판정은 종합자.
"""
import hashlib
import json
import os
import sys

HERE = '/home/mangwon1/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
WANT = 'e7acead8'
_m = hashlib.md5(open(os.path.join(HERE, 'e24i_bp_desktop.py'), 'rb').read()).hexdigest()
if not _m.startswith(WANT):
    raise SystemExit(f'!! e24i_bp_desktop.py md5 {_m[:8]} ≠ {WANT}')
import e24i_bp_desktop as B   # noqa: E402

B.rg.TEMP = 323.0
B.BASE = os.path.join(HERE, 'e24i_bp_runs_323')
B.OUT = os.path.join(HERE, 'results_e24i_blockpockets_323_hkhome.json')


def ref323(tag):
    f = os.path.join(HERE, f'results_magi5_e3_{tag}_323_widom_hkhome.json')
    dd = json.load(open(f, encoding='utf-8'))
    rows = {x['charges']: x for x in dd['rows']}
    return {'file': os.path.basename(f), 'on': rows['on'], 'off': rows['off']}


B.unblocked_ref = ref323

if __name__ == '__main__':
    sys.argv = [sys.argv[0], '--tags', 'e24i_c2h5_open']
    rc = B.main()
    if os.path.exists(B.OUT):
        d = json.load(open(B.OUT, encoding='utf-8'))
        d['launcher'] = {'file': os.path.basename(__file__), 'md5': hashlib.md5(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
                         'imports': {'e24i_bp_desktop.py': _m}, 'temp_override_K': 323.0,
                         'why': '323 K Widom(사용자 지시 2026-11-14)의 −C₂H₅ 막음판 — 주머니 구 4(1.65 · 1.82)'}
        d['assign'] = '사용자 지시 2026-11-14 323 K Widom · 막음 규칙 MAGI5_E22_VERDICT §15'
        tmp = B.OUT + '.tmp'
        json.dump(d, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, B.OUT)
    sys.exit(rc)
