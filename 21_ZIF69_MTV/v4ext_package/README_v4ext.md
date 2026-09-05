# v4 습윤 작업 용량 2종 — 계산 부탁 (sa25nb75, ms50nb50)

기존 MTV-ZIF_계산지원 꾸러미 **위에** 이 폴더 내용을 덮어 주세요
(21_ZIF69_MTV/ 아래로 charged_v3 CIF 2개와 러너 1개가 들어갑니다).
기존 러너(run_humid_wc.py, run_humid_wc_v3.py)와 19_WaterCompetition/water.def
를 그대로 씁니다 — 규약은 수분 v3 때와 동일(15000 사이클, TIP5P-Ew 5사이트).

    cd <꾸러미>/21_ZIF69_MTV
    export RASPA_DIR=$HOME/RASPA/simulations
    HWC_V4E_WORKERS=6 python -u run_humid_wc_v4ext.py 2>&1 | tee humid_v4ext.log

작업 6개(2조성 x ads/tsa/vsa), 6워커면 전부 병렬입니다. 벽시계는 가장 긴
ads 작업이 정하며 귀측 하드웨어 기준 10~13시간 예상입니다(수분 v3 실측
기준). **내일 20시 취합이 목표라 시작이 이를수록 좋습니다.**
완료 파일 v4_humid_wc/humid_working_capacity_v4ext.json + humid_v4ext.log
를 회신해 주시면 됩니다. 중단되면 같은 명령 재실행(작업 단위 이어받기).
