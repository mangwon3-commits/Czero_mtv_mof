# 이 폴더 자료의 출처 (2026-09-20 21:0x 작성)

## 저작·라이선스

    저작    Guobin Zhao (sxm13) 외 — CoRE-MOF-Tools / CoRE MOF DB
    라이선스 **CC-BY-4.0** (전문: `../upstream/LICENSE`) — 재배포 허용, **출처 표시 의무**
    저장소  https://github.com/Chung-Research-Group/CoRE-MOF-Tools
            미러 https://github.com/mtap-research/CoRE-MOF-Tools · PyPI `CoREMOF-tools` 0.3.1
    Zenodo  doi 10.5281/zenodo.15055758
    인용    Zhao G, Brabson L, Chheda S, Huang J, Kim H, Liu K, et al.
            "CoRE MOF DB: a curated experimental metal-organic framework database with
             machine-learned properties for integrated material-process screening."
            *Matter* **8** (2025) 102140.  doi 10.1016/j.matt.2025.102140

**이 자료를 쓴 결과를 발표·출판할 때 위 인용을 넣어야 합니다.**

---

## 1. `CR_meta_data_SI_slice.json`  ← 저장소에 있음 (3.45 MB)

`screen_core.py` 의 기본 입력입니다.

    md5        688b790046ef910ff7d5713c89581704
    레코드     2,737 (CoRE MOF SI 부분집합, 옛 스키마)
    보존 필드  Zeopp · CrystalNets · water(GEMC 제외) · metal · stability · heat_capacity
               · structure_info · reference · id
    뺀 것      RACs(분자 서술자 150여 개 — 관문·순위에 안 씀)
               water.GEMC(물 등온선 원문 — 우리 물 규약과 달라 인용 안 함, `../ZIP_FINDINGS_20260920.md §7`)
    만든 법    `python3 make_slice.py <원본> <출력>`  (같은 폴더의 스크립트)
    검산       원본과 슬라이스가 같은 수를 냅니다 — 관문별 2657/2233/955 · 교집합 754 · 창 63/52.

### 원본(저장소에 없음)

    이름   CR_meta_data_SI.json
    크기   19.9 MB
    md5    b39cbc1d4376416e5dc3eb5e2f5a7f6a
    받은 곳 사용자가 2026-09-20 에 직접 제공(zip 밖의 별도 파일). 노트북 `MOF Screening.ipynb` 의 실제 입력.
    ⚠ **zip 안에는 없습니다.** 신판(`CoREMOF/data/CR.json`)과 값은 같습니다(refcode 로 짝지은 2,052건 중 Widom 다른 것 0건).

## 2. `MOF_Project_Master_Data.pkl`  ← 저장소에 있음 (698 KB)

스크리닝의 **최종 산출물**. 우리 재현과 대조하는 기준입니다.

    115행 × 22열 · `Filter_Type` = N2-Sieving(Narrow) 63 + High-Flux(Wide) 52
    주요 열: id · Zeopp · CrystalNets · PLD_value · LCD_value · water_class · node_stability
             · CO2_Affinity · Selectivity · Chemistry · Filter_Type · RACs
    출처   zip 안의 같은 이름 파일. 2026-09-20 사용자가 GitHub 웹으로 올린 것(커밋 `5f4a58a`)을 이 폴더로 옮김.
    ⚠ **판다스 3 판 피클**이라 이 기기 환경(pandas 2.3.3 / numpy 2.2.6)에서는 그냥 안 열립니다.
       우회 방법(StringArray 를 우회하는 커스텀 Unpickler)은 `../ZIP_FINDINGS_20260920.md §3` 에 있습니다.

## 3. 저장소에 **두지 않은** 것과 그 이유

    CoRE-MOF-Tools-main.zip     599 MB (압축 풀면 1.74 GB)  → `D:\` 에 그대로. md5 79213f201dec0cbefd19000d7a93d701
    CoREMOF/models/             1.31 GB — 우리가 안 씁니다
    CoREMOFDBSI_0613/SI/NCR/    계산 준비가 안 된 쪽 6,520 CIF
    CoREMOFDBSI_0613/SI/CR/     CR CIF 2,737개 (47.7 MB) — 갈래 (B) 를 실제로 시작할 때 **쓰는 것만** 가져옵니다
    CoREMOF/data/CR.json        40.3 MB 신판 — 옛 판과 값이 같아 지금은 불필요
    파생 CSV/XLSX 20여 개       `screen_core.py` 로 다시 만듭니다

`CLAUDE.md §8`: "세션은 서로의 대화를 모릅니다. 공유되는 것은 **이 저장소의 파일뿐**입니다."
→ 슬라이스 3.45 MB 하나로 랩탑·laptop2 도 이 스크리닝을 재현할 수 있습니다.
