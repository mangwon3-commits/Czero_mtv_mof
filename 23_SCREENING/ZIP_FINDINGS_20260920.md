# CoRE-MOF-Tools-main.zip 개봉 기록 (2026-09-20 20:12, 데스크탑 세션)

사용자가 D 드라이브에 둔 `D:\CoRE-MOF-Tools-main.zip` 을 열어 확인한 결과입니다.
**압축을 풀지 않고** `zipfile` 로 읽었습니다(1.74 GB 로 부풀고, WSL 루트는 C: 위 VHDX 입니다 — CLAUDE.md §5).

    파일      /mnt/d/CoRE-MOF-Tools-main.zip
    크기      627,873,526 바이트 (599 MB) · 압축 풀면 1.74 GB · 항목 9,892개
    md5       79213f201dec0cbefd19000d7a93d701
    받은 때   2026-09-20 19:58:53 (+0900)  ← 파일 mtime. 내려받은 날짜는 사용자 확인 필요
    정체      업스트림 저장소 통째 — Chung-Research-Group / mtap-research, `CoRE-MOF-Tools` (개발 Guobin Zhao)
    라이선스  **CC-BY-4.0** (`LICENSE`, `setup.py` 의 `license="CC-BY-4.0"`)
    인용      Zhao G. 외, *Matter* 8 (2025) 102140, doi 10.1016/j.matt.2025.102140 · Zenodo doi 10.5281/zenodo.15055758

## 1. 무엇이 들어 있나

    1,309.7 MB  CoREMOF/models/           ML 모델 가중치 339개 — **우리에게 불필요**
      277.6 MB  CoREMOFDBSI_0613/SI/      CIF 원본.  CR 2,737개 · NCR 6,520개  ← **구조 파일이 통째로 있음**
      133.3 MB  CoREMOF/data/             CR.json 40.3 MB · NCR.json 4.95 MB · SI/CR.zip 9.1 MB(CIF 2,664) · SI/NCR.zip
       24.2 MB  MOF Screening.ipynb       ← 사용자가 올린 노트북과 **바이트 단위로 동일**(md5 44ec03d95ca564d000d0da54292cfb7a)
       14.5 MB  .ipynb_checkpoints/MOF Screening-checkpoint.ipynb   (한 판 이전 사본)
        1.6 MB  .ipynb_checkpoints/Untitled-checkpoint.ipynb        (`extract_performance` 초기 판 — widom[0]/widom[1] 가정의 출처)
        0.7 MB  MOF_Project_Master_Data.pkl   ← **스크리닝의 최종 산출물**. 115행 × 22열
       13.6 MB  docs/ · 1.6 MB examples/ · setup.py · env.yaml · LICENSE

**따라서 `CR_meta_data_SI.json` 은 이 zip 안에 없습니다.** 대신 같은 자료의 **신판**인 `CoREMOF/data/CR.json` 이 있습니다.

## 2. 스키마가 두 판입니다 (이름만 바뀜 — 위치가 아님)

    옛 판 (노트북 입력 `CR_meta_data_SI.json`)      신 판 (`CoREMOF/data/CR.json`)
    Zeopp.PLD / Zeopp.LCD / Zeopp.VF            →  PLD / LCD / VF          (평평해짐)
    CrystalNets.all_nodes                       →  Topology.AllNode
    water.water_classification                  →  WaterClass
    Widom (2원소 배열) · GEMC                    →  그대로

신판 최상위는 `{unit, ASR, FSR, Ion}` 입니다 — `ASR` 8,857 · `FSR` 7,635 · `Ion` 710, 합 **17,202 레코드**.
ASR/FSR/Ion 은 **같은 골격의 다른 정리판**이므로 섞으면 한 물질이 여러 번 세어집니다.
`screen_core.py` 가 두 스키마를 **이름 별칭**으로 흡수하고, 신판 키에 계열을 붙여 돌려줍니다(`ASR/2020[Cu][sql]2[ASR]1`).

또한 `unit` 절이 단위를 못박습니다: **`Widom` = mmol/g/Pa** (= mol/kg/Pa, 우리 K_H 와 같은 단위), `GEMC` = Molecules/Supercell.

## 3. ★ 가장 큰 것 — 1순위 관문이 **항상 거짓**이었습니다 (D6)

노트북 1순위:

    (df['node_stability'] == 'stable') &   # 1순위: 관절이 무조건 튼튼할 것
    df['node_stability'] = df['CrystalNets'].apply(lambda x: x.get('all_nodes', 'unknown') ...)

그런데 `all_nodes`(신판 `Topology.AllNode`)에 들어 있는 것은 **위상 기호**입니다:

    unknown 6536 · pcu 1370 · dia 1149 · sql 1011 · unstable 342 · hcb 307 · rtl 276 · rna 255 · srs 228 …  고유값 361종
    'stable' 인 레코드 :  ASR 0 · FSR 0 · Ion 0  →  **전체 17,202 건 중 0건**

**그래서 "3중 관문 생존자 0명" 은 관문이 엄해서가 아니라 관문이 성립하지 않아서입니다.**
원본은 그 0 을 "관문이 너무 빡빡하다" 로 읽고 관문을 버린 뒤 사후 창(PLD 3.3~3.6 / 3.7~4.2)을 만들었습니다.
따라서 **뒤따른 63+52=115 종은 뼈대 안정성 검사를 한 번도 거치지 않았습니다.**

### 확인 — 최종 115종 안에 실제로 불안정한 것이 들어 있습니다
`MOF_Project_Master_Data.pkl` 을 복원해(판다스 판 차이로 `StringArray` 를 우회) 직접 셌습니다.

    행 115 (N2-Sieving 63 + High-Flux 52 — 노트북 수치와 일치) · water_class 전부 'weak' · PLD 3.306~4.199
    node_stability 분포:  unnamed 28 · pcu 16 · sql 16 · kgd 7 · **unstable 6** · sod 5 · bey 5 · pcu-h 3 · **mismatch 3** · …
      → 고친 관문에서 탈락 **9개**(unstable 6 + mismatch 3, 전부 'N2-Sieving' 창)
      → 위상 미상(unknown/unnamed) **28개** — 통과/탈락을 선택해야 하는 자리
      → 확실히 통과 **78개** (115 의 68 %)

### 관문을 고쳐 다시 걸면
"안정" 을 **`unstable`·`mismatch` 가 아님**으로 읽고 나머지 둘은 그대로 둡니다.

    ['unknown/unnamed' 통과]   ASR 3580 · FSR 2834 · Ion 190  →  교집합 **6,604종**
    ['unknown/unnamed' 탈락]   ASR 2537 · FSR 1904 · Ion 146  →  교집합 **4,587종**
    (관문별: 뼈대 16,789 · PLD≥3.3 13,387 · water weak 8,205 — `screen_core.py` 가 독립 재현)

**0개가 아니라 6,604개(또는 4,587개)입니다.** 사후 창은 필요 없었습니다.
위상 미상이 CR 의 38 % 이므로 **어느 쪽을 쓸지 먼저 등록해야 합니다** — 자료를 본 뒤 고르면 D3 의 반복입니다.

> CLAUDE.md §0 이 이 자리를 정확히 가리킵니다 — **"나쁜 결과를 보면 검사기부터 의심하고, 좋은 결과를 보면 기준을 의심하세요."**
> 0명이라는 나쁜 결과에서 의심했어야 할 것은 물질이 아니라 관문이었습니다.
> 우리도 같은 유형을 겪었습니다: 검사기 오탐 3건(멀쩡한 구조를 결함으로 찍음), 08-14 부착 원자 고정 인덱스.

## 4. Widom 두 원소의 정체 — **배포본 어디에도 적혀 있지 않습니다**

`widom[0]` = CO₂ 친화도, `widom[0]/widom[1]` = CO₂/N₂ 선택도라는 가정이 노트북 전체를 떠받칩니다. 검증했습니다.

    zip 전체(모델·CIF 제외)에서 "Widom" 문자열:  업스트림 문서·코드에 **딱 2회**, 둘 다 단위 문자열 'mmol/g/Pa' 뿐
    docs/source · docs/build · CoREMOF/*.py · examples/**  →  기체 이름 **0회**
    CoREMOF 패키지에 Widom 생성 코드 없음 (값은 미리 계산되어 CR.json 에 실려 옴)

즉 **저장물 안에서는 순서를 확정할 수 없습니다.** 외부 문헌(Matter 2025 / chemRxiv)은 UFF + TraPPE 로 CO₂·N₂ Henry 계수를
Widom 삽입으로 냈다고 적지만, **어느 쪽이 [0] 인지는 그 기술로도 안 정해집니다.**

### 순서를 물리로 재 본 두 시험 — 둘 다 "CO₂가 [0]" 을 **받쳐 주지 않습니다**

    ① 좁은 세공 가설:  CO₂(길이 4.9 Å)가 N₂(4.5 Å)보다 못 들어가는 곳이 있다면
       w0/w1 < 1 이 **작은 PLD 에 몰려야** 합니다. 실측은 반대입니다.
           PLD  0~3.0   <1 비율  3.2 %        PLD 6~8     6.4 %
           PLD  3.0~3.3        5.1 %          PLD 8~12    8.2 %
           PLD  4.0~5.0        6.3 %          PLD 12~     **15.1 %**   ← 넓을수록 늘어남
    ② OMS 가설:  열린 금속 자리는 CO₂ 사중극자를 강하게 잡으므로 w0/w1 이 **커져야** 합니다. 실측은 반대입니다.
           OMS 있음 n=5,698  w0/w1 중앙 **6.17**      OMS 없음 n=9,673  중앙 **9.73**

둘 다 교란(세공 크기와 OMS 가 얽힘)이 있어 **반증은 아닙니다.** 그러나 "위치 가정이 안전하다" 는 근거도 아닙니다.
`screen_core.py` 는 이 값을 `by-position(UNVERIFIED)` 로 표시하고, **확정 전에는 선택도를 인용하지 말라**고 경고합니다.

### 결정적 시험은 가능합니다 (제안 — 아직 안 돌림)
zip 안에 CR CIF 2,737개가 있습니다. 그 중 몇 개에 **UFF + TraPPE 로 CO₂ 와 N₂ Widom 을 각각 돌려**
저장된 두 값과 맞춰 보면 순서가 확정됩니다. **이것은 외부 자료를 해독하는 시험이지 우리 물질의 결과가 아니므로
우리 계열(`v3*`)에 절대 섞지 말고 별도 태그로 두어야 합니다.** 힘장이 우리 고정값(§1)과 다르다는 점도 그 이유입니다.

## 5. Widom 값에 발산이 섞여 있습니다

    ASR w[0] 최소/중앙/최대   3.022e-13 / 1.870e-04 / **1.877e+22**  mmol/g/Pa
    ASR w[1] 최대                                    **5.151e+22**

1 Pa 에서 10²² mol/kg 은 뜻이 없습니다 — 깊은 우물에서 `<exp(-βΔU)>` 가 터진 것입니다.
WaterClass 별 중앙값이 이를 그대로 보여 줍니다(log₁₀ w0): superweak −7.43 · weak −4.72 · strong −2.43 ·
superstrong −1.61 · strong_high_loading −1.02 · superstrong_high_loading +0.26 · **none +1.72**.
**원본은 이 행들을 거르지 않고 순위에 넣었습니다.** 상위 5 % 클리핑(D5)이 증상만 가립니다.
`screen_core.py` 에 `WIDOM_SANITY_MAX` 를 두되 **기본은 "표시만, 거르지 않음"** 입니다 — 문턱은 자료를 보기 전에 고를 수 없습니다.

## 6. 모양이 깨진 레코드 4건

    Widom == [None, None]                    2건   → `widom[0]/widom[1]` 이 TypeError → 맨 except 가 삼킴 → NaN
    Widom == [{id: val}, {id: val}]          2건   → 값이 한 겹 더 싸여 있음. 같은 경로로 NaN
    GEMC 가 list 가 아니라 str               409건  (ASR 기준)

D1(위치)과 D2(맨 except)가 **합작**하는 자리입니다. 정리본은 풀어 주거나 `Missing` 을 냅니다.

## 7. GEMC 는 물입니다 (CO₂ 아님)

    ASR 8,448건 전부 `_simltn_forcefield_adsorptive TIP4P` · `_simltn_forcefield_adsorbent UFF4MOF` · 298 K
    cutoff 9 Å · 5E3 + 1.5E4 + 2.5E4 사이클 · 단위 Molecules/Supercell
    `_simltn_code` 에 `GEMC_Incomplete` 가 섞여 있습니다 — **완주 여부를 안 보면 미완주 등온선을 쓰게 됩니다.**

우리 물 계산과 **다른 규약**입니다(우리: TIP5P-Ew 5자리 + `Hw none`/`Lw none`, UFF_MOF, 12 Å, 2×2×2, 5,000+15,000).
**두 계열의 물 값을 같은 축에 놓지 마십시오** — CLAUDE.md §2 "버전을 넘나들며 인용하지 마세요" 와 같은 이유입니다.

## 8. 우리에게 새로 생긴 것

1. **CR CIF 2,737개** (PACMAN-DDEC6 전하 포함, `CoREMOFDBSI_0613/SI/CR/*.cif`) — 갈래 (B) "다리 놓기" 를
   **내려받기 없이** 시작할 수 있습니다. 우리 프로토콜로 N 종을 다시 돌려 두 계열의 변환을 재는 일입니다.
2. **CoRE 축 3종의 생성 도구**: `CoREMOF.calculation.Zeopp` · `CoREMOF.mosaec`(산화수/안정성) · `MOFClassifier`.
   `env.yaml` 이 그대로 있어 갈래 (C) "관문 빌려 쓰기" 의 환경이 정의돼 있습니다.
   ⚠ Zeo++ 는 **RASPA 와 동시에 띄우지 마십시오**(§5, v3 구조 한 건 9.5 GB). 지금 `simulate` 8건이 돌고 있습니다.
3. **최종 115종의 정본 값** (`MOF_Project_Master_Data.pkl`) — 우리가 다시 만든 수치와 대조할 기준.

## 9. 안 한 것 / 열린 것

    · 압축을 풀지 않았습니다. 풀면 1.74 GB 이고 C: 여유가 43 G 입니다(§5 는 `df /mnt/c` 로 판정).
    · NCR(6,520 CIF)은 보지 않았습니다 — 계산 준비가 안 된(non-computation-ready) 쪽입니다.
    · `CoREMOF/models/` 1.31 GB 은 열지 않았습니다.
    · **Widom 순서** — §4 의 결정 시험을 아직 안 돌렸습니다.
    · `CR_meta_data_SI.json`(옛 판)과 `CR.json`(신 판)이 **같은 물질을 같은 값으로 담고 있는지** 대조 안 함.
      노트북 결과를 재현하려면 옛 판이 필요합니다 — 사용자가 이미 올린 파일 중에 있는지 확인이 필요합니다.
    · 이 문서는 판정문이 아니라 **개봉 기록**입니다. 이의 창 없음.
