"""작업 용량 v3 — 이완된 구조(charged_v3) 기준. 랩탑 등 별도 기기에서 돌리기 좋다.

[왜 이것을 다른 기기로 빼나]
    이 배치는 **건조 계열**이라 한 작업이 약 2.3시간입니다. 물이 낀 작업(9~20시간)
    과 달리 코어가 적은 기기에서도 끝납니다. 20작업이면 4코어에서 약 12시간입니다.

    그리고 이것이 본 기계의 **임계 경로 위에** 있습니다. 여기서 빼내면 본 기계가
    수분 v3(27시간)를 7시간 일찍 시작합니다. 같은 시간에 두 배치가 동시에 갑니다.

[대상 — v2 와 같은 다섯에 saIm100 을 더한다]
    앞의 다섯은 v2 와 **직접 비교**하기 위한 것입니다. 그래야 차이를 "이완 때문"
    이라고 말할 수 있습니다.

[saIm100 을 되살리는 근거 — 처음 적었던 이유는 틀렸다]
    처음에 "수분 v2 가 20/20 으로 끝났으므로 넣을 근거가 생겼다" 고 적었습니다.
    **그것은 근거가 아닙니다.** 계산이 끝났다는 사실과 기준을 통과했다는 사실은
    다릅니다. run_working_capacity.py 가 경고한 자기합리화에 그대로 걸리는
    문장이었고, 지적을 받고 고칩니다.

    진짜 근거는 이렇습니다.

    종료 판정의 출처가 **철회됐습니다.** 그 판정은 RH90 유지율 38.1 ± 1.2% 에
    근거했는데, 그 값은 v1 구조에서 나온 것입니다. 2026-08-14 에 빌더가 벤조
    고리 부착 원자를 고정 인덱스로 고르는 결함이 드러나 **v1 치환 구조 결과는
    전량 폐기**됐습니다(STRUCTURE_DEFECT.md). 38.1% 도 그때 같이 폐기된
    숫자입니다. 살아 있는 판정이 아니라 이미 무효가 된 판정입니다.

    그리고 같은 기준을 고친 구조에 **다시 적용**했습니다(수분 경쟁 v2, 20/20):

        구조       CO2 RH0    CO2 RH90    유지율        판정(50% 기준)
        base        0.6711     0.6513     97.0 ± 3.1%   통과
        saIm025     0.9923     0.8724     87.9 ± 3.2%   통과
        saIm050     1.4109     1.1356     80.5 ± 1.6%   통과
        saIm075     1.8265     1.3127     71.9 ± 3.4%   통과
        saIm100     2.3046     1.3477   **58.5 ± 2.2%** 통과 (50% 대비 3.9시그마)

    기준을 바꾸지 않았습니다. 50% 그대로이고, 유지율의 정의도 그대로입니다.
    바뀐 것은 구조뿐이고, 그래서 값이 38.1 에서 58.5 로 갔습니다.

    **다만 표를 읽을 때 붙일 단서가 있습니다.** saIm100 은 다섯 중 유지율이
    가장 낮고 물 흡착량이 가장 많습니다(RH90 에서 2.7887 mol/kg). 유지율이
    치환율에 대해 단조 감소하므로 **선을 넘지는 않았지만 선에 가장 가깝습니다.**
    작업 용량이 좋게 나오더라도 "습윤 조건에서 여유가 가장 적은 조성" 이라는
    말을 함께 적어야 합니다.

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
