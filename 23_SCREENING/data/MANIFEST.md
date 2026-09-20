# 23_SCREENING/data — 무엇을 어디에 둘 것인가

`screen_core.py` 가 읽는 입력과, 원본 노트북이 참조하던 파생 파일 목록입니다.

> **2026-09-20 20:12 갱신** — 사용자가 `D:\CoRE-MOF-Tools-main.zip`(599 MB, md5 `79213f201dec0cbefd19000d7a93d701`)을
> 갖고 있음을 확인했고, 그 안에서 **라이선스와 자료 위치가 확정됐습니다**. 아래 §0 이 결론입니다.
> 개봉 기록: `../ZIP_FINDINGS_20260920.md`

## 0. 결론 — 무엇을 올리고 무엇을 올리지 않을 것인가

**라이선스는 CC-BY-4.0 입니다** (`LICENSE` + `setup.py` 의 `license="CC-BY-4.0"`).
출처를 밝히면 **재배포가 허용됩니다.** "확인 전에는 올리지 마십시오" 라는 옛 경고는 이것으로 해제합니다.
다만 **허용된다고 다 올릴 이유는 없습니다** — 저장소에 들어가는 순간 모든 기기가 매번 받습니다.

> **2026-09-20 21:0x — 아래를 전부 실행했습니다.** 이 절은 이제 기록입니다.

    올린다      ✅ `CR_meta_data_SI_slice.json` 3.45 MB — 원본 19.9 MB 에서 RACs·water.GEMC 를 뺀 것.
                   원본과 **같은 수**를 냅니다(2657/2233/955 · 교집합 754 · 창 63/52). 만든 스크립트 `../make_slice.py`.
                ✅ `SOURCE.md`  (출처·md5·라이선스·인용·안 올린 것과 이유)
                ✅ `MOF_Project_Master_Data.pkl` 698 KB — 루트에서 이리로 옮김. 최종 115종 정본.
    안 올린다   ⬛ zip 통째 599 MB / 압축 해제 1.74 GB   (md5 79213f201dec0cbefd19000d7a93d701, `D:\` 에 보관)
                ⬛ CoREMOF/models/ 1.31 GB — 우리가 안 씁니다
                ⬛ NCR (계산 준비가 안 된 쪽) 6,520 CIF
                ⬛ CR_meta_data_SI.json 원본 19.9 MB — 슬라이스로 대체 (md5 b39cbc1d4376416e5dc3eb5e2f5a7f6a)
                ⬛ 파생 CSV/XLSX 20여 개 — `screen_core.py` 로 다시 만듭니다 (§3)
    나중에      ⬜ CR CIF 2,737개(47.7 MB) — 갈래 (B) 를 실제로 시작할 때. 그때는 **쓰는 것만** 골라서.

**zip 원본은 D 드라이브에 그대로 두십시오.** 정본은 거기 있고, 저장소에는 "어디서 어떻게 받는지" 와
md5 만 남깁니다. 이게 §5 의 요구("다른 기기가 재현 가능할 것")를 크기 없이 만족시키는 방법입니다.

### 루트 정리도 같이 했습니다 (커밋 `5f4a58a` 가 올린 업스트림 파일)

    LICENSE · README.md · setup.py · env.yaml · logo.png  →  `../upstream/` 로 이동 (+ `README-왜여기있나.md`)
    MOF_Project_Master_Data.pkl                           →  이 폴더로 이동
    MOF Screening.ipynb (25 MB)                           →  삭제. 코드는 `../MOF_Screening_original_stripped.ipynb`
                                                             에 동일(md5 fd97c0a0…), 글자 출력은 `../notebook_outputs_20260920.txt` 에 보존
    screening (1 B 빈 파일)                                →  삭제
    README.md (우리 것)                                    →  새로 씀. **우리 저장소 라이선스는 아직 미정입니다.**

## 1. 반드시 필요한 것

    CR_meta_data_SI.json     노트북이 읽는 **옛 판**. {mof_id: record} 평평한 사전.
                             필드: Zeopp.PLD/LCD/VF · CrystalNets.all_nodes · water.water_classification · Widom · GEMC
                             ⚠ **zip 안에 없습니다.** 사용자가 따로 갖고 있는 파일입니다.

    CoREMOF/data/CR.json     zip 안의 **신 판**, 40.3 MB. {unit, ASR 8857, FSR 7635, Ion 710} = 17,202 레코드.
                             필드 이름이 평평해짐: PLD · Topology.AllNode · WaterClass · Widom · GEMC
                             `screen_core.py` 가 **두 판을 이름 별칭으로 둘 다 읽습니다.**

두 판이 같은 물질을 같은 값으로 담는지 **아직 대조하지 않았습니다.** 노트북 결과(115종)를 재현하려면 옛 판이 필요합니다.

### 슬라이스를 만드는 법 (권장)
17,202 레코드에서 관문·순위에 쓰는 필드만 뽑으면 수 MB 로 줄어 **그냥 커밋**할 수 있습니다.

    python3 - <<'EOF'
    import json
    src = json.load(open('/mnt/d/…/CR.json'))          # zip 에서 추출한 것
    KEEP = ('PLD','LCD','VF','Dimension','Density','Topology','WaterClass','Widom','hasOMS','Metal','refcode','DOI')
    out = {s: {k: {f: v[f] for f in KEEP if f in v} for k, v in src[s].items()} for s in ('ASR','FSR','Ion')}
    json.dump(out, open('CR_slice.json','w'))
    EOF

**GEMC(물 등온선)는 빼십시오** — 레코드당 수십 줄이고 우리는 §7 이유로 인용하지 않습니다.

## 2. 원본 노트북이 만들어 쓰던 파생 파일 (지금 저장소에 없음 — 그래서 셀 대부분이 못 돕니다)

    N2_Sieving_Group_63_MOFs.csv        '매직 윈도우' 63종 (PLD 3.3~3.6 & water weak)
    High_Flux_Bottleneck_52_MOFs.csv    '호리병' 52종 (PLD 3.7~4.2 & LCD>=5.5 & water weak)
    MAGIC_WINDOW_63_MOFS.csv · Bottleneck_MOFS.csv      위 둘의 옛 이름
    Tier1_Ultimate_Targets_ColorSynced.csv 외 CSV/XLSX 20여 개 · PDF/PNG 40여 개(Frontier 도면)

    MOF_Project_Master_Data.pkl         ← **zip 안에 있습니다.** 115행 × 22열, 위 둘을 합친 최종본.
                                           복원해 확인함(`../ZIP_FINDINGS_20260920.md` §3).

⚠ **파생 파일은 저장소에 넣지 마십시오.** 입력 하나에서 `screen_core.py` 로 다시 만들 수 있고,
   넣으면 "어느 판으로 만든 CSV 인가" 를 아무도 모르게 됩니다(이 저장소가 태그 사본 중복으로 이미 데인 자리).
   `MOF_Project_Master_Data.pkl` 은 예외 후보입니다 — **노트북 결과의 정본**이라 우리 재현과 대조할 기준이 됩니다.
   0.7 MB 라 크기 문제도 없습니다. 다만 판다스 3 판 피클이라 이 기기 환경에서 그냥은 안 열립니다(우회 방법은 개봉 기록에).

## 3. 올리는 방법 — 크기로 나눕니다

    < 10 MB    그냥 커밋. 가장 좋습니다 — 정본이 저장소 안에 있게 됩니다.
    10~100 MB  git LFS. `git lfs track "23_SCREENING/data/*.json"`
    > 100 MB   **커밋하지 말고** 받는 법 + md5 만 남깁니다.  ← zip(599 MB) 이 여기.

## 4. 어느 경우든 반드시 남길 것 (`SOURCE.md`)

    출처      https://github.com/Chung-Research-Group/CoRE-MOF-Tools  (미러: mtap-research/CoRE-MOF-Tools)
              PyPI `CoREMOF-tools` 0.3.1 · Zenodo doi 10.5281/zenodo.15055758
    판        SI 부분집합인지 본편(CSD)인지 — 노트북 셀 4 가 "본편 데이터(CSD)를 가져와야" 라고 적어 둠.
              zip 은 **SI 판**입니다(`CoREMOFDBSI_0613/SI/`). 본편은 CSD 라이선스가 따로 필요합니다.
    md5       zip: 79213f201dec0cbefd19000d7a93d701   (슬라이스를 만들면 그것도 따로)
    날짜      zip mtime 2026-09-20 19:58:53 +0900. **내려받은 날짜는 사용자 확인 필요**(mtime ≠ 배포일).
    라이선스  **CC-BY-4.0** — 재배포 허용, 출처 표시 의무.
    인용      Zhao G. 외, *Matter* 8 (2025) 102140, doi 10.1016/j.matt.2025.102140

## 5. 왜 이게 중요한가
`CLAUDE.md` §8: "세션은 서로의 대화를 모릅니다. 공유되는 것은 **이 저장소의 파일뿐**입니다."
입력 자료가 밖에 있으면 다른 기기 세션이 이 스크리닝을 재현할 수 없습니다.
**지금 정확히 그 상태입니다** — 랩탑·laptop2 는 D 드라이브를 못 봅니다.
