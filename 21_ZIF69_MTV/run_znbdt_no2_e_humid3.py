# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리 E 습윤 3성분 — HKHOME. 사용자 11-07 "일단 돌려". `run_znbdt_c1_e_humid3.py` 사본(바꾼 것: 대상 · 결과 이름 · 기기 기본 hkhome).

`run_znbdt_e_humid3.py`(md5 9702366) 를 **무수정 import** 하고 두 가지만 바꿉니다.
  ① 대상: env ZNBDT_E_TARGETS = e24i_no2_open(열린 자리 −NO₂, charged_v3/e24i_no2_open_DDEC6.cif md5 3a2a53ac · HKHOME 작성)
  ② 결과 이름: 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §6 의 `results_znbdt_no2_e_humid3_<기기>.json` 에 맞춰 OUT · AUDIT 만 바꿈.
  ③ (11-07 21:4x 추가) 착수 간격 60 s — 등록 §6 "착수 60 s 이상 간격" · laptop2 s4~s6 실행기와 같음. 반복 번호는 래퍼 기본 1 · 2 · 3(= 등록 s1~s3).
     기본 이름(results_znbdt_e_humid3_laptop2.json)은 MAGI-007 E 결과가 이미 차지해 래퍼가 착수를 거부하기 때문입니다.
조건 · 앵커 · 완주 표지 · 씨앗 · 막음 표(BLOCKS) · 반복 수(3)는 래퍼 그대로입니다. 래퍼 md5 가 다르면 착수하지 않습니다.
막음: 래퍼 BLOCKS 에 e24i_no2_open 을 아래에서 더함(물 1.30 구 4 · CO₂ · N₂ 구 0 — 같은 파일이 master 에 있어 laptop2 도 씀).
"""
import os
import sys

os.environ['ZNBDT_E_TARGETS'] = 'e24i_no2_open'
os.environ.setdefault('ZNBDT_E_MACHINE', 'hkhome')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3 as E                             # noqa: E402

# 막음(HKHOME 11-07 Zeo++ results_znbdt_no2_access_hkhome.json): 물 1.30 주머니 4 · CO₂ 1.65 · N₂ 1.82 는 구 0.
# 래퍼는 BLOCKS 대상이면 세 성분 모두에 BlockPockets 를 넣으므로 셋 다 줌 — CO₂ · N₂ 파일은 구 0(차단 없음과 같은 물리), 물만 구 4.
_ZB = os.path.join(HERE, 'znbdt_no2_zeo_runs', 'e24i_no2_open')
E.BLOCKS['e24i_no2_open'] = {
    'CO2': (os.path.join(_ZB, 'block1.65', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'N2': (os.path.join(_ZB, 'block1.82', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'water': (os.path.join(_ZB, 'block1.30', 'e24i_no2_open_relaxed.block'), '46b306e39cc368360e8e74d6459ad123')}

E.STAGGER = 60.0                                           # 등록 §6 착수 60 s 이상 간격(11-07 21:4x)

WANT = '9702366386edf93755c50d2527dbbe92'
if E.md5(os.path.abspath(E.__file__)) != WANT:
    sys.exit(f'  !! 래퍼 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(E.__file__))} ≠ {WANT})')

if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_no2_e_humid3_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_no2_e_humid3_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')

if __name__ == '__main__':
    sys.exit(E.main())
