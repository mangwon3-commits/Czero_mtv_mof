"""작업 용량 재계산 (charged_v2 기준).

[왜 지금 이것인가]
    v2 GCMC 가 끝나면서 상위권이 통째로 바뀌었습니다. 그런데 **높은 Q_st 와
    선택도가 접근가능부피(AV)의 급감과 함께 왔습니다.**

        base       AV 989.8
        saIm075    AV 324.8   Q_st 32.32  선택도 128
        mslm075    AV 263.6   Q_st 36.90  선택도 336
        saIm100    AV 525.5   Q_st 34.33  선택도 231

    기공이 거의 닫히면 CO2 가 좁은 자리에 갇혀 Q_st 와 선택도가 올라갑니다.
    **그것은 잘 잡는다는 뜻이지 잘 쓴다는 뜻이 아닙니다.** 놓지 못하면
    작업 용량이 0 에 가까워집니다. 그래서 흡착 결과만으로 순위를 말하면 안 되고
    여기서 갈립니다.

[대상]
    base / saIm025 / saIm050 / saIm075 는 계열의 연속성 때문에,
    mslm075 는 v2 에서 Q_st 최고(36.90)로 올라왔기 때문에 넣습니다.
    v1 에서 mslm 은 "최하위" 로 분류됐는데 그 판정 자체가 깨진 구조에서
    나온 것이었습니다 -- mslm050/075 는 v1 에서 아예 만들어지지도 않았습니다.

    saIm100 은 뺐습니다. v1 수분 경쟁에서 종료 판정을 받았고, 재판정은
    지금 도는 수분 v2 가 줍니다. 그 결과를 보고 넣을지 정합니다.

[HERE 까지 옮기는 이유]
    run_working_capacity.py 는 RESULT 를 모듈 상수로 두지만(54행) 76행이
    `os.path.join(HERE, 'structures')` 를 **함수 안에서** 만듭니다.
    HERE 를 옮기지 않으면 v2 를 돌리면서 v1 폴더를 뒤집니다.
    run_water_v2.py 에서 같은 함정에 실제로 빠졌습니다.
"""
import os
import sys

import run_working_capacity as wc

REAL = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(REAL, 'v2_wc')
os.makedirs(V2, exist_ok=True)

wc.HERE = V2
wc.CHARGED = os.path.join(REAL, 'charged_v2')
wc.RUNS = os.path.join(REAL, 'wc_runs_v2')
wc.RESULT = os.path.join(V2, 'working_capacity.json')
wc.TARGETS = ['base', 'saIm025', 'saIm050', 'saIm075', 'mslm075']
wc.MAX_WORKERS = int(os.environ.get('WC_V2_WORKERS', '4'))

if __name__ == '__main__':
    print('작업 용량 v2', flush=True)
    print(f'  입력   {wc.CHARGED}', flush=True)
    print(f'  작업   {wc.RUNS}', flush=True)
    print(f'  결과   {wc.RESULT}', flush=True)
    print(f'  대상   {wc.TARGETS}', flush=True)
    print(f'  워커   {wc.MAX_WORKERS}', flush=True)
    missing = [t for t in wc.TARGETS
               if not os.path.exists(os.path.join(wc.CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print(f'  !! charged_v2 에 없음: {missing}', flush=True)
        sys.exit(1)
    print('  (이어받기 가능)' if os.path.exists(wc.RESULT)
          else '  (처음부터)', flush=True)
    print(flush=True)
    sys.exit(wc.main())
