# D8 — 노트북의 "CO₂ 작업 용량" 은 **물 등온선**입니다 (2026-09-21 00:02, 데스크탑 세션)

사용자 질문: *"내가 보낸 자료로부터 미리 내가 계산했던 로그가 남아있을 텐데"* — 남아 있습니다
(`notebook_outputs_20260920.txt`, 원본 25 MB 를 내리기 전에 글자 출력 259블록을 보존). 그 로그를 따라가 보니
**공정 성능 층 전체가 물 등온선을 CO₂ 로 읽고 있습니다.**

## 1. 증거 사슬

### ① 자료가 물이라고 적혀 있습니다
`water.GEMC` 의 AIF 머리말(예 `am7b10757_si_002_ASR_pacman`):

    _exptl_temperature 298
    _simltn_forcefield_adsorbent  UFF4MOF
    _simltn_forcefield_adsorptive **TIP4P**          ← 물입니다
    _units_loading  **Molecules/Supercell**          ← mmol/g 이 아닙니다
    # Setting: cutoff=9 Å, cycles 5E3 + 1.5E4 + 2.5E4

ASR 전체 8,448 레코드가 예외 없이 `TIP4P` 입니다(`ZIP_FINDINGS_20260920.md §7`).
같은 레코드에 **진짜 CO₂/N₂ 값은 따로** 있습니다 — `water.Widom = [6.876e-05, 1.360e-05]`.

### ② 셀 27 이 그 물 등온선을 `Isotherm_Data` 로 만듭니다

    def extract_isotherm_data(gemc_str):
        gemc_lines = gemc_dict.get('GEMC', [])        # ← 물
        ...
        p_val = float(parts[0]); q_val = float(parts[2])
        return {'Pressure': ..., 'Uptake': ...}
    final_clean_df['Isotherm_Data'] = final_clean_df['GEMC_data'].apply(extract_isotherm_data)

### ③ 셀 28·30·31·32·35·36 이 그것을 CO₂ 로 씁니다

    P_adsorption = 0.15  # 배가스 CO2 분압 (bar)
    P_desorption = 0.01  # 진공 펌프 탈착 압력 (bar)
    P_bar = P_raw / 100000.0
    popt_h, _ = curve_fit(henry_eq, P_bar, Uptake)
    K_synthetic = kH_fit / q_max_physical
    q_ads = pseudo_langmuir(0.15);  q_des = pseudo_langmuir(0.01)
    working_capacity = q_ads - q_des

`q_max_physical = (GPV × 1.03 / 44.01) × 1000` — **CO₂ 액체 밀도와 CO₂ 분자량**으로 상한을 잡고,
거기에 **물** 등온선의 기울기를 꽂습니다.

### ④ 재현했습니다 — 소수 셋째 자리까지 일치

창 115종에 셀 35 의 계산을 그대로 돌렸습니다.

    key                           GPV    q_max   q_ads0.15  WC      kH [mmol/g/bar]
    am7b10757_si_002_ASR_pacman   0.696  16.28   **11.568**  9.279   266.3
    am7b04265_si_002_FSR_pacman   0.499  11.68   ** 8.885**  6.844   247.3
    am7b04265_si_002_ASR_pacman   0.499  11.68   ** 9.810**  6.787   407.9
    d1cc04371d2_ASR_pacman        0.498  11.65   ** 8.563**  6.743   215.6
    …
    노트북 출력(셀 35)  q_ads  11.568  8.885  9.810  8.563  9.303  9.834  9.874  7.555  9.933  11.889
    이 재현            q_ads  11.568  8.885  9.810  8.563  9.303  9.834  9.874  7.555  9.933  11.889

**10개가 전부 일치합니다.** 경로가 확정됐습니다.

## 2. 겹친 결함 셋

    (ㄱ) **기체가 다름**   물 등온선을 CO₂ 로 읽음.
    (ㄴ) **단위 미환산**   적재량이 `Molecules/Supercell` 인데 `mmol/g` 로 다룸.
                          같은 레코드에 `_simltn_size 'Volume (cm3): 1.23e-20'` 과 `Density` 가 있어 환산이 가능한데 안 했음.
    (ㄷ) **자료 밖 외삽**  GEMC 압력은 0.1~1000(일부 4315) Pa = 1e-6~0.0432 bar.
                          거기서 **0.15 bar** 값을 냅니다 — 최고 자료점의 **3.5배 바깥**, 그것도 포화하는 양에 대해.

그래서 `q_ads(0.15 bar)` 가 7~12 mmol/g 으로 나옵니다.

## 3. 왜 이 값이 물리적으로 불가능한가 — 우리 자료가 자입니다

    우리 GCMC 0.15 bar 건조 CO₂ (31조성)   최소 0.416 · 중앙 0.752 · **최대 1.543** mmol/g
    우리 GCMC MUF-16 0.165 bar, 293 K      **1.1174** mmol/g
    같은 조건 **실측**(Qazvini·Telfer 2021)  **1.08** mmol/g   →  배율 **1.035**

**우리 파이프라인은 실측 MOF 의 0.15 bar 급 CO₂ 흡착을 3.5 % 안에서 맞춥니다.**
그 눈금에서 7~12 mmol/g 은 0.15 bar CO₂ 로 **측정된 적이 없는 값**입니다(문헌 최고 기록도 그 아래).
물 등온선이라면 자연스러운 크기입니다 — 1000 Pa(P/P₀ 0.22)에서 2.68 molecules/supercell 이 그대로 흘러 들어간 것입니다.

## 4. 못 쓰는 것 / 쓸 수 있는 것

    ❌ 못 씁니다 (전부 ③ 경로에서 나옴)
       q_ads_0.15bar · q_des_0.01bar · Working_Capacity_mmol/g · Recovery_% · Performance_Score
       DAC_Score · FlueGas_Score · Tier 1/2 랭킹 · Fully_Calibrated_PseudoLangmuir_Metrics.csv
       Final/Fixed/Hybrid_VSA_Process_Metrics.csv · Verified_Langmuir_MOFs.csv
       Tier1_Tier2_Survival_Frontier.pdf 및 같은 계열 도면
       (셀 71 의 Sips 피팅도 같은 `Isotherm_Data` 를 씁니다 — 같은 경로입니다.)

    ✅ 그대로 씁니다
       **`Widom` = [K_H(CO₂), K_H(N₂)]**  — 진짜 CO₂/N₂, mmol/g/Pa.
         순서는 크기로 확인했습니다(`ZIP_FINDINGS_20260920.md §4`). **`fig9_frontier.png` 의 두 축이 이것입니다.**
       **기하** PLD · LCD · VF · GPV · Dimension  (Zeo++, 우리와 같은 도구)
       **WaterClass** 와 그 **분류 문턱**(되찾음, `water_class.py`)
       **GEMC 물 등온선** — **물로서는 정본입니다.** 단위만 환산하면(`Molecules/Supercell` →
         `_simltn_size` 의 부피 × `Density` 로 질량을 얻어 mmol/g) 우리 물 K_H 와 **같은 양**이 됩니다.
       HeatCapacity · Stability(ML)

## 5. 그래서 "기존 MOF 와 비교가 불가능한가" 에 대한 답

**가능합니다.** 다만 노트북의 공정 성능 층을 거치지 말고 **Widom 과 물 등온선에서 직접** 가야 합니다.

    지금 되는 것   CO₂ 친화도 K_H · CO₂/N₂ 선택도 — `fig9` 의 축. CoRE 6,604종(관문 통과)이 그 위에 있습니다.
                   물 — CoRE 의 GEMC 물 등온선을 mmol/g 으로 환산하면 우리 39조성 물 K_H 와 직접 견줍니다.
                   기하 — `fig7` 왼쪽이 이미 그 비교입니다.
    남은 장애물    힘장 오프셋 하나뿐입니다. T-BR-1(`BRIDGE_CORE_REGISTRATION_20260920.md`)이 재고 있습니다.
    ⚠ 안 되는 것   "작업 용량" 축에서의 비교. CoRE 쪽에 **CO₂ 등온선이 아예 없기 때문**입니다 —
                   노트북이 만들어 낸 것이 아니라, 자료에 없는 것을 외삽한 것이었습니다.
                   CoRE 로 작업 용량을 비교하려면 **CO₂ 등온선을 우리가 계산해야** 합니다(갈래 B 의 확장).

## 6. 이 문서가 쓴 것

    자료  `CR_meta_data_SI.json`(사용자 제공, md5 b39cbc1d…) · `notebook_outputs_20260920.txt`
          `MOF_Screening_original_stripped.ipynb` 셀 27·28·30·31·32·35·36·71
          `21_ZIF69_MTV/results_v3.json` · `TNF_RESULTS_20260910.md`(MUF-16 실측 대조)
    새 계산 **0건**. 판정문이 아니라 감사 기록입니다 — 이의 창 없음.
