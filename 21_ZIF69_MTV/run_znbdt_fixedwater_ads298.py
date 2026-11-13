# -*- coding: utf-8 -*-
"""N 보강 — 물 수 고정 298 K 흡착만 추가 반복. 등록 `ASSIGN_N2_KPP_20261113.md` §1(자료 0건에서 씀).
`run_znbdt_fixedwater_wc.py`(0ed029a4)를 무수정 import 하고 조건 표를 ads298 한 줄로만 줄인다. 그 밖(입력 · 사이클 · 물 48분자 고정 · 표지 · 결과 형식)은 원판 그대로.
환경변수는 원판과 같다: FXW_MACHINE(필수 · 새 표지) · FXW_TAGS · FXW_WORKERS · FXW_CORE_CAP · FXW_SMOKE · FXW_ROOT."""
import sys

import run_znbdt_fixedwater_wc as fx

fx.CONDS = [c for c in fx.CONDS if c[0] == 'ads298']
assert len(fx.CONDS) == 1 and fx.CONDS[0] == ('ads298', 15000.0, 298.0, 2852.1), fx.CONDS

if __name__ == '__main__':
    sys.exit(fx.main())
