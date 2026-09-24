# MAGI-005 R1 (Junseok) 재현 자료

R1 본문 `../MAGI-005_R1_junseok.md` 의 각주가 가리키는 스크립트·중간 산출입니다. 봉인 폴더 `~/.mof_magi/MAGI-005/junseok/` 에서
**바이트 그대로** 옮겼습니다(아래 sha256 — R1 각주의 앞 16자와 대조). 계산은 저장소 기존 결과 JSON·CIF 에 대한 산술뿐입니다.

    실행 순서 (czeromof python, ASE 3.29 · scipy)
      python magi5_core.py  <출력 json>                 # 524 합침 · 금속 배위 분류 · 75.8 초과 목록   (J-1·J-3·J-4)
      python magi5_strat.py <magi5_core.json>           # PLD 층화 · 계열 묶음 · CIF 머리말            (J-3)
      python magi5_desc.py  <magi5_core.json>           # 자유 극성 |q| 밀도 · Spearman · n(0.15)/n(0.01) (J-5·J-11 각주)
      python magi5_ours.py  <magi5_core.json>           # 헨리 선형 지수 L · 우리 조성 같은 척도        (J-6·J-8·J-13)
      python magi5_med.py   <magi5_core.json> <magi5_ours.py 경로>   # 띠별 L·LCD 중앙 · 48행 |q| 중앙  (J-6·J-7·J-13)

    ⚠ 스크립트 안의 저장소 경로 D = '/home/mangwon/mof_project/21_ZIF69_MTV/' 는 Junseok 기기 경로입니다 — 자기 기기에 맞게 바꾸십시오.
    ⚠ magi5_ours.py 는 magi5_desc.py 를 import 하지 않고 같은 desc() 를 다시 정의합니다(파일 간 정의가 같음을 눈으로 확인하십시오).

    sha256
      5aa9d3282517a6da81e4f0fef74f39d419b4aecc45cf3b37bfa0b1fc01d3221b  magi5_core.json
      6b78de41f40f66ee6df7fa8005450347638342ae998e5c1c9229efd1eefb49d8  magi5_core.py
      6e7dd746208ae972d713d9bcaefb6eca23d49afd507a6013a96a7a5d96eb214d  magi5_desc.py
      2b9c21997c9da224f52e5da07a9dbed54a72d21f13851cca406d79091ecce61d  magi5_med.py
      d286293ec3a8db93b79031c2e10bbb7de77e26e1b8741a875e72fafefda3b2e2  magi5_ours.py
      3702df27bbe80c0120d05d7c4b07d0047b8e9c990adbf79a50052dc134171298  magi5_strat.py
