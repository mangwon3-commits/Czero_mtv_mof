"""후보 습윤 ⑨ — 데스크탑 (MAGI-002 §6-5 ⑨, ASSIGN_20260907 §F-2). `run_water_v3w.py` 를 그대로 쓰고
등록 목록에 `sa25nb75`·`ms50nb50` 을 더하며 **RH 를 [0.0, 0.9]** 로 둡니다(두 조성 다 수정 힘장 RH0 분모가 없음).
작업 넷(2 조성 × 2 RH)이 한 번에 뜨므로 단계 분리는 필요 없습니다(랩탑 T-MTV-2w 의 순서 함정은 작업 수 > 워커 수일 때).

    V3W_SUFFIX=_cand python run_water_v3w_cand_desktop.py --only sa25nb75 ms50nb50 mslm025   # 6작업, 워커 4 → 2파도
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_water_v3w as v3w
_wire = v3w.wire
def wire():
    _wire()
    have = {n for n, _ in v3w.rw.TARGETS}
    for n, label in (('sa25nb75', 'SO3H 25% + NO2 75% (후보 ⑨)'), ('ms50nb50', 'SO2CH3 50% + NO2 50% (후보 ⑨)'),
                     ('mslm025', 'SO2CH3 25% — 구경 창(4.3~4.8 Å) 안의 비양성자성 술포닐 (⑩, 랩탑 §6-13 등록)')):
        if n not in have:
            v3w.rw.TARGETS = list(v3w.rw.TARGETS) + [(n, label)]
    v3w.rw.RH_LIST = [0.0, 0.9]          # RH0 분모 함께
    v3w.rw.MAX_WORKERS = int(os.environ.get("V3W_WORKERS", "4"))
v3w.wire = wire
if __name__ == '__main__':
    sys.exit(v3w.main())
