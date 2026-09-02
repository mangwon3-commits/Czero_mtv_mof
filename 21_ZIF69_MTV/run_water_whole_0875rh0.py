"""분할 검증의 **관문 ③ 전용** — `saIm0875` RH0 을 데스크탑에서 통짜로 돈다.

[왜 이것이 필요한가 — 등록된 ③ 을 지금 자료로는 판정할 수 없다]
    `CHUNKED_PROTOCOL_20260826.md` 3절 ③ 은 이렇게 등록돼 있습니다:

        분할 총 소요 / 통짜 소요  <=  1.15

    그런데 저장소에 있는 통짜 RH0 소요는 **laptop2 실측 4.44 h** 뿐이고,
    분할은 **데스크탑에서 2.61 h** 로 쟀습니다. 이 둘을 나누면 0.59 가
    나오는데 **그것은 오버헤드가 아니라 기기 속도 차이**입니다.

    저장소 규약이 정확히 이것을 금지합니다 — COMMS.md "작업 비용은 기기마다
    재고, 배율을 옮기지 않습니다". 08-26 에 랩탑이 같은 이유로 데스크탑
    배율 이식을 거절했고 그 판단이 맞았습니다.

    그래서 **같은 기기의 통짜 값**이 있어야 ③ 을 판정할 수 있습니다.
    이 러너가 그것 하나만 만듭니다.

[무엇도 바꾸지 않습니다]
    `run_water.py` 를 그대로 씁니다. 힘장·물 정의(TIP5P-Ew 5자리)·CO2 모델·
    분압 0.15 bar·사이클(초기화 5,000 + 생산 15,000)·컷오프·Ewald 전부
    한 글자도 다르지 않습니다. **바뀌는 것은 대상 1종과 RH 1점뿐**입니다.

[출력을 왜 분리하나]
    격자 결과(`v3_water_grid/`)에 섞으면 `saIm0875` RH0 이 세 벌
    (junseok · laptop · 이것)이 됩니다. 앞의 둘은 **교차 검증 쌍**이고
    이것은 **오버헤드 측정용**이라 성격이 다릅니다. 같은 표에 넣으면
    쌍이 셋으로 보여 판정이 흐려집니다.

    그래서 `v3_water_chunkref/` 로 따로 받습니다. `generation_of()` 가
    'v3_water' 를 부분문자열로 잡아 세대 **v3** 로 읽는데, 격자는 **v3격자**
    라 애초에 병합되지 않습니다 — 의도한 대로입니다.

사용:
    RASPA_DIR=$HOME/RASPA/simulations python run_water_whole_0875rh0.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_water as rw                                        # noqa: E402

REF = os.path.join(HERE, 'v3_water_chunkref')
os.makedirs(REF, exist_ok=True)

rw.HERE = REF
rw.CHARGED = os.path.join(HERE, 'charged_v3')
rw.RUNS = os.path.join(HERE, 'water_runs_chunkref')
rw.WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = 1                          # 1코어. 다른 계산과 경합하지 않는다
rw.RH_LIST = [0.0]
rw.TARGETS = [('saIm0875', 'SO3H 87.5% (21/24) — 분할 검증 관문 ③ 기준')]


if __name__ == '__main__':
    print('통짜 기준 — saIm0875 RH0 (분할 검증 관문 ③ 전용)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}   RH {rw.RH_LIST}', flush=True)

    # 좁힌 러너가 사고를 낸 전력이 있어(08-25 d0b6f50) 범위를 검사합니다.
    if len(rw.TARGETS) != 1 or rw.RH_LIST != [0.0]:
        print('  !! 대상·RH 범위가 어긋납니다. 중단합니다.', flush=True)
        sys.exit(1)
    if not os.path.exists(os.path.join(rw.CHARGED, 'saIm0875_DDEC6.cif')):
        print('  !! 전하 CIF 없음', flush=True)
        sys.exit(1)

    # 물 정의가 5자리인지. 배포본 TraPPE/water.def 는 3자리라 조용히 다른
    # 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    print(flush=True)

    rc = rw.main()

    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        shutil.copy(src, os.path.join(rw.HERE, f'water_results_{tag}.json'))
        print(f'  기기명 사본 저장: water_results_{tag}.json', flush=True)

    sys.exit(rc)
