# -*- coding: utf-8 -*-
"""Zn(bib)(bdtdc) E 습윤 3성분 보강 s4~s6 — 모체 · −CH₃ 열린 자리 · laptop2. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §7 추가(23:3x · 순찰 5) ⑧.

laptop2 자기 E 래퍼 `run_znbdt_e_humid3.py`(md5 9702366) 를 **무수정 import** 하고 아래만 바꿉니다.
  ① 대상: env ZNBDT_E_TARGETS = e22_parent,e24i_ch3_open — s1~s3(`results_znbdt_e_humid3_laptop2.json`)과 같은 전하 CIF
     (charged_v3/e22_parent_DDEC6.cif f15ce100 · charged_v3/e24i_ch3_open_DDEC6.cif a8e6a165 — 다르면 착수 거부).
  ② 막음: 없음(두 대상 모두 래퍼 BLOCKS 표 밖 — s1~s3 와 같음).
  ③ 반복 번호 4 · 5 · 6 — 실행 폴더 · CIF 사본 이름이 s1~s3 과 갈립니다. 씨앗 = 착수 초라 s1~s3(11-04)와 겹치지 않습니다.
  ④ 결과 이름 results_znbdt_e_humid3_s456_laptop2.json(등록 §7 ⑧). 워커 · 착수 간격은 래퍼 기본(6 · 15 s) — s1~s3 와 같음.
조건 · 앵커 · 완주 표지 · 씨앗 · 감사는 래퍼 그대로입니다. 래퍼 md5 가 다르면 착수하지 않습니다.
"""
import os
import sys

os.environ['ZNBDT_E_TARGETS'] = 'e22_parent,e24i_ch3_open'
os.environ.setdefault('ZNBDT_E_MACHINE', 'laptop2')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3 as E                             # noqa: E402

WANT = '9702366386edf93755c50d2527dbbe92'
if E.md5(os.path.abspath(E.__file__)) != WANT:
    sys.exit(f'  !! 래퍼 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(E.__file__))} ≠ {WANT})')
CIFS = {'e22_parent': 'f15ce100dbbaa49714fdb2e5dabfe9ff', 'e24i_ch3_open': 'a8e6a165aaa036205631d834ec82f6bb'}
for b, want in CIFS.items():
    p = os.path.join(HERE, 'charged_v3', f'{b}_DDEC6.cif')
    if not os.path.exists(p) or E.md5(p) != want:
        sys.exit(f'  !! 전하 CIF {b} 없음 또는 md5 가 s1~s3 기록 {want[:8]} 와 다름 — 착수 안 함')
assert not any(b in E.BLOCKS for b in CIFS), '막음 표에 대상이 있음 — s1~s3 와 다른 조건'

if not (E.SMOKE or E.DRY):
    E.REPS_RUN = [4, 5, 6]
E.TAGS = [f'{b}_e3r{k}' for b in E.BASES for k in E.REPS_RUN]
E.hw.TARGETS = E.TAGS
E.JOBS = [(t, lab, p, T, ps) for t in E.TAGS for lab, p, T, ps in E.hw.CONDITIONS]

if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_e_humid3_s456_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_e_humid3_s456_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')

if __name__ == '__main__':
    sys.exit(E.main())
