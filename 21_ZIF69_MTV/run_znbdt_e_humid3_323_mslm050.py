# -*- coding: utf-8 -*-
"""⑪ — ZIF 비교군 mslm050(e0) 의 323 K 습윤 3성분 선택도 3씨앗 · 랩탑.
등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §4-S [14:00 정정] · [14:01](종합자 COMMS/cloud.md 14:00 · 14:01 글).

laptop2 의 RT-E 실행기 `run_znbdt_e_humid3_323.py`(md5 7f83dc3c)를 **무수정 import** 하고, 대상 · 기기 · 폴더 · 결과 이름만 바꿉니다.
  ① 조건: RT-E 그대로 — import 한 실행기가 정한 값(323 K · 100 kPa · y 0.150000 / 0.738859 / 0.111141 · 5,000 + 15,000)을
     아래에서 다시 대조만 하고 바꾸지 않습니다. 단위셀은 래퍼의 규칙대로입니다.
  ② 대상: mslm050 하나. 전하 CIF `charged_v3/mslm050_DDEC6.cif` md5 2d5602c5 — 298 K E 기록
     `results_znbdt_e_humid3_laptop.json` 의 inputs.cifs 와 같은 값이어야 착수합니다.
  ③ 막음: 없음 — 298 K E 기록의 inputs.blocks 에 mslm050 이 없고 그 행의 block 도 비어 있습니다.
     import 한 실행기의 막음 표(−NO₂ 하나)에 mslm050 이 없음을 확인합니다.
  ④ 폴더: humid_wc_runs_v3w_323/znbdt_e3_323_mslm050_laptop/ · 반복 1~3 · 워커는 ZNBDT_E_WORKERS(배정 3).
  ⑤ 결과: results_znbdt_e_humid3_323_mslm050_laptop.json + _audit.json. import 한 실행기의 fix_header() 를 그대로 부른 뒤
     test · assign · launcher 세 칸만 이 판으로 다시 적고, 바꾼 칸을 launcher_fix2 에 남깁니다. 값 · 행 · 감사는 건드리지 않습니다.
완주 표지 · 앵커 · 씨앗 · 막음 감사는 래퍼 그대로입니다. 실행기 md5 · CIF md5 · 조건 가운데 하나라도 다르면 착수하지 않습니다.
"""
import json
import os
import sys

os.environ['ZNBDT_E_MACHINE'] = 'laptop'
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3_323 as R                          # noqa: E402
E = R.E

WANT_R = '7f83dc3c57f5c89d357d877664139e5d'
if E.md5(os.path.abspath(R.__file__)) != WANT_R:
    sys.exit(f'  !! RT-E 실행기 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(R.__file__))} ≠ {WANT_R})')
if E.MACHINE != 'laptop':
    sys.exit(f'  !! 기기 {E.MACHINE} — 착수 안 함')

BASE = 'mslm050'
WANT_CIF = '2d5602c54c74af6c805284596441b624'
_cif = os.path.join(HERE, 'charged_v3', f'{BASE}_DDEC6.cif')
if not os.path.exists(_cif) or E.md5(_cif) != WANT_CIF:
    sys.exit(f'  !! 전하 CIF {BASE} 없음 또는 md5 가 298 K 기록 {WANT_CIF[:8]} 와 다름 — 착수 안 함')
if BASE in E.BLOCKS:
    sys.exit(f'  !! 막음 표에 {BASE} 가 있음 — 298 K 기록(막음 없음)과 다름, 착수 안 함')

# ① 조건 대조(바꾸지 않음)
_c = E.hw.CONDITIONS
if not (len(_c) == 1 and _c[0][0] == 'ads' and _c[0][1] == 15000.0 and _c[0][2] == 323.0 and _c[0][3] == 12349.0):
    sys.exit(f'  !! 조건이 RT-E 와 다름 {_c} — 착수 안 함')
if abs(E.hw.P_H2O - 11114.1) > 1e-6 or E.Y != {'CO2': 0.15, 'N2': 0.738859, 'water': 0.111141} or E.P_TOT != 100000:
    sys.exit(f'  !! 분압 · 몰분율이 RT-E 와 다름 ({E.hw.P_H2O} · {E.Y} · {E.P_TOT}) — 착수 안 함')

# ② 대상 · ④ 폴더 · 작업
E.BASES = [BASE]
if E.SMOKE or E.DRY:
    E.ROOT = os.path.join(E.CHAIN, f"znbdt_e3_323_{BASE}_{'smoke' if E.SMOKE else 'dry'}_{E.MACHINE}")
else:
    E.ROOT = os.path.join(HERE, 'humid_wc_runs_v3w_323', f'znbdt_e3_323_{BASE}_{E.MACHINE}')
E.hw.RUNS = os.path.join(E.ROOT, 'runs')
E.hw.CHARGED = os.path.join(E.ROOT, 'cifs')
E.TAGS = [f'{b}_e3r{k}' for b in E.BASES for k in E.REPS_RUN]
E.hw.TARGETS = E.TAGS
E.JOBS = [(t, lab, p, T, ps) for t in E.TAGS for lab, p, T, ps in E.hw.CONDITIONS]

# ⑤ 결과
if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_e_humid3_323_{BASE}_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_e_humid3_323_{BASE}_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')


def fix_header2():
    if not os.path.exists(E.OUT):
        return
    d = json.load(open(E.OUT, encoding='utf-8'))
    old = {k: d.get(k) for k in ('test', 'assign', 'launcher')}
    d['test'] = 'ZIF 비교군 mslm050(e0) — 습윤 3성분 흡착점 S_humid,323(323 K · RH 90 %) · RT-E 조건'
    d['assign'] = 'ASSIGN_ZNBDT_REALTEMP_20261108.md §4-S [14:00 정정] · [14:01] ⑪(laptop2 에서 랩탑으로)'
    d['launcher'] = {'file': os.path.basename(__file__), 'md5': E.md5(os.path.abspath(__file__)),
                     'imports': {'file': os.path.basename(R.__file__), 'md5': WANT_R}}
    d['launcher_fix2'] = {'why': 'import 한 RT-E 실행기의 fix_header() 가 laptop2 RT-E 판 test · assign · launcher 를 씀 — 값 · 행 · 감사는 그대로',
                          'before': old}
    json.dump(d, open(E.OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)


if __name__ == '__main__':
    print(f'  ⑪ 대상 {E.BASES} · 기기 {E.MACHINE} · 조건 {E.hw.CONDITIONS} · y {E.Y} · 막음 표 {sorted(E.BLOCKS)} · 단계 {E.JOBS}', flush=True)
    rc = E.main()
    R.fix_header()
    fix_header2()
    sys.exit(rc)
