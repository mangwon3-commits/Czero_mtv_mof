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
`run_water_v3w.read_ff_header` 를 **그대로 부릅니다.** 다른 것은 하나뿐입니다:
runs 뿌리가 아니라 **실행 폴더마다** 부릅니다.

    python check_ff_per_run.py water_runs_density_v3w water_runs_v3w
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ⚠️ **이 파일을 러너 안에서 import 하지 마십시오. 명령줄로만 부르십시오.**
#
#   `run_water_v3w` 와 `run_density_water_v3` 는 **둘 다 `import run_water as rw`**
#   를 하고 **모듈 전역** `rw.HERE` · `rw.RUNS` · `rw.CHARGED` 를 자기 계열로
#   덮어씁니다. 그래서 밀도 계열 프로세스가 `run_water_v3w` 를 한 번 import 하면
#   그 순간 **밀도 실행이 물 계열 폴더(`v3w_water/`·`water_runs_v3w/`)로 샙니다** —
#   오류 없이, 조용히. (09-07 에 밀도 러너에 관문을 넣으려다 이 지뢰를 밟을 뻔했습니다.)
#
#   여기서는 import 전후로 그 전역을 **떠 놓고 되돌립니다.** 이 파일 자체는
#   안전하지만, 러너 안에서 부르는 것은 여전히 권하지 않습니다.
import run_water as _rw                            # noqa: E402
_KEYS = ('HERE', 'RUNS', 'CHARGED', 'WATER_DEF', 'RH_LIST', 'MAX_WORKERS', 'TARGETS')
_SAVED = {k: getattr(_rw, k, None) for k in _KEYS}
from run_water_v3w import read_ff_header, FF_MD5, FF_PATH   # noqa: E402  (자를 빌려 옵니다)
for _k, _v in _SAVED.items():                      # 훔쳐 온 자만 갖고 전역은 되돌립니다
    setattr(_rw, _k, _v)

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS = ('HwHw', 'OwHw', 'OwLw', 'LwLw')
OWOW = 89.633                                     # WATER_FIX_20260906.md §1


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


def md5_gate():
    """**파일 관문** — 공용 힘장 파일이 그 파일인가 (착수 **전**에 답합니다).

    머리말 관문과 **다른 것을 잡습니다**(`FF_GATES_20260907.md`):
        파일 관문    파일이 맞는가         <- 공용 힘장이 바뀌었나
        머리말 관문  RASPA 가 그걸 읽었나  <- 지역 사본·경로가 가로챘나 (09-05 사례)
    """
    if not os.path.exists(FF_PATH):
        print(f'  [파일 관문] **못 찾음** {FF_PATH}')
        return False
    m = hashlib.md5(open(FF_PATH, 'rb').read()).hexdigest()
    ok = (m == FF_MD5)
    print(f'  [파일 관문] {FF_PATH}\n              md5 {m}  '
          f'({"**일치**" if ok else f"**불일치 — 기대 {FF_MD5}**"})')
    return ok


def main(roots):
    rc = 0 if md5_gate() else 1
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
