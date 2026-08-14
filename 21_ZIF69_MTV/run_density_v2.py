"""밀도맵 재계산 (charged_v2 기준).

[왜 다시 하는가]
    STRUCTURE_DEFECT.md -- 빌더가 치환기를 엉뚱한 탄소에 달아, 24개 자리 중 18개가
    깨져 있었습니다. 기존 density/ 의 saIm025~saIm100 여덟 폴더는 그 구조에서 나온
    것이라 무효입니다. base 두 개(q_on/q_off)만 유효합니다 -- 무치환 모체는 결함
    검사를 통과했습니다.

    덤으로 조성 이름표도 틀렸습니다. 옛 saIm050 은 실제 14/24 = 58.3%,
    saIm075 는 17/24 = 70.8% 였습니다(AUDIT_20260814.md 3절). 즉 옛 맵은
    "무엇을 그린 것인지"조차 이름과 달랐습니다.

[왜 원본을 고치지 않고 감싸는가]
    같은 작업 디렉터리를 다른 세션이 함께 쓰고 있습니다(SESSION_LOG.md).
    원본을 편집하면 상대 세션과 부딪힙니다. 그리고 옛 결과를 재현할 수단을
    남겨야 합니다.

[HERE 까지 옮기는 이유 -- run_water_v2.py 에서 겪은 것]
    run_density_map.py 236행이 결과 파일을 모듈 상수가 아니라
    `os.path.join(HERE, 'density_results.json')` 로 **함수 안에서 직접** 만듭니다.
    CHARGED 와 OUT 만 바꾸면 v2 를 돌려 놓고 **v1 의 density_results.json 을
    덮어씁니다.** HERE 를 함께 옮기면 그 줄이 따라옵니다.

    HERE 는 44~46·236행 네 군데에서만 쓰이고 보조 스크립트를 찾는 데는 쓰이지
    않습니다(grep 으로 확인). 그래서 옮겨도 안전합니다.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(REAL, 'density_v2')
os.makedirs(V2, exist_ok=True)

# 순서 주의. HERE 를 옮기고, HERE 에서 파생되던 것을 전부 다시 지정합니다.
rd.HERE = V2                                       # density_results.json 이 여기로
rd.OUT = V2                                        # 작업 폴더도 여기 밑으로
rd.CHARGED = os.path.join(REAL, 'charged_v2')
rd.MAX_WORKERS = int(os.environ.get('DENSITY_WORKERS', '4'))

if __name__ == '__main__':
    print('밀도맵 v2', flush=True)
    print(f'  입력   {rd.CHARGED}', flush=True)
    print(f'  출력   {rd.OUT}', flush=True)
    print(f'  결과   {os.path.join(rd.HERE, "density_results.json")}', flush=True)
    print(f'  워커   {rd.MAX_WORKERS}', flush=True)
    print(f'  조성   {rd.TARGETS}  x 전하 ON/OFF', flush=True)

    if not os.path.isdir(rd.CHARGED):
        print(f'  !! 전하 CIF 폴더 없음: {rd.CHARGED}', flush=True)
        sys.exit(1)
    missing = [t for t in rd.TARGETS
               if not os.path.exists(os.path.join(rd.CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print(f'  !! charged_v2 에 없는 조성: {missing}', flush=True)
        sys.exit(1)

    old = os.path.join(rd.HERE, 'density_results.json')
    print('  (이어받기: 기존 v2 결과 있음)' if os.path.exists(old)
          else '  (처음부터 -- 이어받을 v2 결과 없음)', flush=True)
    print(flush=True)
    sys.exit(rd.main())
