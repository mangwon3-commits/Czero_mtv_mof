# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리(e24i_no2_open) 작동점 S_mix 298 K 3씨앗 — 사용자 11-07 "일단 돌려"(등록 보완은 첫 결과 읽기 전 · CLAUDE.md §2 09-06 결정).
`run_znbdt_c2_mix.py` 와 같은 꼴: `run_e24i_mix.py` 를 그대로 import(그 안에서 run_tj1_mix 무수정)하고 실행 폴더 · 출력 · 기록 문구만 바꿈.
규약: CO₂/N₂ 0.15/0.85 · 100 kPa · 298 K · 5,000+15,000 · 착수 15 s 간격 — −CN · C2 와 같음. 차단 없는 구조 전용(Zeo++ 구 0 확인 뒤 띄움).
S_Henry 열: Widom ON 결과가 있으면 그 값, 없으면 자리 채움 1.0(비 인용 금지 — run_e24i_mix 규칙)."""
import os, sys
os.environ['E24G_TAG'] = 'e24i_no2_open'
os.environ.setdefault('E24G_MACHINE', 'hkhome')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_e24i_mix as R          # noqa: E402
M = R.M; TAG = R.TAG
M.RUNS = os.path.join(HERE, 'znbdt_no2_mix_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_no2_mix_{M.MACHINE}.json')
M.TEST = 'ZNBDT −NO₂ 열린 자리 작동점 S_mix 298 K 3씨앗'
M.ASSIGN_REF = '사용자 11-07 "일단 돌려" · 사슬 틀 ASSIGN_ZNBDT_C1_20261105.md §1'
M.REG_REF = '등록 보완 대기(종합자 · 첫 결과 읽기 전)'
if __name__ == '__main__':
    for p in (M.RUNS, M.OUT):
        if os.path.exists(p):
            sys.exit(f'!! 이전 산출 있음: {p} — 착수 안 함(이어받기 섞임 방지)')
    sys.exit(M.main())
