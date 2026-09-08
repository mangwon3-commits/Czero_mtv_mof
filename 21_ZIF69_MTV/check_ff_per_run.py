"""실행 폴더 **하나하나**의 출력 머리말에서 물 힘장을 읽습니다 (09-07).

왜 따로 두는가 — 09-07 에 같은 유형의 결함이 셋 나왔습니다. 셋 다 **오류를
내지 않고 그럴듯한 수를 냅니다**:

    nbIm075 가 남은 미치환 Cl 6개를 집던 것          (랩탑, e16a600)
    죽은 .data 하나가 관문을 대신 통과시키던 것      (랩탑, 5c30af6)
    조각 2개짜리 사슬이 "블록 5" 로 Δ40 을 내던 것   (랩탑, 5c30af6)

**넷째가 여기 있습니다 — `run_density_water_v3w.py` 에는 힘장 관문이 아예
없습니다.** md5 도, `ZERO_POTENTIAL` 확인도, 산출물의 힘장 표기도 없습니다.
T-4′ 판정이 그 격자 위에 서 있는데 근거는 "런처가 맞는 RASPA_DIR 을 썼을
것" 뿐입니다. 09-05 에 **지역 힘장이 안 먹은 채 완주한 사례**가 실제로
있었으므로(`run_water_v3w.read_ff_header` 독스트링) 이것으로는 부족합니다.

자를 두 벌 두지 않습니다(`COMMS.md` ⑥ (가)) — 판정 함수는 만들지 않고
`ff_gate.read_ff_header` 를 **그대로 부릅니다**(09-07 오후부터 자는 `ff_gate.py` 한 자리).
다른 것은 하나뿐입니다: runs 뿌리가 아니라 **실행 폴더마다** 부릅니다.

    python check_ff_per_run.py water_runs_density_v3w water_runs_v3w
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 자는 `ff_gate.py` 한 자리에 있습니다(`FF_GATES_20260907.md`). 그 모듈은 프로젝트
# 안의 무엇도 import 하지 않으므로 여기서 불러도 경로가 새지 않습니다 — 09-07 에
# `run_water_v3w` 를 import 하던 판은 `run_water` 의 모듈 전역을 건드려, 전역을 떠
# 놓고 되돌리는 방어가 필요했습니다(랩탑이 `053a806` 으로 그쪽도 고쳤습니다).
from ff_gate import md5_gate, read_ff_header, OWOW_EPS, ZERO_PAIRS   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = ZERO_PAIRS
OWOW = OWOW_EPS


def verdict(chk):
    if not chk:
        return 'ff없음', '.data 안에 물 쌍 표가 없습니다 (미완주이거나 물이 없는 실행)'
    bad = [k for k in PAIRS if chk.get(k) != 'ZERO_POTENTIAL']
    eps = chk.get('OwOw_eps')
    if bad:
        return '결함판', f'{",".join(bad)} 가 ZERO_POTENTIAL 이 아닙니다 (수소에 LJ 가 붙음)'
    if eps is None or abs(eps - OWOW) >= 1e-3:
        return '다름', f'Ow-Ow eps {eps} != {OWOW}'
    return '통과', f'Hw/Lw none · Ow-Ow {eps}'


def finished(d):
    """완주 여부는 출력의 `Simulation finished` 로 셉니다 (파일 존재가 아니라)."""
    n = 0
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith('.data'):
                with open(os.path.join(root, fn), encoding='utf-8', errors='ignore') as f:
                    n += sum(1 for ln in f if 'Simulation finished' in ln)
    return n


def main(roots):
    rc = 0 if md5_gate()[0] else 1
    for r in roots:
        p = r if os.path.isabs(r) else os.path.join(HERE, r)
        print(f'\n=== {os.path.relpath(p, HERE)}')
        if not os.path.isdir(p):
            print('  (없음)')
            continue
        for name in sorted(os.listdir(p)):
            d = os.path.join(p, name)
            if not os.path.isdir(d):
                continue
            v, why = verdict(read_ff_header(d))
            fin = finished(d)
            flag = '  <- 확인 필요' if v in ('결함판', '다름') else ''
            if v in ('결함판', '다름'):
                rc = 1
            print(f'  {name:24s} 힘장 {v:5s} · 완주 {fin} · {why}{flag}')
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or ['water_runs_density_v3w', 'water_runs_v3w']))
