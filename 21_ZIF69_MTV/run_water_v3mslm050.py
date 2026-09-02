"""수분 경쟁 — `mslm050` 한 종, RH90 · RH0 두 작업.

[왜 이 조성인가 — 자료가 한 점도 없습니다]
    관문(LCD 감소 20%)을 통과하는 치환 조성은 여섯뿐이고 그중 `mslm` 은
    `mslm025` 와 `mslm050` 둘입니다. `mslm050` 은 LCD 감소 6.68% 로 치환 조성
    중 관문 여유가 가장 큽니다. 그런데 CO2/H2O 경쟁 자료가 **없습니다** —
    08-27 확인: `v3_water` · `v3_water_ens` · `v3_water_grid` ·
    `v3_water_grid_cliff` · `v3_water_chunkref` 어디에도 `mslm050` 행이 없습니다.

[왜 RH90 을 앞에 두는가]
    `CO2_retention_pct` 의 **분자가 RH90 로딩**입니다. 이것이 밀리면 유지율
    결론이 통째로 밀립니다(랩탑 지적, 2026-08-27). 그래서 `RH_LIST` 앞에
    둡니다. 워커 2라 실제로는 둘이 함께 뜨고, RH0(실측 1.6~1.9h)이 먼저 끝나며
    RH90(8.6~9.4h)이 기계를 붙잡습니다.

[HERE 를 옮기는 이유 — 안 옮기면 전부 건너뜁니다]
    `run_water.main()` 이 결과 파일 경로를 모듈 상수가 아니라 함수 안에서
    `os.path.join(HERE, ...)` 로 만들고, 그 파일을 **이어받기 소스로도** 읽습니다.
    `CHARGED`/`RUNS` 만 바꾸면 옛 결과를 보고 전부 건너뜁니다
    (2026-08-14 에 실제로 그랬습니다 — `run_water_v3.py` 독스트링).

[사전 등록과의 관계]
    `MSLM050_CHALLENGE_20260827.md` 는 `mslm050` **습윤 WC 3작업**(ads/tsa/vsa)을
    사전 등록했고 기기를 **랩탑**으로 적었습니다. 이 파일은 그것이 **아니라**
    별개의 물 경쟁 2작업입니다. 규약(물 모델·사이클·힘장)은 다른 조성과
    완전히 동일해야 같은 표에 놓입니다 — `run_water` 기본값을 건드리지 않습니다.
"""
import os
import shutil
import subprocess
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REAL, 'v3_water_mslm050')
os.makedirs(OUT, exist_ok=True)

rw.HERE = OUT
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_v3mslm050')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_MSLM050_WORKERS', '2'))

# RH90 먼저. 유지율의 분자입니다.
rw.RH_LIST = [0.90, 0.0]

rw.TARGETS = [
    ('mslm050', 'SO2CH3 50% — 관문 통과 비-saIm 중 여유 최대'),
]

if __name__ == '__main__':
    print('수분 경쟁 — mslm050 (RH90, RH0)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  RH     {rw.RH_LIST}  (RH90 이 유지율의 분자)', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)

    # 등록된 2작업이 맞는지. 조성이나 RH 가 늘어나 있으면 멈춥니다.
    if len(rw.TARGETS) != 1 or rw.RH_LIST != [0.90, 0.0]:
        print('  !! 등록된 2작업(mslm050 x RH90,RH0)이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)

    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)

    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {" ".join(missing)}', flush=True)
        sys.exit(1)

    # 물 정의가 5자리인지. 배포본 TraPPE/water.def 는 3자리라 조용히 다른 물로
    # 계산됩니다 — COMMS.md 0절이 말하는 "실패가 결과처럼 보이는 것" 입니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리가 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)

    # [2026-08-27] Zeo++ 와 RASPA 를 같이 띄우지 않습니다. 08-12 에 그 조합이
    # OOM 을 내고 dbus 까지 죽여 WSL 이 통째로 먹통이 됐고, 08-27 에 제가
    # 워커를 올려 같은 것을 재현시켰습니다(network 4개 합 24.0 GB).
    busy = subprocess.run(['pgrep', '-f', 'risk_screen|/network'],
                          capture_output=True, text=True).stdout.strip()
    if busy:
        print(f'  !! Zeo++ 계열이 돌고 있습니다(PID {busy.replace(chr(10), " ")}). '
              '같이 띄우지 않습니다. 중단합니다.', flush=True)
        sys.exit(2)

    # simulate 를 찾을 수 있는지. PATH 에 없으면 여기서 멈춥니다 — 08-27 에
    # risk_screen 이 맨 `python` 을 못 찾아 7종이 조용히 실패한 것과 같은 유형입니다.
    print(f'  simulate {rw.SIMULATE}', flush=True)
    if not (rw.SIMULATE and os.path.exists(rw.SIMULATE)):
        print('  !! simulate 를 찾을 수 없습니다. 중단합니다.', flush=True)
        sys.exit(1)

    # 작업 단위 이어받기가 있으므로 중단 뒤 그냥 다시 띄우면 됩니다.
    print(flush=True)
    rc = rw.main()

    # 기기 이름을 붙인 사본. `run_water_v3grid_0583.py` 와 같은 배선입니다.
    # 기기 이름을 하드코딩하지 않습니다 — 08-22 에 cloud4c 가 박혀 있어 다른
    # 기기 산출물이 남의 이름을 달았습니다(merge_water_batches.machine_of 가
    # 파일명에서 출처를 읽으므로 그 순간 되돌릴 수 없게 됩니다).
    #
    # 이 줄은 `autopush` 의 water 스키마가 **완주 표지로 요구**하기도 합니다
    # (autopush.check_log:188). 없으면 정상 완주를 실패로 읽습니다.
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        dst = os.path.join(rw.HERE, f'water_results_{tag}.json')
        shutil.copy(src, dst)
        print(f'  기기명 사본 저장: {dst}', flush=True)

    sys.exit(rc)
