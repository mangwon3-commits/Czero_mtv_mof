#!/usr/bin/env python
"""RH90 유지율 재계산 — **수정 힘장 계열 v3w** (`WATER_FIX_20260906.md` §2·§4 등록분).

`run_water.py` 를 감싸 **경로를 전부 새로** 잡습니다. 러너의 이어받기는 출력 파일의
존재만 보고 **어느 힘장으로 만들어졌는지 안 봅니다**(CLAUDE.md §3). 그래서
`HERE` 와 `RUNS` 를 **둘 다** 새 경로로 두어 결함판을 물려받을 길 자체를 없앱니다.

    HERE      v3w_water/           (water_results.json + water_results_<기기>.json)
    RUNS      water_runs_v3w/
    CHARGED   charged_v3/
    RH_LIST   [0.90]               RH0 행은 물 분자 0이라 결함과 무관 — 옛 값을 분모로 씁니다
    TARGETS   랩탑 몫 11종 (§4)

**힘장 관문이 둘 있습니다. 하나라도 걸리면 산출물을 쓰지 마십시오.**

    착수 전   실물 힘장 md5 == FF_MD5            아니면 **즉시 중단**
    완주 후   출력 머리말 `Hw - Hw [ZERO_POTENTIAL]` · `Ow - Ow 89.633/3.097`
              아니면 그 행을 `ff_check.ok = false` 로 찍고 **K 값을 쓰지 말라고 적습니다**

사용:
    python run_water_v3w.py                 등록된 11종 전부
    python run_water_v3w.py --only saIm050  검증용 1건 (§4 가 시키는 첫 건)
"""
import json, os, re, socket, sys

import run_water as rw

HERE = os.path.dirname(os.path.abspath(__file__))
# 힘장 관문은 **한 자리**에서만 옵니다 (`ff_gate.py`, 09-07 신설).
# 상수를 러너마다 적으면 힘장을 또 고칠 때 한 곳만 고치는 사고가 납니다.
# `ff_gate` 는 프로젝트 안의 무엇도 import 하지 않으므로 여기서 불러도 안전합니다.
from ff_gate import ff_path as _ffp
from ff_gate import (FF_MD5, FF_TAG, OWOW_EPS, ZERO_PAIRS,
                     md5_gate, read_ff_header)

# --- 계열 배선 --------------------------------------------------------------
# ⚠️ **import 시점에 하지 않습니다.** `run_water` 는 여러 러너가 공유하는 모듈이고
# 그 전역(`HERE`·`RUNS`·`CHARGED`)을 여기서 덮으면, **이 파일을 import 한 것만으로**
# 남의 프로세스 산출물이 제 계열 폴더로 샙니다 — 오류 없이.
# 09-07 데스크탑 실측: 밀도 러너가 `run_water_v3w` 를 import 하면 그 순간
# `.../water_runs_density_v3` 가 `.../water_runs_v3w` 로 바뀝니다.
# 그래서 배선은 **`main()` 에서만** 합니다. `read_ff_header` 같은 함수를 밖에서
# 가져다 써도 안전해집니다(`check_ff_per_run.py` 가 그렇게 씁니다).
#
# 접미사로 계열을 가릅니다. 기본값 '' 이면 원 계열 그대로입니다.
#   V3W_SUFFIX=_rep  ->  v3w_water_rep/ · water_runs_v3w_rep/   (씨앗 반복)
SUF = os.environ.get('V3W_SUFFIX', '')
TARGETS = [
    ('saIm025',     'SO3H 25%'),
    ('saIm050',     'SO3H 50%'),
    ('saIm0583',    'SO3H 58.3%'),
    ('saIm0583e1',  'SO3H 58.3% 실현 1'),
    ('saIm0583e2',  'SO3H 58.3% 실현 2'),
    ('saIm0583e3',  'SO3H 58.3% 실현 3'),
    ('saIm0583e4',  'SO3H 58.3% 실현 4'),
    ('saIm0583e5',  'SO3H 58.3% 실현 5'),
    ('saIm0625',    'SO3H 62.5%'),
    ('saIm0667',    'SO3H 66.7%'),
    ('saIm075',     'SO3H 75% — 관문 미해결(STAGE2 판정문). 관찰용'),
]


def wire():
    """공유 모듈 `run_water` 의 전역을 이 계열로 맞춥니다. **main() 에서만.**"""
    rw.HERE = os.path.join(HERE, 'v3w_water' + SUF)
    rw.RUNS = os.path.join(HERE, 'water_runs_v3w' + SUF)
    rw.CHARGED = os.path.join(HERE, 'charged_v3')
    rw.WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
    rw.RH_LIST = [0.90]
    rw.MAX_WORKERS = 8
    rw.TARGETS = list(TARGETS)


def main():
    wire()                      # 배선은 여기서만 (import 부작용 없음)
    if '--gate-only' in sys.argv:
        # 관문만 보고 **아무것도 안 돌립니다.**
        # 09-07: 관문 출력을 보려고 `--only saIm050` 로 러너를 불렀다가
        # `rw.main()` 이 그대로 돌았습니다. 캐시 경로라 계산은 안 떴지만
        # **살아 있는 계열 폴더에 1행짜리 결과 JSON 을 썼습니다.**
        # 관문을 보려고 러너를 부르는 일이 없도록 길을 따로 냅니다.
        ok, _ = md5_gate()
        bad = []
        for n, _d in TARGETS:
            d = os.path.join(rw.RUNS, f'rh{int(rw.RH_LIST[0] * 100):02d}_{n}')
            if not os.path.isdir(d):
                continue
            c = read_ff_header(d)
            good = (all(c.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
                    and c.get('OwOw_eps') is not None
                    and abs(c['OwOw_eps'] - OWOW_EPS) < 1e-3)
            print(f'  [머리말 관문] {n:<14} {"통과" if good else "**실패**"}')
            if not good:
                bad.append(n)
        print(f'  -> 파일 관문 {"통과" if ok else "**실패**"} · 머리말 실패 {len(bad)}건'
              + (f' {bad}' if bad else ''))
        return 0 if (ok and not bad) else 1
    if '--stamp-only' in sys.argv:
        # 도는 프로세스는 import 시점의 함수를 쥐고 있어 이 파일을 고쳐도 안 바뀝니다
        # (CLAUDE.md §6). 그 실행이 남긴 잘못된 ff_check 를 **다시 찍기** 위한 길입니다.
        return stamp()
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1:]
        rw.TARGETS = [t for t in rw.TARGETS if t[0] in only]
        missing = [n for n in only if n not in [t[0] for t in rw.TARGETS]]
        if missing:
            print(f'!! 등록 목록에 없는 이름: {missing}  (§4 목록만 돕니다)'); return 2

    print('RH90 유지율 재계산 — **v3w 계열** (수정 힘장)', flush=True)
    print(f'  HERE {rw.HERE}\n  RUNS {rw.RUNS}\n  CHARGED {rw.CHARGED}', flush=True)
    print(f'  RH {rw.RH_LIST} · 워커 {rw.MAX_WORKERS} · 대상 {len(rw.TARGETS)}종'
          f'{"  [--only]" if only else ""}: ' + ', '.join(n for n, _ in rw.TARGETS), flush=True)
    if not md5_gate()[0]:
        return 1
    for d in (rw.HERE, rw.RUNS):
        os.makedirs(d, exist_ok=True)

    rc = rw.main()
    return 0 if (stamp() == 0 and rc == 0) else 1


def read_seed(name, rh):
    """그 작업의 RASPA 난수 씨앗을 **출력 머리말에서** 회수합니다.

    ⚠️ `run_water.py` 는 씨앗을 안 적습니다 — RASPA 기본값(시각 기반)이 쓰이고
    산출물 JSON 에도 남지 않아 **어떤 실행도 재현이 불가능**합니다(09-06 실측:
    같은 실행의 세 작업이 1788660534/534/535 = 착수 시각 초 단위).

    ⚠️ **그래서 결과 JSON 을 쓰는 시점에 회수해야 합니다.** §7 이 결과 JSON 이
    있으면 `*_runs*/` 를 지워도 된다고 하므로, 나중으로 미루면 **씨앗이 함께
    사라집니다.** 폴더가 살아 있는 지금 찍습니다.
    """
    d = os.path.join(rw.RUNS, f'rh{int(rh * 100):02d}_{name}', 'Output', 'System_0')
    if not os.path.isdir(d):
        return None
    for fn in sorted(x for x in os.listdir(d) if x.endswith('.data')):
        with open(os.path.join(d, fn), encoding='utf-8', errors='ignore') as f:
            for ln in f:
                m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
                if m:
                    return int(m.group(1))
                if ln.startswith('Number of cycles'):   # 머리말을 지나면 없는 것
                    break
    return None


def stamp():
    """산출물에 힘장 출처를 **행마다** 남깁니다.

    등록문은 "JSON 최상단" 이라 했으나 `water_results.json` 은 **맨 리스트**이고
    이 형식을 그대로 순회하는 판독기가 열 곳 넘습니다(check_retention.py ·
    repro_verdict.py · merge_water_batches.py · scope_report.py …).
    **그래서 행마다 찍고 사이드카를 따로 둡니다** — 형식을 안 깨고, 행이 다른
    파일로 복사돼도 힘장 표기가 **따라갑니다.** 어젯밤 밀도 격자에서 곁의 설정
    파일이 자료와 떨어진 그 문제를, 곁에 두지 않는 쪽으로 막습니다.
    """
    # ⚠️ **조성마다 따로 봅니다.** 초판은 `read_ff_header(rw.RUNS)` 로 runs 아래
    # **아무 `.data` 하나**를 읽어 그 결과를 **모든 행에** 찍었습니다. 그러면
    # 죽은/낡은 실행 파일 하나가 **관문을 대신 통과**시키고, 조성마다 힘장이
    # 달라도 못 잡습니다(09-07 데스크탑이 디스크 사고 뒤 발견).
    # `CLAUDE.md §3` 은 이어받기만 말하지만 **관문도 파일 존재를 봅니다.**
    def ff_of(name, rh):
        d = os.path.join(rw.RUNS, f'rh{int(rh * 100):02d}_{name}')
        c = read_ff_header(d)
        c['ok'] = (all(c.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
                   and c.get('OwOw_eps') is not None
                   and abs(c['OwOw_eps'] - OWOW_EPS) < 1e-3)
        return c

    ff_gate_path = _ffp()
    p = os.path.join(rw.HERE, 'water_results.json')
    ok = False                    # 결과 파일이 없으면 통과가 아닙니다(초판은 여기서 터졌습니다)
    if not os.path.exists(p):
        print(f'  !! 결과 파일 없음: {p}\n'
              f'     (계열 접미사 V3W_SUFFIX 를 확인하십시오. 아무것도 안 찍었습니다.)')
        return 1
    if True:
        rows = json.load(open(p, encoding='utf-8'))
        nseed = 0; nff = 0
        for r in rows:
            r['forcefield'] = FF_TAG
            c = ff_of(r['name'], r['RH'])
            r['ff_check'] = c
            nff += bool(c['ok'])
            sd = read_seed(r['name'], r['RH'])
            if sd is not None:
                r['raspa_seed'] = sd
                nseed += 1
        print(f'  난수 씨앗 회수 {nseed}/{len(rows)}행 '
              f'(러너가 안 적어 출력 머리말에서 읽습니다 — 폴더를 지우면 사라집니다)')
        print(f'  힘장 확인 **{nff}/{len(rows)}행 통과** (조성마다 자기 출력으로)')
        ok = (nff == len(rows))
        if not ok:
            print('  !! 통과 못 한 행: '
                  + str([r['name'] for r in rows if not r['ff_check']['ok']]))
        json.dump(rows, open(p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        json.dump({'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'ff_path': ff_gate_path,
                   'ff_all_rows_ok': ok, 'series': 'v3w', 'host': socket.gethostname().lower(),
                   'RH_LIST': rw.RH_LIST, 'targets': [n for n, _ in rw.TARGETS],
                   'note': '수정 힘장(Hw none/Lw none) 계열. v3 결함판과 섞지 말 것.'},
                  open(os.path.join(rw.HERE, 'water_results_meta.json'), 'w',
                       encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'  {len(rows)}행에 forcefield·ff_check 를 찍고 사이드카를 남겼습니다.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
