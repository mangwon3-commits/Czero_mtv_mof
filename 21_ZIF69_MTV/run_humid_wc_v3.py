"""습윤 작업 용량 v3 — 이완된 구조에서, 물이 낀 채로 재생까지 본다.

[이 계산만이 답하는 질문]
    건조 작업 용량은 "붙였다 떼는 양" 을 재지만 물이 없습니다. 수분 경쟁은
    물이 있지만 흡착 조건 하나만 봅니다. **실제 공정은 둘 다입니다** --
    습한 배가스에서 붙이고, 습한 채로 떼야 합니다.

    핵심은 TSA 에서 온도가 오르면 포화증기압이 함께 올라 **RH 가 90 -> 2.8%
    로 떨어진다**는 것입니다(물 분압은 그대로 2852 Pa). 즉 온도를 올리는 것만으로
    물이 스스로 빠질 수도 있습니다. VSA 는 온도가 그대로라 RH 90% 가 유지되고
    물이 계속 자리를 차지합니다. 그 차이를 재는 것이 이 배치입니다.

[대상 — v1 의 셋에 saIm100 을 더한 넷]
    v1(humid_working_capacity.json)이 base / saIm050 / saIm075 를 했습니다.
    직접 비교를 위해 그대로 두고, saIm100 을 더합니다.

    saIm100 은 수분 경쟁 v2 에서 RH90 유지율 58.5 +- 2.2% 로 사전 등록 기준
    (50%)을 3.9시그마 위에서 통과했습니다. 다만 **다섯 중 가장 낮고 물을 가장
    많이 먹습니다**(RH90 에서 2.7887 mol/kg). 습한 조건의 재생이 바로 그 약점이
    드러나는 자리이므로, 여기에 넣지 않으면 이 조성을 추천할 수 없습니다.

[비용]
    물이 낀 작업이라 한 건이 길다. 4종 x 3조건 = 12작업, 워커 7 에서 약 16시간.
"""
import os
import sys

import run_humid_wc as hw

REAL = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REAL, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

# HERE 파생 경로를 전부 다시 지정합니다. CHARGED/RUNS 만 바꾸면 결과 파일이
# 옛 자리를 가리켜 v1 결과를 보고 전부 건너뜁니다(run_water_v2 에서 겪음).
hw.HERE = V3
hw.CHARGED = os.path.join(REAL, "charged_v3")
hw.RUNS = os.path.join(REAL, "humid_wc_runs_v3")
hw.RESULT = os.path.join(V3, "humid_working_capacity.json")
hw.TARGETS = ["base", "saIm050", "saIm075", "saIm100"]
hw.MAX_WORKERS = int(os.environ.get("HWC_V3_WORKERS", "7"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 (이완된 구조)", flush=True)
    print(f"  입력   {hw.CHARGED}", flush=True)
    print(f"  작업   {hw.RUNS}", flush=True)
    print(f"  결과   {hw.RESULT}", flush=True)
    print(f"  대상   {hw.TARGETS}", flush=True)
    print(f"  워커   {hw.MAX_WORKERS}", flush=True)
    missing = [t for t in hw.TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없음: {missing}", flush=True)
        sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
