"""물 밀도 격자 (T-4·T-6) — **수정 힘장 계열(v3w)**. WATER_FIX_20260906 §3 ③ (선택).
run_density_water_v3.py 를 그대로 쓰되 출력·작업 폴더만 새 계열로(CLAUDE.md §3: 옛 폴더 이어받기 금지).
등록 덱: base · nbIm025 · saIm050, RH90, 초기화 5000 + 생산 15000, 90³ VTK. 단일 복셀 자리 주장은 금지(DENSITY_GRID_TWO_GENERATIONS).
사용: python run_density_water_v3w.py [base nbIm025 saIm050]
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_density_water_v3 as D
# 대상마다 프로세스를 따로 띄우므로(러너는 순차) JSON 충돌을 피해 DW_SUB 로 결과 폴더를 가른다 — 병합은 종합자가.
D.OUT = os.path.join(HERE, 'density_water_v3w', os.environ.get('DW_SUB', ''))
D.rw.HERE = D.OUT
D.rw.RUNS = os.path.join(HERE, 'water_runs_density_v3w')
# 확장 덱(T4_PRIME §7 등록, 09-07 06:5x): DW_EXTRA="saIm100,sa50nb50,nbIm075" 처럼 주면 등록 대상에 더한다.
if os.environ.get('DW_EXTRA'):
    D.TARGETS = list(D.TARGETS) + [t for t in os.environ['DW_EXTRA'].split(',') if t and t not in D.TARGETS]
os.makedirs(D.OUT, exist_ok=True)
if __name__ == '__main__':
    sys.exit(D.main())
