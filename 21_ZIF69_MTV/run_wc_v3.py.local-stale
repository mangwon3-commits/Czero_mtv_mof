"""작업 용량 v3 — 이완된 구조(charged_v3) 기준. 랩탑 등 별도 기기에서 돌리기 좋다.

[왜 이것을 다른 기기로 빼나]
    이 배치는 **건조 계열**이라 한 작업이 약 2.3시간입니다. 물이 낀 작업(9~20시간)
    과 달리 코어가 적은 기기에서도 끝납니다. 20작업이면 4코어에서 약 12시간입니다.

    그리고 이것이 본 기계의 **임계 경로 위에** 있습니다. 여기서 빼내면 본 기계가
    수분 v3(27시간)를 7시간 일찍 시작합니다. 같은 시간에 두 배치가 동시에 갑니다.

[대상 — v2 와 같은 다섯에 saIm100 을 더한다]
    앞의 다섯은 v2 와 **직접 비교**하기 위한 것입니다. 그래야 차이를 "이완 때문"
    이라고 말할 수 있습니다.

    saIm100 은 v2 에서 뺐던 것입니다 -- v1 수분 경쟁에서 종료 판정을 받았고
    재판정을 수분 v2 에 맡겼기 때문입니다. **그 수분 v2 가 2026-08-17 00:56 에
    20/20 으로 끝났으므로** 이제 넣을 근거가 생겼습니다. 비교표에서는 앞의
    다섯만 v2 와 나란히 놓고, saIm100 은 신규 항목으로 답니다.

[조건 — 원본과 동일]
    흡착   0.15 bar / 298 K
    VSA-1  0.10 bar / 298 K
    VSA-2  0.05 bar / 298 K
    TSA    0.15 bar / 373 K

[HERE 까지 옮기는 이유]
    run_working_capacity.py 는 76행에서 `os.path.join(HERE, 'structures')` 를
    **함수 안에서** 만듭니다. HERE 를 옮기지 않으면 v3 를 돌리면서 v1 폴더를
    뒤집니다. run_water_v2.py 에서 같은 함정에 실제로 빠졌습니다.
"""
import os
import sys

import run_working_capacity as wc

REAL = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REAL, 'v3_wc')
os.makedirs(V3, exist_ok=True)

wc.HERE = V3
wc.CHARGED = os.path.join(REAL, 'charged_v3')
wc.RUNS = os.path.join(REAL, 'wc_runs_v3')
wc.RESULT = os.path.join(V3, 'working_capacity.json')
# 앞의 다섯이 v2 비교군. saIm100 은 신규.
wc.TARGETS = ['base', 'saIm025', 'saIm050', 'saIm075', 'mslm075', 'saIm100']
wc.MAX_WORKERS = int(os.environ.get('WC_V3_WORKERS', '4'))

if __name__ == '__main__':
    print('작업 용량 v3 (이완된 구조)', flush=True)
    print(f'  입력   {wc.CHARGED}', flush=True)
    print(f'  작업   {wc.RUNS}', flush=True)
    print(f'  결과   {wc.RESULT}', flush=True)
    print(f'  대상   {wc.TARGETS}', flush=True)
    print(f'  워커   {wc.MAX_WORKERS}', flush=True)
    missing = [t for t in wc.TARGETS
               if not os.path.exists(os.path.join(wc.CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print(f'  !! charged_v3 에 없음: {missing}', flush=True)
        sys.exit(1)
    # 작업 단위 이어받기가 있으므로 중단 뒤 그냥 다시 띄우면 됩니다.
    print('  (이어받기 가능)' if os.path.exists(wc.RESULT) else '  (처음부터)',
          flush=True)
    print(flush=True)
    sys.exit(wc.main())
