# 23_SCREENING/data — 무엇을 어디에 둘 것인가

`screen_core.py` 가 읽는 입력과, 원본 노트북이 참조하던 파생 파일 목록입니다.

## 1. 반드시 필요한 것 (없으면 CoRE 쪽이 안 돕니다)

    CR_meta_data_SI.json     CoRE MOF 메타데이터(SI 부분집합, 2,737종)
                             필드: Zeopp · CrystalNets · water · metal · id · GEMC(Widom)

## 2. 원본 노트북이 만들어 쓰던 파생 파일 (지금 저장소에 없음 — 그래서 셀 대부분이 못 돕니다)

    N2_Sieving_Group_63_MOFs.csv        매직윈도우 63종 (PLD 3.3~3.6 & water weak)
    High_Flux_Bottleneck_52_MOFs.csv    호리병 52종 (PLD 3.7~4.2 & LCD>=5.5 & water weak)
    MAGIC_WINDOW_63_MOFS.csv · Bottleneck_MOFS.csv      위 둘의 옛 이름
    Tier1_Ultimate_Targets_ColorSynced.csv 외 CSV/XLSX 20여 개 · PDF/PNG 40여 개(Frontier 도면)

⚠ **파생 파일은 저장소에 넣지 마십시오.** `CR_meta_data_SI.json` 하나에서 `screen_core.py` 로 다시 만들 수 있고,
   넣으면 "어느 판으로 만든 CSV 인가" 를 아무도 모르게 됩니다(이 저장소가 태그 사본 중복으로 이미 데인 자리).

## 3. 올리는 방법 — 크기로 나눕니다

    < 10 MB    그냥 커밋. 가장 좋습니다 — 정본이 저장소 안에 있게 됩니다.
    10~100 MB  git LFS. `git lfs track "23_SCREENING/data/*.json"`
    > 100 MB   **커밋하지 말고** 아래 `SOURCE.md` 형식으로 받는 법 + md5 만 남깁니다.

크기를 먼저 재십시오:  `ls -lh CR_meta_data_SI.json && md5sum CR_meta_data_SI.json`

## 4. 어느 경우든 반드시 남길 것 (`SOURCE.md`)

    출처      CoRE MOF 판(년도·버전)과 내려받은 URL
    판        SI 부분집합인지 본편(CSD)인지 — 노트북 셀 4 가 "본편 데이터(CSD)를 가져와야" 라고 적어 둠
    md5       파일 체크섬 (다른 기기가 같은 파일인지 확인하는 유일한 방법)
    날짜      내려받은 날 (`date` 로 — 짐작 금지)
    라이선스  CoRE MOF 재배포 조건. **확인 전에는 공개 저장소에 올리지 마십시오.**

## 5. 왜 이게 중요한가
`CLAUDE.md` §8: "세션은 서로의 대화를 모릅니다. 공유되는 것은 **이 저장소의 파일뿐**입니다."
입력 자료가 밖에 있으면 다른 기기 세션이 이 스크리닝을 재현할 수 없습니다. 지금 노트북이 정확히 그 상태입니다.
