"""수분 경쟁 — saIm0583 앙상블 e1·e2 의 RH25 만 (2작업). 사용자 승인 08-24.

[무엇을 재는가 — 유지율이 못 하는 일을 대신할 자가 쓸 만한지]
    08-23 판정이 조성 간 **유지율 순위를 보류**했습니다. 배치 산포가 조성 간
    산포의 2.57배라서입니다. 앙상블 10작업(`run_water_v3ens0583.py`)이 그
    상쇄 비율을 재고 있고, 이 2작업은 **다른 질문**에 답합니다.

        유지율(RH90/RH0)  물 클러스터 온셋(~RH30) 을 한참 지난 뒤를 읽는다
        W25 (RH25 의 물 로딩)  온셋 **직전**을 읽는다

    Veldhuizen 2023 은 CO2-물 경쟁이 협력으로 바뀌는 전환이 RH 자체가 아니라
    **물 클러스터 온셋**에서 일어남을 보였고, Zhao 2024 의 메틸화 소수성
    효과도 물 등온선 온셋을 P/P0 0.25 로 미루는 것이지 총 물 용량을 낮추는
    것이 아니라고 명시합니다(저자들이 "저습도에서" 로 주장을 한정).

    **RH90 에서 조성이 안 갈리는 이유가 그것이라면, RH25 에서는 갈려야
    합니다.** 그런데 그 축을 순위에 쓰려면 먼저 이 축이 배치 산포에
    견디는지를 봐야 합니다 — 유지율이 죽은 바로 그 이유로 W25 도 죽을 수
    있기 때문입니다. e1·e2 두 실현의 W25 차이가 그 시험입니다.

    사전 등록(PROPOSAL_20260824.md §5 R3, 수를 보기 전에 고정):

        d = |W25(e1) - W25(e2)|
        d <  0.17 mol/kg  -> 배치에 견딤. W25 를 순위 자 후보로 유지
        d >= 0.33 mol/kg  -> 유지율과 같은 이유로 사망. W25 순위 폐기
        그 사이           -> 미결. e3~e5 추가(다음 창, 조건부 승인 사항)

        부수: 앙상블 W25(0583) 가 [0.45, 0.75] 안이면 격자 0625 의 0.6983 과
        같은 구간 — 승자 조성의 온셋 좌표가 격자와 이어집니다.

[왜 2작업뿐인가]
    이 질문에 필요한 최소가 둘입니다. 배정된 10작업의 여유(34 h) 안에
    들어가고, 죽는 쪽 답이 나오면 e3~e5 를 안 돌려 3작업을 아낍니다.

[엔진·규약]
    `run_water_v3ens0583.py` 를 import 해 경로·물 정의·워커 수·결과 폴더를
    **그대로** 물려받고 TARGETS 와 RH_LIST 만 좁힙니다. 사이클·힘장·CO2
    모델·물 정의·압력이 한 글자도 다르지 않습니다(CLAUDE.md 1 절).

    결과도 같은 `v3_water_ens/water_results.json` 에 씁니다. 그래야
    이어받기가 RH0/RH90 을 읽어 **유지율 기준선 c0**(`run_water.py:315`,
    `res[n][0.0]`)를 잡습니다. 다른 폴더에 쓰면 c0 가 없어 유지율이 NaN 이
    됩니다 — W25 자체는 물 로딩이라 무관하지만, 표가 반쪽이 됩니다.

[순서 관문 — 10작업이 끝난 뒤에만 돕니다]
    같은 결과 파일을 두 프로세스가 함께 쓰면 경쟁 상태가 됩니다. 작업 폴더는
    RH 별로 갈려 충돌하지 않지만 `water_results.json` 쓰기가 겹칩니다.
    그래서 아래에서 **10행이 다 있는지 확인하고, 없으면 시작하지 않습니다.**

사용 (10작업 완주 후):
    WATER_BATCH_TAG=junseok WATER_V3_WORKERS=6 \
        python run_water_v3ens0583_rh25.py
"""
import json
import os
import shutil
import sys

import run_water_v3ens0583  # noqa: F401 — 앙상블 경로·폴더·워커 전역을 물려받는다
import run_water as rw

PAIR = ['saIm0583e1', 'saIm0583e2']

rw.TARGETS = [
    ('saIm0583e1', 'SO3H 58.3% 실현 1 — RH25 온셋'),
    ('saIm0583e2', 'SO3H 58.3% 실현 2 — RH25 온셋'),
]
rw.RH_LIST = [0.25]

if __name__ == '__main__':
    print('수분 경쟁 — saIm0583 앙상블 e1·e2 RH25 (2작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}  (앙상블과 같은 파일)',
          flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}   RH {rw.RH_LIST}', flush=True)

    if len(rw.TARGETS) != 2 or rw.RH_LIST != [0.25]:
        print('  !! 대상/RH 가 등록된 2작업이 아닙니다. 중단합니다.', flush=True)
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

    # 순서 관문. 앙상블 10작업(e1~e5 x RH0/RH90)이 다 끝난 뒤에만 돕니다.
    res_path = os.path.join(rw.HERE, 'water_results.json')
    if not os.path.exists(res_path):
        print(f'  !! 앙상블 결과가 없습니다: {res_path}', flush=True)
        print('     run_water_v3ens0583.py (10작업) 를 먼저 완주시키세요.', flush=True)
        sys.exit(1)
    rows = json.load(open(res_path, encoding='utf-8'))
    have = {(r['name'], r['RH']) for r in rows}
    need = {(f'saIm0583e{i}', rh) for i in range(1, 6) for rh in (0.0, 0.90)}
    lack = sorted(need - have)
    if lack:
        print(f'  !! 앙상블 10작업이 아직 {len(lack)}개 남았습니다:', flush=True)
        for n, rh in lack[:10]:
            print(f'       {n} RH{int(rh*100)}', flush=True)
        print('     같은 결과 파일을 두 프로세스가 쓰면 경쟁 상태가 됩니다.',
              flush=True)
        print('     10작업 완주 후 다시 실행하세요.', flush=True)
        sys.exit(1)
    print('  순서 관문 통과 — 앙상블 10작업 완주 확인', flush=True)

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

    # 사전 등록된 판정을 그 자리에서 찍습니다. 수를 보고 문턱을 고르는 일이
    # 없도록, 문턱은 이 파일 상단 주석과 PROPOSAL §5 R3 에 이미 있습니다.
    if rc == 0 and os.path.exists(res_path):
        rows = json.load(open(res_path, encoding='utf-8'))
        w = {r['name']: r.get('H2O_molkg')
             for r in rows if r['RH'] == 0.25 and r['name'] in PAIR}
        if all(w.get(n) is not None for n in PAIR):
            d = abs(w[PAIR[0]] - w[PAIR[1]])
            if d < 0.17:
                verdict = '배치에 견딤 — W25 를 순위 자 후보로 유지'
            elif d >= 0.33:
                verdict = '사망 — 유지율과 같은 이유. W25 순위 폐기'
            else:
                verdict = '미결 — e3~e5 추가 여부는 사용자 판단'
            print(f'\n  W25(e1) {w[PAIR[0]]:.4f} / W25(e2) {w[PAIR[1]]:.4f} '
                  f'mol/kg', flush=True)
            print(f'  d = {d:.4f}  ->  {verdict}', flush=True)

        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        dst = os.path.join(rw.HERE, f'water_results_{tag}.json')
        shutil.copy(res_path, dst)
        print(f'  기기명 사본 저장: {dst}', flush=True)

    sys.exit(rc)
