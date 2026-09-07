#!/usr/bin/env python
"""**T-MTV-2w** — 혼합(sa50nb50)의 **습윤 배치 단위**를 잽니다 (`MAGI-002 §6-9-1` 등록분).

왜 이 계산이 있는가: `MAGI-002 §6-7` 의 습윤 판정은 혼합의 배치 단위를 **재지 않고**
단일(`saIm0583` 6 실현 = 3.8 p)의 것을 빌려 썼습니다. 혼합은 수정 힘장 물 자료가
**배열 1 개뿐**이기 때문입니다(`sa50nb50e1~e5` 는 전부 결함판). §6-9 의 민감도 표가
그 가정에 얼마나 걸리는지 보였고, 이 계산이 k 를 **실측으로** 확정합니다.

    등록 3 항 (자료 0 건 상태에서 적음, `MAGI-002 §6-9-1`)
      ① 주 산출은 5 실현의 **유지율 SD**. 분모는 각 실현의 RH0.
      ② 그 값으로 §6-9 표의 k 를 확정하고 `saIm0958` 쌍 한정어를 확정/철회.
      ③ **이 시험으로 §6-1·§6-7 의 결론을 바꾸지 않는다** — 자를 재는 계산이지
         가설 시험이 아니다. 단 k >= 4.2 면 `sa50nb50 vs saIm100` 도 판정 불가로 내린다.

`run_water_v3w.py` 를 못 쓰는 이유: 그쪽 `TARGETS` 는 등록된 랩탑 11 종이고
`--only` 가 목록 밖 이름을 거부합니다(§4 목록만 돕니다). 계열도 갈라야 합니다.

    HERE      v3w_water_mix/        RUNS  water_runs_v3w_mix/
    CHARGED   charged_v3/           RH    [0.90, 0.0]   <- 비싼 것 먼저(§5 LPT)
    TARGETS   sa50nb50e1~e5 (구조는 이미 있습니다 — 빌드 0)

⚠️ **RH0 에는 물 분자가 없어 `Hw`·`Lw` 쌍이 출력 머리말에 아예 안 나옵니다.**
그래서 머리말 관문을 그대로 걸면 **멀쩡한 건조 자료를 실패로 찍습니다.**
`ff_of()` 가 RH0 을 `해당 없음`으로 가릅니다 — CLAUDE.md §0 의 "검사기 오탐" 그대로입니다.
RH0 은 물 힘장 수정과 무관하고(계에 물이 0), CLAUDE.md 도 **RH>0** 만 결함판으로 지정합니다.

사용:
    python run_tmtv2w.py               5 실현 x RH{90,0} = 10 건, 워커 4
    python run_tmtv2w.py --gate-only   관문만 보고 **아무것도 안 돌립니다**
"""
import json, os, sys

import run_water as rw

HERE = os.path.dirname(os.path.abspath(__file__))
from ff_gate import ff_path as _ffp
from ff_gate import (FF_MD5, FF_TAG, OWOW_EPS, ZERO_PAIRS,
                     md5_gate, read_ff_header)
from run_water_v3w import read_seed

SUF = '_mix'                    # 환경변수로 두지 않습니다 — 계열을 손으로 틀릴 자리를 없앱니다
TARGETS = [(f'sa50nb50e{i}', f'saIm 12 + nbIm 12 실현 {i}') for i in range(1, 6)]


def wire():
    """공유 모듈 `run_water` 의 전역을 이 계열로. **main() 에서만**(import 부작용 금지)."""
    rw.HERE = os.path.join(HERE, 'v3w_water' + SUF)
    rw.RUNS = os.path.join(HERE, 'water_runs_v3w' + SUF)
    rw.CHARGED = os.path.join(HERE, 'charged_v3')
    rw.WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
    rw.RH_LIST = [0.90, 0.0]    # 비싼 것 먼저 — jobs 가 이 순서로 깔립니다(§5 LPT)
    rw.MAX_WORKERS = 4          # 배정분(ASSIGN_20260907 §F-1). 8 로 올리지 마십시오
    rw.TARGETS = list(TARGETS)


def ff_of(name, rh):
    """머리말 관문. **RH0 에도 그대로 겁니다.**

    🔴 초판은 *"RH0 은 물이 없어 `Hw`·`Lw` 쌍이 안 찍히니 해당 없음"* 으로
    **건너뛰었습니다. 틀렸습니다** — 09-07 15:5x 실측: 착수 45 초 뒤
    `check_ff_per_run.py water_runs_v3w_mix` 가 `rh00_sa50nb50e1/e2` 에 대해
    **`힘장 통과 · Hw/Lw none · Ow-Ow 89.633`** 을 찍었습니다. RASPA 는 성분이
    계에 몇 개 있든 **정의된 성분의 쌍 표를 전부 인쇄**합니다.

    건너뛰기가 오탐보다 나쁜 이유: 오탐은 멀쩡한 자료를 붙잡지만 이것은
    **결함판으로 돈 RH0 을 조용히 통과**시킵니다. 관문은 걸리는 쪽으로 틀립니다.
    """
    d = os.path.join(rw.RUNS, f'rh{int(rh * 100):02d}_{name}')
    c = read_ff_header(d)
    c['ok'] = (all(c.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
               and c.get('OwOw_eps') is not None
               and abs(c['OwOw_eps'] - OWOW_EPS) < 1e-3)
    return c


def stamp():
    """산출물에 힘장 출처를 **행마다**(`run_water_v3w.stamp` 와 같은 이유)."""
    p = os.path.join(rw.HERE, 'water_results.json')
    if not os.path.exists(p):
        print(f'  !! 결과 파일 없음: {p}  (아무것도 안 찍었습니다)')
        return 1
    rows = json.load(open(p, encoding='utf-8'))
    nff = nseed = 0
    for r in rows:
        r['forcefield'] = FF_TAG
        c = ff_of(r['name'], r['RH'])
        r['ff_check'] = c
        nff += bool(c['ok'])
        sd = read_seed(r['name'], r['RH'])
        if sd is not None:
            r['raspa_seed'] = sd
            nseed += 1
    json.dump(rows, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    side = os.path.join(rw.HERE, 'ff_provenance.json')
    json.dump({'forcefield': FF_TAG, 'md5': FF_MD5, 'path': _ffp(),
               'test': 'T-MTV-2w', 'registered': 'MAGI-002 §6-9-1',
               'rows': len(rows), 'ff_ok_rows': nff},
              open(side, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  난수 씨앗 회수 {nseed}/{len(rows)}행 · 힘장 확인 **{nff}/{len(rows)}행 통과**')
    return 0


def main():
    wire()
    if '--stamp-only' in sys.argv:
        # 도는 프로세스는 **import 시점의 `ff_of`** 를 쥐고 있습니다(CLAUDE.md §6).
        # 위 🔴 고침 전에 띄운 실행은 RH0 행을 `not_applicable` 로 찍고 끝납니다.
        # 완주 뒤 이 길로 **다시 찍으십시오** — 그래야 RH0 도 진짜 관문을 지납니다.
        return stamp()
    if '--gate-only' in sys.argv:
        ok, _ = md5_gate()
        bad = []
        for n, _d in TARGETS:
            for rh in rw.RH_LIST:
                d = os.path.join(rw.RUNS, f'rh{int(rh * 100):02d}_{n}')
                if not os.path.isdir(d):
                    continue
                c = ff_of(n, rh)
                print(f'  [머리말 관문] {n:<12} RH{int(rh*100):>3}%  '
                      f'{"해당 없음" if c.get("gate") == "not_applicable" else ("통과" if c["ok"] else "**실패**")}')
                if not c['ok']:
                    bad.append((n, rh))
        print(f'  -> 파일 관문 {"통과" if ok else "**실패**"} · 머리말 실패 {len(bad)}건')
        return 0 if (ok and not bad) else 1

    print('T-MTV-2w — 혼합 sa50nb50 의 습윤 배치 단위 (MAGI-002 §6-9-1 등록)', flush=True)
    print(f'  HERE {rw.HERE}\n  RUNS {rw.RUNS}\n  CHARGED {rw.CHARGED}', flush=True)
    print(f'  RH {rw.RH_LIST} · 워커 {rw.MAX_WORKERS} · 대상 {len(rw.TARGETS)}종: '
          + ', '.join(n for n, _ in rw.TARGETS), flush=True)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, f'{n}_DDEC6.cif'))]
    if missing:
        print(f'!! 전하 CIF 없음: {missing}'); return 2
    if not md5_gate()[0]:
        return 1
    for d in (rw.HERE, rw.RUNS):
        os.makedirs(d, exist_ok=True)
    rc = rw.main()
    return 0 if (stamp() == 0 and rc == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
