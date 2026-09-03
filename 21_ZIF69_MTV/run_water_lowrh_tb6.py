"""T-B6 **예비** — azbIm 저RH 물 (RH 5/10/15%) × azbIm050 / azbIm100 / bIm100 (9작업).

[사전 등록] DESIGN_STUDY_20260903.md T-B6 — 정식 판정 문턱은 **T-B1(TIP5P-Ew
ΔH_vap 자)** 이 끝나야 정해집니다. 이 러너는 판정하지 않고 **수치만** 만듭니다.
tb5_chain.sh 5단계에서 부릅니다.

[무엇을 재는가]
    run_water_lowrh.py 와 같은 축입니다 — 물 클러스터 온셋(≈RH30) 아래의 초기
    기울기 = 골격 자체의 물 친화도(Chanut 2017 의 x 축). 아자 N 이 물 자리가
    되는지(DESIGN_STUDY R-7, 주 제안의 최대 위험)를 여기서 처음 봅니다.
    bIm100 은 "N 이 아니라 Cl 제거가 원인" 인지 가르는 대조군입니다.

[바뀌지 않는 것]
    run_water.py 그대로. 엔진·힘장·CO2 모델(García-Sánchez)·물 정의(TIP5P-Ew
    5자리)·CO2 분압 0.15 bar·사이클(5,000+15,000) 전부 동일. 바뀌는 것은
    대상과 RH_LIST 뿐.

[출력을 왜 분리하나]
    run_water_lowrh.py 의 guard 가 대상 6종을 못 박고 있어(08-25 사고 이후) 그
    파일을 늘리지 않습니다. 결과는 v3_water_lowrh_tb6/ 로 따로 받고, 저RH 18작업
    표(v3_water_lowrh/)와 사람이 합칩니다. 실행 폴더도 water_runs_lowrh_tb6/ 로
    분리해 이어받기가 섞이지 않게 합니다.

사용:
    WATER_TB6_WORKERS=<코어수> RASPA_DIR=$HOME/RASPA/simulations python run_water_lowrh_tb6.py
"""
import os
import shutil
import sys

HERE_REAL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE_REAL)

import run_water as rw                                        # noqa: E402

OUT = os.path.join(HERE_REAL, 'v3_water_lowrh_tb6')
os.makedirs(OUT, exist_ok=True)

rw.HERE = OUT
rw.CHARGED = os.path.join(HERE_REAL, 'charged_v3')
rw.RUNS = os.path.join(HERE_REAL, 'water_runs_lowrh_tb6')
rw.WATER_DEF = os.path.join(HERE_REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_TB6_WORKERS', '4'))
rw.RH_LIST = [0.15, 0.10, 0.05]          # 비싼 것 먼저(LPT)
rw.TARGETS = [
    ('azbIm050', '5-azabenzimidazole 50% — T-B6 대상'),
    ('azbIm100', '5-azabenzimidazole 100% — T-B6 대상'),
    ('bIm100',   'benzimidazole(H) 100% — Cl 제거 대조군'),
]

if __name__ == '__main__':
    print('T-B6 예비 — 저RH 물, azbIm050/azbIm100/bIm100 (9작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}   RH {rw.RH_LIST}', flush=True)

    # 좁힌 러너가 사고를 낸 전력(08-25 d0b6f50)이 있어 범위를 못 박습니다.
    if [n for n, _ in rw.TARGETS] != ['azbIm050', 'azbIm100', 'bIm100'] \
            or rw.RH_LIST != [0.15, 0.10, 0.05]:
        print('  !! 대상/RH 가 등록된 9작업이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {" ".join(missing)}', flush=True)
        sys.exit(1)
    # 배포본 TraPPE/water.def 는 3자리라 조용히 다른 물로 계산됩니다.
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
