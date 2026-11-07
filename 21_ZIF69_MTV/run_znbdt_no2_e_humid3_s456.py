# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리 E 습윤 3성분 s4~s6 — laptop2. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §6 · §7(종합자 21:1x · 6시간 위임).

laptop2 자기 E 래퍼 `run_znbdt_e_humid3.py`(md5 9702366) 를 **무수정 import** 하고 아래만 바꿉니다.
  ① 대상: env ZNBDT_E_TARGETS = e24i_no2_open(charged_v3/e24i_no2_open_DDEC6.cif · 등록 md5 3a2a53ac — 다르면 착수 거부)
  ② 막음: HKHOME `run_znbdt_no2_e_humid3.py` 와 **같은 표**(같은 파일 · 같은 md5). 물 1.30 주머니 4 · CO₂ 1.65 · N₂ 1.82 는 구 0.
     래퍼는 BLOCKS 대상이면 세 성분 모두에 BlockPockets 를 넣으므로 셋 다 줍니다(CO₂ · N₂ 파일은 구 0 — 막음 없음과 같은 물리).
  ③ 반복 번호 4 · 5 · 6(등록 §6 "laptop2 s4~s6") — 실행 폴더 · CIF 사본 이름이 HKHOME 의 r1~r3 과 갈립니다.
  ④ 착수 간격 60 s(등록 §6 "60 s 이상") · 결과 이름 results_znbdt_no2_e_humid3_laptop2.json(등록 §6).
조건 · 앵커 · 완주 표지 · 씨앗(착수 초) · 막음 감사는 래퍼 그대로입니다. 래퍼 md5 가 다르면 착수하지 않습니다.
"""
import hashlib
import os
import sys

os.environ['ZNBDT_E_TARGETS'] = 'e24i_no2_open'
os.environ.setdefault('ZNBDT_E_MACHINE', 'laptop2')
os.environ.setdefault('ZNBDT_E_WORKERS', '3')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3 as E                             # noqa: E402

WANT = '9702366386edf93755c50d2527dbbe92'
if E.md5(os.path.abspath(E.__file__)) != WANT:
    sys.exit(f'  !! 래퍼 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(E.__file__))} ≠ {WANT})')
CIF = os.path.join(HERE, 'charged_v3', 'e24i_no2_open_DDEC6.cif')
if not os.path.exists(CIF) or not E.md5(CIF).startswith('3a2a53ac'):
    sys.exit(f'  !! 전하 CIF 없음 또는 md5 가 등록 3a2a53ac 와 다름 — 착수 안 함')

_ZB = os.path.join(HERE, 'znbdt_no2_zeo_runs', 'e24i_no2_open')
E.BLOCKS['e24i_no2_open'] = {
    'CO2': (os.path.join(_ZB, 'block1.65', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'N2': (os.path.join(_ZB, 'block1.82', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'water': (os.path.join(_ZB, 'block1.30', 'e24i_no2_open_relaxed.block'), '46b306e39cc368360e8e74d6459ad123')}

E.STAGGER = 60.0
if not (E.SMOKE or E.DRY):
    E.REPS_RUN = [4, 5, 6]
E.TAGS = [f'{b}_e3r{k}' for b in E.BASES for k in E.REPS_RUN]
E.hw.TARGETS = E.TAGS
E.JOBS = [(t, lab, p, T, ps) for t in E.TAGS for lab, p, T, ps in E.hw.CONDITIONS]

if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_no2_e_humid3_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_no2_e_humid3_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')

if __name__ == '__main__':
    sys.exit(E.main())
