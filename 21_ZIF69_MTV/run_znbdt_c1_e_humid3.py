# -*- coding: utf-8 -*-
"""ZNBDT-C1 E 습윤 3성분 — laptop2. 등록 `ASSIGN_ZNBDT_C1_20261105.md` §1 'E 습윤 3성분' · §4 분담(70cee7bc).

`run_znbdt_e_humid3.py`(md5 9702366) 를 **무수정 import** 하고 두 가지만 바꿉니다.
  ① 대상: env ZNBDT_E_TARGETS = e24i_cch_open(열린 자리 4,8-(C≡CH)₂, charged_v3/e24i_cch_open_DDEC6.cif · HKHOME 작성)
  ② 결과 이름: 등록 §4 의 `results_znbdt_c1_*_<기기>.json` 에 맞춰 OUT · AUDIT 만 바꿈.
     기본 이름(results_znbdt_e_humid3_laptop2.json)은 MAGI-007 E 결과가 이미 차지해 래퍼가 착수를 거부하기 때문입니다.
조건 · 앵커 · 완주 표지 · 씨앗 · 막음 표(BLOCKS) · 반복 수(3)는 래퍼 그대로입니다. 래퍼 md5 가 다르면 착수하지 않습니다.
막음: 래퍼 BLOCKS 에는 e24i_c2h5_open 만 있으므로, HKHOME Zeo++ 가 이 구조에 주머니를 찾으면 이 실행기로 돌리지 않고 우편함에 적습니다.
"""
import os
import sys

os.environ['ZNBDT_E_TARGETS'] = 'e24i_cch_open'          # 래퍼가 import 때 읽으므로 import 전에 고정
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3 as E                             # noqa: E402

WANT = '9702366386edf93755c50d2527dbbe92'
if E.md5(os.path.abspath(E.__file__)) != WANT:
    sys.exit(f'  !! 래퍼 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(E.__file__))} ≠ {WANT})')

if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_c1_e_humid3_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_c1_e_humid3_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')

if __name__ == '__main__':
    sys.exit(E.main())
