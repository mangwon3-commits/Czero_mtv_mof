"""씨앗 반복 B — 데스크탑 판 (`ASSIGN_20260907.md §B-1`). `run_water_v3w.py` 를 그대로 쓰고
**등록 목록에 `base` · `nbIm025` 를 더하는 것**만 합니다. 설정은 하나도 안 적습니다.

왜 래퍼인가: `run_water_v3w.py` 의 `--only` 는 "§4 목록만 돕니다" 라고 막습니다 — 옳은 관문입니다.
B 는 `ASSIGN_20260907.md §B` 에 등록됐지만 그 목록(WATER_FIX §4)에는 없는 두 조성이라, 그 관문을
**등록 문서를 가리키며** 넘습니다. 이 파일 없이 `run_water_v3w.py` 를 고치면 랩탑이 오늘 고치는
파일과 충돌합니다.

    V3W_SUFFIX=_rep_base     python run_water_v3w_rep_desktop.py --only base
    V3W_SUFFIX=_rep_nbIm025  python run_water_v3w_rep_desktop.py --only nbIm025

**두 조성을 한 드라이버로 띄우지 않습니다** — 같은 초에 시작하면 같은 씨앗입니다(오늘 A 가 고친 그 충돌).
접미사를 조성별로 갈라 결과 파일 경쟁도 없앱니다. 짝(같은 기기·같은 프로토콜의 원 실행)은
데스크탑 밀도 격자 계열 `water_runs_density_v3w/rh90_{base,nbIm025}` — 밀도 러너는 `run_water` 위에
VTK 출력만 얹은 것이라 표본 추출은 같습니다(그래도 판정문에 "짝은 밀도 계열" 을 병기).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_water_v3w as v3w          # noqa: E402  (053a806 뒤라 import 부작용 없음)

_wire = v3w.wire


def wire():
    _wire()
    have = {n for n, _ in v3w.rw.TARGETS}
    for n, label in (('base', '모체 (씨앗 반복 B)'), ('nbIm025', 'NO2 25% (씨앗 반복 B)')):
        if n not in have:
            v3w.rw.TARGETS = list(v3w.rw.TARGETS) + [(n, label)]


v3w.wire = wire                       # main() 이 이름으로 부르므로 여기서 바꾸면 먹습니다

if __name__ == '__main__':
    sys.exit(v3w.main())
