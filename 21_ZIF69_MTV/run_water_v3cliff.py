"""수분 경쟁 — 절벽 구조 saIm0917 / saIm0958, RH0/RH90 만 (4작업).

[무엇을 재는가]
    랩탑 12작업이 87.5% 를 74.2 pp 로 재 "아직 고원 안"이라고 답했고,
    100% 는 60.6% 로 꺾여 있습니다. **절벽은 87.5~100% 사이인데 그 구간에
    점이 하나도 없습니다.** 24 자리 중 그 사이의 격자점은 22·23 자리
    둘뿐이라 이 둘이 구간을 전부 채웁니다.

[왜 RH0/RH90 만인가]
    질문이 "절벽이 어디냐" 이고 그 답은 유지율(RH90/RH0)입니다. RH25/50 은
    계단 모양을 보는 데 쓰이지 절벽 위치에는 쓰이지 않습니다. 4단계로 하면
    작업이 8개가 되는데 늘어난 4개가 이 질문에 답하지 않습니다.

[폴더 이름이 v3_water_grid_cliff 인 이유 — 둘 다 만족해야 합니다]
    saIm0583e1~e5 앙상블은 **같은 조성의 다른 실현**이라 배치 축이고, 그래서
    v3_water_ens/ 로 분리했습니다. 그러나 0917·0958 은 **조성 축의 점**입니다
    — 0583·0625·0667·0875 와 같은 자에 놓고 읽어야 절벽이 보입니다. 그러니
    merge 도구가 격자와 **같은 표**에 놓아야 합니다.

    그런데 격자와 같은 폴더(v3_water_grid/)에 그대로 쓰면 안 됩니다.
    run_water.py:318~340 의 최종 저장은 **TARGETS 만 순회해** rows 를 만들고
    water_results.json 을 통째로 덮어씁니다. 이 러너의 TARGETS 는 절벽 2종
    뿐이므로, 같은 폴더에 쓰면 이미 그 파일에 있는 **saIm0583 4행이
    사라집니다.** 이어받기가 읽어 들이기는 하지만 쓸 때는 TARGETS 밖의 행을
    담지 않습니다.

    그래서 폴더를 나누되 이름에 'v3_water_grid' 를 포함시킵니다.
    merge_water_batches.generation_of() 는 부분 문자열로 세대를 잡으므로
    v3_water_grid_cliff/ 도 'v3격자'로 분류됩니다 — 파일은 분리되고 표는
    합쳐지는, 둘 다 되는 유일한 이름입니다. (v3_water_cliff/ 로 하면 'v3' 가
    되어 격자와의 병합이 거부됩니다. 실제로 확인했습니다.)

[출처 중복도 막습니다 — 2026-08-23 함정의 재발 방지]
    폴더를 나눴으므로 이 폴더의 water_results.json 에는 절벽 2종만 있습니다.
    그래도 사본에 이름 필터를 겁니다. 08-23 에 같은 행이 두 출처로 세어져
    0.00시그마 유령 교차 검증 쌍이 만들어진 적이 있어, 사본을 만들 때
    **무엇이 담기는지 세어 보는** 습관을 남깁니다.

[엔진·규약]
    run_water_v3grid.py 를 import 해 경로·물 정의·워커를 물려받고 TARGETS 와
    RH_LIST 만 바꿉니다. 사이클 15000, CO2 0.15 bar, UFF_MOF, TIP5P-Ew 5자리가
    한 글자도 다르지 않습니다 (CLAUDE.md 1 절).

[작업 길이]
    RH_LIST 를 [0.90, 0.0] 으로 놓아 비싼 것을 먼저 큐에 넣습니다(5 절 LPT).
    4작업 / 워커 8 이면 전부 동시에 도므로 makespan 은 가장 긴 RH90 하나,
    약 12 시간입니다.

사용:
    WATER_BATCH_TAG=desktopcliff WATER_V3_WORKERS=8 python run_water_v3cliff.py
"""
import json
import os
import sys

import run_water_v3grid  # noqa: F401 — 경로·워커·물 정의 전역을 물려받는다
import run_water as rw

_HERE = os.path.dirname(os.path.abspath(__file__))
# 격자 파일을 덮지 않도록 폴더를 나누되, 이름에 'v3_water_grid' 를 남겨
# 세대 검사가 'v3격자'로 잡게 합니다. 위 [폴더 이름이 ...] 참조.
rw.HERE = os.path.join(_HERE, 'v3_water_grid_cliff')
rw.RUNS = os.path.join(_HERE, 'water_runs_v3cliff')
os.makedirs(rw.HERE, exist_ok=True)

# 비싼 것 먼저 (LPT).
rw.RH_LIST = [0.90, 0.0]

CLIFF = ['saIm0917', 'saIm0958']
rw.TARGETS = [
    ('saIm0917', 'SO3H 91.7% (22/24) — 절벽 구간'),
    ('saIm0958', 'SO3H 95.8% (23/24) — 절벽 구간'),
]

if __name__ == '__main__':
    print('수분 경쟁 — 절벽 구조 2종, RH0/RH90 (4작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)
    print(f'  RH     {rw.RH_LIST}  (비싼 RH90 먼저 — LPT)', flush=True)

    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {" ".join(missing)}', flush=True)
        sys.exit(1)

    # 물 정의가 5자리인지 확인합니다. 배포본 TraPPE/water.def 는 3자리라
    # 조용히 다른 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    print(flush=True)

    rc = rw.main()

    # 기기명 사본 — 이 실행이 낸 두 조성만 걸러 담습니다. 위 [출처 중복] 참조.
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        rows = [r for r in json.load(open(src, encoding='utf-8'))
                if r['name'] in CLIFF]
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        dst = os.path.join(rw.HERE, f'water_results_{tag}.json')
        json.dump(rows, open(dst, 'w', encoding='utf-8'),
                  indent=2, ensure_ascii=False)
        got = sorted({r['name'] for r in rows})
        print(f'  기기명 사본 저장: {dst}', flush=True)
        print(f'    {len(rows)}행, 조성 {got} (0583 은 desktop4 몫이라 제외)',
              flush=True)
        if len(rows) != 4:
            print(f'  !! 기대 4행인데 {len(rows)}행입니다. 확인하세요.',
                  flush=True)

    sys.exit(rc)
