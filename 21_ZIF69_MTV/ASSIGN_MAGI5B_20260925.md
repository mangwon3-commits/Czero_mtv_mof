# ASSIGN MAGI-5B — 예약 계산 배정 (2026-09-25 02:03 HKHOME 종합자) · 시한: 오늘 14:00 종합 갱신

**권한**: 사용자 지시(2026-09-25 01:5x) *"Please decide the task assignments by 14:00 today and assign the scheduled reservation calculations"* → 종합자가 배정을 정하고 **보류돼 있던 계산(E-9b·E-3b·E-10·E-4 완결·E-2b)** 을 기기에 할당한다. 이 위임은 **배정**에 한하며, 규약 변경(§9-10 정의·가중치·비대칭·"ZIF" 범위)과 환경 변경(패키지 설치·`$RASPA_DIR` 수정)은 여전히 사용자 결정이다(CLAUDE.md §9 경계 ①②③ 그대로). 등록된 예측·문턱은 결과 전 고정.
**근거 결과**: `MAGI5_E2_VERDICT_20260925.md`(E-2 완주) · `MAGI5_E3_VERDICT_20260925.md`(MAF-66 S 15.5, 문턱 80.3 기각, 문헌 225 의 1/14.5) · E-1 중간(Zn pts OFF 비 0.68 · Co dia 1.06 · saIm050 대기) · E-9 개정(srs 자격 없음) · E-4 준비(비-RHO 10 기하).
**규율**: CLAUDE.md §1 고정값(md5 8e8ec933) · 파일·머리말 관문 · 완주 표지(`Simulation finished`)로만 회수 · 결과는 `21_ZIF69_MTV/results_*.json`(postman 글롭) · 공용 러너 무수정(사본) · 실행 뿌리는 (온도·압력)마다 새 폴더(§3) · 견적은 출처 병기 · 판정문은 종합자.

## 새 가설 E-3-F1 (E-1·E-3·CoRE 모집단에서 나옴 — E-10·E-4 가 시험)
> UFF_MOF + DDEC6 자에서 **순수 N 아졸레이트 3D 골격의 선택도는 기하 15~43 뿐이고 정전기 기여가 없다.** 그 위(140~334)는 **O 를 가진 골격**(카복실레이트·술포네이트·아세테이트·배위수)에서만 나오고 초과분은 정전기다.
> 근거: CoRE(우리 자) 3D·강체·PLD ≥ 3.3 에서 O/S/할로겐 없는 N 골격 35행 **최대 34.1**, O 골격 310행 상위 141~334 · E-1 Zn pts(카복실레이트) OFF 비 0.68 대 Co dia 1.06 · MAF-66 0.98 · 우리 saIm/nbIm 정전기 분율 43~68 %(M-2).

---
## Junseok — **E-3b** MAF-66 등온선 대조 (GCMC 4작업, 즉시) → **E-2b** Co(p-Me₂-bdp) BlockPockets S(r) (조건부)

### E-3b (T-J3′ 후속 — 문헌 225 대 우리 15.5 의 원인 가르기)
    대상  `charged_v3/maf66_DDEC6.cif`(master · 2×2×1 초격자 304원자 · 셀 20.408 × 20.408 × 13.100 · PACMAN DDEC6 · `unit_cells()` 규칙이 복제 결정). 전하 ON.
    작업  ① CO₂ 298 K · 1.0 bar  ② CO₂ 298 K · 0.15 bar  ③ CO₂ 273 K · 1.0 bar  ④ N₂ 298 K · 1.0 bar — GCMC 5,000 + 15,000, 자는 E-2 와 같음.
          드라이버: `run_magi5_srs273.py`(master 9664c333) 를 본떠 **전역 TEMP/PRESSURE/RUNS 만 덮는 사본** `magi5_e3b_junseok.py`. **뿌리는 (기체·T·P)마다** `magi5_e3b_runs_<gas>_<T>K_<P>bar/`.
    출력  `21_ZIF69_MTV/results_magi5_e3b_maf66_gcmc_junseok.json` — 행마다 gas · temp_K · pressure_bar · n_mmol_g ± · status(완주 표지) · seed · minutes · unit_cells · ff_md5. 우편함 한 줄(값·표지·소요).
    대조(등록, 초록 재확인 02:0x)  Lin 2012: CO₂ **19.4 wt% @298 K·1 atm = 4.41 mmol/g** · **27.6 wt% @273 K = 6.27 mmol/g**(wt%/44.01×10). 1 atm 대 1.0 bar 차 1.3 % 는 병기만.
    양    R₂₉₈ = n(298 K, 1 bar)/4.41 · R₂₇₃ = n(273 K, 1 bar)/6.27 · 함의 결합에너지 결손 ΔQ = −RT·ln R (보고만).
    예측(종합자, 결과 전)  **R₂₉₈ ∈ [0.4, 0.8]** — Widom K_H 5.2 mmol/g/bar·Q_st 24.5 kJ/mol(파일 22.0, 드라이버 결함 정정) 의 헨리 외삽(같은 계·같은 자, 포화 무시).
    판정  R₂₉₈ < 0.67 → 가설 (a) 힘장이 아미노·트리아졸 N 특이 상호작용을 못 봄 **또는** (c) 활성화상 ≠ CIF — 둘을 가르는 것은 ESI PXRD 대조(사용자 항목).
          0.67 ≤ R₂₉₈ ≤ 1.5 → 적재는 맞음 → 어긋남은 **N₂/헨리 추출 쪽**(가설 (b)) → ④ 의 N₂ 적재를 논문 그림의 N₂ 298 K 와 대조(`[그림 판독]`, laptop2 또는 사용자).
          R₂₉₈ > 1.5 → 과대(srs 형) → (c). RASPA ± 와 1 atm/bar 차를 합친 구간이 문턱을 품으면 **"경계"**.
    비용  4 GCMC ≈ **40~60 분 벽시계**(출처: §AW 랩탑 실측 20~40 분/건 — 다른 기기에서 옮긴 값; 이 기기 Widom 실측 24~27 분의 1.5~2배 추정).

### E-2b (조건부 — 우편함 01:54 ①~⑥ 의 답)
    0단계(계산 0)  RASPA 가 **실행 폴더(cwd)의 `<FrameworkName>.block`** 을 읽는지 시험: 임의 block 1점으로 Widom 짧게(100 사이클) 돌려 `.data` 에 `Pockets are blocked`·N>0 줄이 있는지.
          cwd 에서 읽으면 **환경 변경 없음 → 진행**. `$RASPA_DIR/share/raspa/structures/block/` 만 읽으면 **멈추고 보고**(환경 변경 = 사용자 결정).
    회수 관문  차단 실행마다 `.data` 의 `Pockets are blocked` 줄 + N>0 을 **필수**로(없으면 `no-block` 실패 — 조용한 실패 ① 을 표지로).
    대상  `core_pop_cifs/2016_Co__pts_3_ASR_5.cif`(CoRE "승자" S 113.4, PLD 3.57 — CO₂ 3.30 과 N₂ 3.64 사이). Zeo++ `network -block` 탐침 반경 **1.50 · 1.65(CO₂) · 1.82(N₂) · 2.00 Å** → 반경마다 CO₂·N₂ Widom(8작업) → **S(r) 곡선**. "정식" 짝은 CO₂@1.65 + N₂@1.82.
    예측(등록)  S_정식 ≥ 2 × 113.4 (PLD 가 두 지름 사이라 N₂ 만 주머니를 잃음) — 즉 CoRE 승자의 수는 **탐침 규약이 정한다**(맹점 ① 의 크기). 기각: S_정식 이 113.4 의 1.5 단위 안.
    출력  `results_magi5_e2b_blockpockets_junseok.json`(반경 · 차단 수 · K_H ± · S · 표지). 비용 ≈ 1 h(Zeo++ 소형 + Widom 8, 이 기기 실측 24~27 분/건 → 4워커 2회전).

---
## laptop (Melchior) — E-1 완주 뒤 **E-10** 전하 OFF 확장 (Widom 20작업, F1 시험)
    A 군(순수 N 아졸레이트형 3D, O/S/할로겐 없음 · ON 값은 `core_pop_annotated.json`)
        `2022_Cd__nuc_3_FSR_1`(33.4) · `2024_Zn__lig_3_ASR_1`(32.0) · `2024_Zn__srs_3_ASR_1`(32.5, ASR — 아세테이트 제거판, 정체 무관한 자 내부 시험) · `2020_Ag__pts_3_ASR_1`(26.5) · `2014_Cu__bcu_3_ASR_2`(18.4)  (+ 완료: Co dia 1.06 · MAF-66 0.98)
    B 군(O 를 가진 3D 상위)
        `2019_Zn__pcu_3_ASR_6`(141.1) · `2017_Zn__dia_3_FSR_1`(139.8, S₈O₁₆ 술포네이트형) · `2018_Cd__dia_3_ASR_5`(91.9) · `2019_Zn__pcu_3_ASR_1`(77.1, F₃₂) · `2021_Co__dia_3_ASR_1`(73.8)  (+ 완료: Zn pts 0.68)
    자    E-1 과 동일(`run_magi5_offwidom.py`, OFF = `UseChargesFromCIFFile no`). 출력 `results_magi5_e10_offwidom_laptop.json`(E-1 행 형식 + `set: A/B`).
    예측(등록)  ln S_OFF / ln S_ON 의 **A 군 중앙 ≥ 0.8 · B 군 중앙 ≤ 0.6**. 구조별 띠 0.6~0.8 은 판정 불가. 기각: B 중앙 ≥ 0.8(높은 S 도 기하 → F1 의 "O = 정전기" 절 붕괴) 또는 A 중앙 ≤ 0.6(아졸레이트에도 정전기 선택도 있음 → F1 붕괴).
    **[보완 2026-09-25 02:07, E-10 자료 0건 — E-1 완주(02:04) 뒤]** 주 지표를 **곱 G = S_ON/S_OFF** 로 둔다(E-1 실측: Zn pts 4.92 · saIm050 4.85 · Co dia 0.80 · MAF-66 1.06 — ln 비는 기하 바닥에 따라 압축되어 B 군을 0.62~0.68 로 띄운다). **등록: A 군 중앙 G ≤ 1.5 · B 군 중앙 G ≥ 3 · 띠 1.5~3.** 기각: B 중앙 G < 3 또는 A 중앙 G > 1.5. 위 ln 비 문턱은 부 지표로 병기(§9-6: 첫 결과 전 보완).
    비용  20 Widom × 17.5 분(E-1 같은 기기 실측) ÷ 8워커 ≈ **45~60 분**(같은 계 실측). E-1 결과 JSON 은 그대로 두고 새 파일.

---
## laptop2 (Balthasar) — **E-4 완결** 비-RHO ZIF 사다리 10종: 이완 → PACMAN → Zeo++ → Widom ON/OFF (F1 + 문헌 다리)
    대상  `e4_ladder_geometry.json` 의 10종(`00_Migration/raspa_share/raspa/structures/mofs/cif/`). 순서(창·PLD 통과 먼저): ZIF-77 → ZIF-90 → ZIF-8 → ZIF-68 → ZIF-2 → ZIF-3 → ZIF-6 → ZIF-10 → ZIF-20 → ZIF-7.
    앞단  ① ZIF-90 은 C–H 0.686 Å 결함을 **1.08 Å 로 정규화한 뒤** 이완 ② `relax_tnf.py` 형 GFN-FF 고정셀 이완(xtb; 단위셀 세그폴트면 MAF-66 선례대로 초격자) ③ `charge_tnf.py` PACMAN ④ Zeo++ `-res`(v1 규모 3.2 GB — RASPA 와 동시 금지) ⑤ `run_magi5_widom.py --cif charged_v3/<tag>_DDEC6.cif --tag <tag> --workers 6`(ON + 전하 0 사본 OFF, 298 K) — 파일명 `results_magi5_e3_<tag>_widom_<host>.json` 그대로 두어도 글롭 안.
    PLD 관문  ZIF-20(2.87)·ZIF-7(2.40)은 **관문 탈락**이지만 "맹점 탐침" 표지로 돌린다(닿지 않는 주머니가 Widom 을 부풀리는지 — E-2b 와 같은 물음).
    예측(등록)  (i) **문헌 다리**: Phan 2010 표 2 의 273 K 헨리 값(저장소 전문 인용)이 있는 구조(ZIF-68 등)에서 우리 298 K S ÷ (문헌 273 K ÷ 1.58[모체 인자, E-2]) ∈ **[1.2, 2.5]**(기능화 ZIF-77 은 2.06 으로 나눔). 밖이면 그대로 적음.
                (ii) **F1**: O 없는 ZIF(2·3·6·8·10·20·7) S_ON ≤ 43 · OFF 비 ≥ 0.8 ; O 있는 ZIF-77(nIm)·ZIF-90(ICA) OFF 비 ≤ 0.6 · S_ON > O 없는 군 중앙.
                (iii) 탐침 둘(20·7)은 문턱 없이 보고.
    출력  구조별 결과 JSON + `E4_LADDER_RESULT_20260925.md`(표: LCD/PLD 이완 전후 · S ON/OFF · 비 · 문헌 273 K · 환산 비). 우편함 한 줄씩.
    비용  이완 10 × 4~20 분(MAF-66 4.1 분/304원자 같은 도구 실측; GME 셀은 더 큼) + PACMAN + Zeo++ + Widom 40 × ~20 분 ÷ 6워커 ≈ 2.3 h → **≈ 4~5 h**(옮긴 값). 기기가 비면 다음 등록 배정 없음 → 종합자에 알림.

---
## HKHOME (종합자) — 관문 ⑤(MAF-66, 01:51~) → **E-9b**(srs FSR_1 273 K·15 kPa GCMC, `E9B_SRS273_REGISTRATION_20260925.md`; 사용자 위임으로 30분 규칙 대신 **위임 실행** 기록) → E-1 판정문(saIm050 도착 시) → E-3 §5 관문 ⑤ 추가 → Notion 갱신 → **14:00 §7 권고 개정**(E-3b·E-10 결과 반영).
    채택 규칙(E-8 제안)  **CoRE 후보를 올리기 전 원 논문 실측 등온선과 우리 적재를 대조한다**(srs 17배·MAF-66 1/14.5 — 양방향 사례). `COREPOP_REGISTRATION_20260921.md` 에 부록으로 적음(오늘).

---
## 추가 배정·후보 [2026-09-25 02:27]
    HKHOME  **E-2d**(273 K 직접 Widom base·nbIm100, Junseok 제안·예측 `MAGI5_E2_VERDICT §7`) — E-2c 뒤 사슬.
    후보 **E-11**(CIF 입수 조건, 사용자 항목): IISERP-MOF16 [Zn(Damtz)(HCOO)](Chem. Mater. 2026, 38, 7679 SI/CCDC) + CALF-20 [Zn₂(tz)₂(ox)] 를 우리 자(Widom ON/OFF + 0.15 bar + 물 Widom)로 — F1(아졸레이트 + O 음이온 → G ≈ 5?)과 E-6 물 축을 한 번에. 예측은 CIF 도착 뒤 자료 0건 시점에 등록.
    **맹점 ⑧ 등록**: 속도·체거름 선택도(구경 ≤ 3.3 Å) 는 Widom 이 못 봄 — MAF-66 문헌 225 의 정체(`MAGI5_E3_VERDICT §7`).

## laptop 2차 — **E-12 물 Widom**(E-10 완주 뒤, 2026-09-25 03:16 등록·자료 0건)
    자    v3w 물 프로토콜 그대로(`run_tb2_water_kh.py` 형 사본: TIP5P-Ew 5자리 `19_WaterCompetition/water.def`, **Hw/Lw none 힘장**(md5 8e8ec933), Widom, 298 K, `unit_cells()`, 전하 ON). 머리말 관문에서 물 5자리·Hw/Lw none 확인.
    대상  ① `charged_v3/maf66_DDEC6.cif`(master) 즉시 ② `charged_v3/calf20_DDEC6.cif` · `charged_v3/mof16_DDEC6.cif`(데스크탑 E-11 PACMAN 뒤 master 로 밀어 줌 — 도착하면).
    출력  `results_magi5_e12_waterkh_laptop.json` — name · KH_water ± · dU_water ± · Qst_rt_corrected · water_sites_in_rundir(=5) · ff_md5 · seed · status · minutes. 참조(v3w 실측, 데스크탑): base 7.13e-5 ± 0.89e-5 · nbIm100 1.30e-4 · saIm050 2.56e-4 ± 1.72e-4 · saIm100 4.08e-3 mol kg⁻¹ Pa⁻¹.
    예측(등록)  (a) MAF-66 K_H(H₂O) ≥ 3 × base(≥ 2.1e-4; 아미노·비배위 N 이 물 자리 — J R1 위험 항목). 기각: base 와 1.5 단위 안. (b) K_H(H₂O) **MOF16 < CALF-20**, 차 ≥ 1.5 단위(논문: MOF16 물 흡착 더 낮음). (c) CALF-20 물 Q_st(보정) ∈ **[35, 45]**(Nat. Commun. 2024 원자료 36~41). 물 경쟁 지수 K_H(H₂O)/K_H(CO₂) 를 base 와 나란히.
    비용  구조당 Widom 1건 ≈ 20~40 분(v3w 데스크탑 실측 — 옮긴 값). 판정은 종합자.

## Junseok 2차 [2026-09-25 04:56, 자료 0건] — **E-2e** 인자표 완성 + **E-4 Widom 뒷절반**
    E-2e  `charged_v3/fbIm100_DDEC6.cif` · `charged_v3/saIm050_DDEC6.cif` 의 N₂ Widom(+ CO₂ 검산), 자는 E-2 그대로(2×2×2, 전하 ON, 298 K). 출력 `results_magi5_e2e_n2du_junseok.json`(E-2c 행 형식).
          예측(등록): fbIm100 dU_N₂ ∈ [−12.5, −11.7](모체 괄호 안 — 플루오르는 N₂ 를 안 붙듦) · **saIm050 ∈ [−13.6, −12.6]**(saIm100 −14.34 와 base −12.46 의 중간 — −SO₃H 50 %). 기각: 밖으로 > 0.5 kJ/mol. 이로써 인자표 6점(base·brbIm100·fbIm100·nbIm100·saIm050·saIm100)이 전부 실측.
    E-4 Widom 뒷절반  데스크탑 앞단이 `charged_v3/e4zif<NN>_DDEC6.cif` 를 올리면 **Junseok 은 zif7 · zif20 · zif10 · zif6 · zif3**, laptop 은 zif77 · zif90 · zif8 · zif68 · zif2 (앞절반). 같은 드라이버·같은 인자(`run_magi5_widom.py --cif … --tag e4zif<NN> --workers 1 --temp 298`, 구조 병렬, 씨앗 감사). 출력 `results_magi5_e3_e4zif<NN>_widom_<host>.json`. 등록 예측은 §laptop2 그대로.
    비용  E-2e 4 Widom ≈ 30 분(E-2 실측) · E-4 5구조 × 4 ≈ 20 × 25 분 ÷ 6 ≈ 1.5 h.

## Junseok 3차 [2026-09-25 05:33, 자료 0건] — **E-13** MAF-66 273 K 직접 Widom (여유 워커, E-4 와 병행)
    대상  `charged_v3/maf66_DDEC6.cif`, CO₂·N₂ Widom **273 K** 전하 ON(2작업; `run_magi5_widom.py --tag maf66_273K --temp 273 --charges on --workers 1`). 출력 `results_magi5_e3_maf66_273K_widom_junseok.json`. **다른 시험**(온도).
    대조  Lin 2012 ESI 표 S3(273 K): K_H(CO₂) **25.72 / 26.82** · K_H(N₂) **0.0638 / 0.0648** mmol g⁻¹ atm⁻¹ · S 403/414. 우리 298 K: 5.22 / 0.336(E-3).
    예측(등록)  K_H(CO₂, 273)/K_H(CO₂, 298) ∈ **[1.8, 2.8]**(ΔU −22.0 의 반트호프 2.25; E-2d·E-11b 에서 외삽이 1.5 단위 안) → K_H(273) ≈ 9.4~14.6 → **실측의 0.35~0.55 배**(298 K 의 0.52 와 같은 급). N₂: 우리 K_H(N₂, 273) 실측의 **5~10 배 위**(298 K 의 7.7 배와 같은 급 — 체거름 읽기의 온도 불변성). 기각: CO₂ 비가 [1.8, 2.8] 밖, 또는 CO₂ 가 실측의 0.7 배 이상(자 과소가 온도 문제였음), 또는 N₂ 비가 3 배 아래(체거름 아닌 다른 원인).
    비용  2 Widom ≈ 25 분(이 기기 E-2 실측).

## 사용자 항목 (배정 아님 — 권고 첫 줄)
    E-7 DFT 물·CO₂ 결합에너지(J R3 2순위, 문턱 5 kJ/mol) — **어느 기기에도 DFT 코드 없음**(xtb 만). 권고: **E-3b 결과 뒤 결정** — R₂₉₈ < 0.67 이면 pyscf 설치(환경 변경, 데스크탑) 승인 요청; 아니면 보류.
    E-6 실험 한 줄(RH90·CO₂ 15 %·7 일 PXRD) — 시료: ZIF-69 모체 · 술폰화 ZIF-69 · MAF-66. srs 제외(자격 없음).
    MAF-66 활성화상 = 1t 인지 — ESI 의 활성화 PXRD 와 1t 시뮬레이션 PXRD 대조(사용자가 ESI 보유) [미확인].
    규약: §9-10 ②·④ 정의 · 가중치표/비대칭 존폐 · "ZIF" 범위 — 권고: 가중치 불곱·비대칭 유지 · "ZIF" = 순수 아졸레이트 + 아졸레이트-O 치환(N₃O 혼합 배위는 인접 후보로 표기).

## 일정
    결과 예상: laptop ~03:30 · Junseok E-3b ~03:00, E-2b ~04:30 · laptop2 ~07:00 · HKHOME E-9b ~04:00. **14:00 종합 갱신**(늦게 오는 것은 그 뒤 판으로).

## laptop2 2차 [2026-09-25 06:32, 자료 0건] — **E-11c** IISERP-MOF16 포메이트 **C12 정렬본** 모델 민감도 (`E11_CALF20_MOF16_REGISTRATION_20260925.md §6` 후속 (i), 종합자 결정 — 사용자 위임)
    왜    C11 정렬본의 **G = 0.22**(전하를 켜면 K_H(CO₂) 가 4배 준다)는 F1 과 정반대인데, 포메이트 C 3자리 무질서(C10 0.667 · C11/C12 0.333)를 C11 하나로 고른 **모델 결정**이 채널 안 전기장을 정한다. 이 G 가 정렬에 따라 바뀌는지 가른다.
    구조  `external_cif/IISERPMOF16_ZnDamtzHCOO_orderedC12_P1_2x2x2.cif`(데스크탑이 만들어 master 에 둠; 512원자). C11 판과 **같은 규칙**: C12 의 네 대칭상을 점유 1 로, 포메이트 H 는 C 에서 1.09 Å(O–C–O 이등분선 반대). 조성 Zn4 C12 H20 N20 O8(단위셀) — C11 판과 같음 · dmin 0.880(아민 N–H, C11 판과 같음). 이완 전 C–O 1.320/1.395 · O–C–O 102.7°(무질서 평균의 왜곡 — C11 판은 1.18/1.41 · 109.6°).
    절차  C11 판과 같은 도구·인자 — `E11` 사슬(`~/.claude_work/magi5_e11_chain.sh` 의 해당 줄):
          ① `RELAX_WORKERS=1 relax_tnf.py --job mof16c12=external_cif/IISERPMOF16_ZnDamtzHCOO_orderedC12_P1_2x2x2.cif`(spectra 환경 xtb, GFN-FF 고정셀)
          ② `coremof_tools/bin/python charge_tnf.py --tag mof16c12 --cif relax_tnf/mof16c12_relaxed.cif`
          ③ `run_magi5_widom.py --cif charged_v3/mof16c12_DDEC6.cif --tag mof16c12 --workers 4 --temp 298`(CO₂/N₂ × ON/OFF, **Q_st 결함 고친 드라이버 — master 판인지 확인**)
          ④ Zeo++ 는 **데스크탑**이 한다(laptop2 = Zeo++ 대량 불가, `MACHINE_CAPABILITIES.md`) — ② 뒤 `relax_tnf/mof16c12_relaxed.cif` 를 커밋하면 데스크탑이 `-ha -res`.
          ⚠ 태그는 반드시 `mof16c12` — `mof16` 을 쓰면 C11 판의 이완·전하본을 덮어씁니다.
    관문  이완 뒤 포메이트 C–O ∈ [1.2, 1.4] · O–C–O ∈ [115, 135]°(C11 판 이완 뒤 1.38/1.38 이 실측이라 상한을 1.4 로 둠) · Zn–O ≤ 2.3 · PACMAN 순전하 |Σq| < 1e-3. 밖이면 Widom 을 돌리지 말고 우편함.
    예측(등록, 자료 0건)  C11 판: S_ON 58.9 ± 11.3 · S_OFF 263 ± 11 · **G 0.22** · K_H(CO₂, ON) 1.49e-5 ± 0.28e-5.
          (i) **G(C12) ≤ 1** — 전기장 불리는 정렬이 아니라 아민·포메이트 배치 자체(F1 반례가 정렬에 강건). 기각: G(C12) ≥ 3(C11 의 0.22 는 정렬 인공물 → E-11 §6 의 G 는 폐기). 띠 1 < G < 3 은 "정렬 민감 — G 를 쓰지 않음".
          (ii) S_OFF(C12) 가 C11 판과 1.5 단위 안(OFF 는 기하만 — 포메이트 C 한 자리 이동으로 기하 바닥은 안 변함). 기각: 1.5 단위 밖 → 정렬이 기하까지 바꿈(PLD 2.59 통로에서는 가능 — 그대로 적음).
          (iii) S_ON(C12) 는 문턱 없이 보고(탐침 표지 PLD 2.59 그대로; 문헌 IAST 67).
    출력  `relax_tnf/mof16c12_relaxed.cif` · `charged_v3/mof16c12_DDEC6.cif` · `results_magi5_e3_mof16c12_widom_<host>.json` + 우편함 한 줄(관문 수치 포함). 판정은 종합자(E11 §8 로 덧붙임).
    비용  이완 ≈ 43 분(C11 판, 데스크탑 실측 198단계 — **다른 기기에서 옮긴 값**) + PACMAN 수 분 + Widom 4작업 ≈ 25 분(C11 판 데스크탑 4워커 실측, 옮긴 값; PLD 좁아 ± 19 % 였음) → **≈ 1.2~2 h**. 끝나면 다음 배정 없음 → 종합자에 알림.

## Junseok 4차 [2026-09-25 06:56, 자료 0건 — ZIF-68 298 K 결과 도착 전] — **E-4b** 탐침 규약 검사(BlockPockets) + ZIF-68 273 K 직접 Widom
    왜    E-4 의 PLD < 3.64 행(ZIF-7 2.37 · ZIF-8 3.28 · ZIF-90 3.47)은 E-2b 규칙 후보("`-block 1.82` 로 통로 유무 확인, 0 channel 이면 탐침 규약값 표지")의 첫 적용처이고, ZIF-7 S_ON 185.4 · K_H(CO₂) 4.0e-3(ZIF-2 의 73배)은 닿지 않는 공동이 Widom 을 부풀린 전형으로 보인다. ZIF-68 은 nIm 을 품어 E-4 (i) 문헌 다리의 온도 인자(등록 ÷1.58)가 1.58(모체)인지 2.06(nbIm100)인지 모호 — 직접 잰다.
    (a) Zeo++ `-ha -block r` (**표본 50,000** — E-2b ④ 의 25 GB 교훈; 동시 2건 상한) r = **1.65 · 1.82** × {`relax_tnf/e4zif7_relaxed.cif` · `e4zif8` · `e4zif90`} = 6건. 채널/주머니 수와 차단 구 수를 표로. 채널이 남는 경우만 그 .block 으로 CO₂@1.65 · N₂@1.82 Widom(전하 ON, 298 K, E-2b 드라이버·관문 그대로: stderr not-found 외 없음 + **N = 구 × 단위셀 수 정확 일치** + 표지).
          예측(등록): ZIF-7 은 두 반경 모두 **0 channel**(PLD/2 = 1.19) → S_ON 185.4 는 **탐침 규약값**. ZIF-8 은 1.65 에서 **0 channel**(PLD/2 = 1.642 < 1.65 — 경계, 5 mÅ 차라 표본 수에 민감하면 그대로 적음). ZIF-90 은 1.65 에서 channel ≥ 1 · 1.82 에서 **0 channel**(PLD/2 = 1.733) → E-2b 와 같은 "정식 짝 발산" 형. 기각: ZIF-7 이 어느 반경에서든 channel ≥ 1(우리 PLD 가 틀림 → e4_zeo_relaxed 재검).
    (b) ZIF-68 273 K 직접 Widom: `run_magi5_widom.py --cif charged_v3/e4zif68_DDEC6.cif --tag e4zif68_273K --workers 4 --temp 273`(ON·OFF 4작업, E-2d·E-13 과 같은 자). 출력 `results_magi5_e3_e4zif68_273K_widom_junseok.json`.
          예측(등록): 인자 f = S₂₇₃/S₂₉₈(같은 전하 ON) ∈ **[1.5, 2.1]**(모체 1.58 과 nbIm100 2.06 사이 — nIm 50 %). 기각: 밖. **E-4 (i) 판정은 등록대로 ÷1.58 로 내고**, 직접값은 "다른 시험" 으로 옆에 적는다(문헌 18.7 @ 273 K 과 직접 대조 — 등록 없음, 값 보고).
    순서  (b) 먼저(RASPA 4워커) → 끝난 뒤 (a) Zeo++(RASPA 와 동시 금지 — CLAUDE.md §5). 또는 (a) 먼저 — **동시만 피하면 순서는 Junseok 선택.**
    출력  `results_magi5_e4b_blockpockets_junseok.json`(E-2b 행 형식) · 위 273 K JSON · 우편함 한 줄씩. 판정은 종합자(`MAGI5_E4_VERDICT` 에 §로).
    비용  (b) ZIF-68 4800원자 × 4작업 — ZIF-7(4176원자) 298 K 81 분/작업 같은 기기 실측을 옮김 → 4워커 병렬 **≈ 1.5 h**(273 K 는 삽입 수용이 달라 ± 30 %). (a) 50,000 표본 × 6건 ≈ 300 s/건(E-2b ④ 같은 기기) → **≈ 20 분**. 합 ≈ 2 h.

## laptop 3차 [2026-09-25 07:16, 예측자 값 0건] — **E-10c** "자리 배치" 예측자: 접근면 전기장 (분석, RASPA 0)
    왜    E-4 판정 §3: n 24 에서 ρ(G, |q| 상위 10 %) 0.48(띠), 이미다졸레이트 사다리 안에서는 **음**(−0.62). 전하 **크기**가 아니라 CO₂ 가 닿는 면에서 전하가 **상쇄되는가**가 남은 가설(E-10b 읽기). CO₂ 사중극자는 장의 **기울기**와 짝하므로 접근면에서의 장 세기를 직접 잰다. laptop 은 이론·기제 자리(R1 T-M1 저자) — 가설 주인이 재는 것이 맞다.
    대상  `e10b_g_predictor_e4.json` 의 24점(MOF16 제외 그대로). 전하본은 전부 master(`charged_v3/` · E-10/E-1 CoRE 전하본 경로는 `e10b_g_predictor.json` 원판과 같은 곳).
    양(기계적, 전하 CIF + 기하만)  접근면 점 = 골격 원자 UFF σ/2 + 1.65 Å 구면 위에서 다른 원자와 겹치지 않는 점(원자당 ≥ 50점, 셀 주기 경계). 각 점에서 **Ewald 정전 퍼텐셜 φ 와 장 |E|**(골격 DDEC6 전하만, α·k 수렴 확인 — 두 설정에서 φ 차 < 1 %).
          **P6(주) = 접근면 rms |E|** · P7 = 접근면 σ_φ · P8 = P6 × (접근면 점 중 |E| 상위 10 % 평균)/(전체 평균)(국소 집중도). 구현 세부(점 밀도·Ewald 인자)는 **P6 를 G 와 맞추기 전에** 우편함에 적을 것.
    예측(등록, 예측자 값 0건)  **ρ(G, P6) ≥ 0.6 (n 24)** 그리고 **E-4 사다리만(n 9)에서도 ρ(G, P6) > 0**(P2 가 음이었던 자리에서 부호가 돌아와야 "상쇄" 가설이 산다). 부트스트랩 95 % 병기. 기각: n 24 에서 ρ(G, P6) < 0.4, 또는 사다리 안 ρ ≤ −0.3(장 세기로도 순위가 안 서면 → 남는 것은 CO₂ 자리의 기하 — 전하 모형 밖). 띠는 판정 불가. ZIF-77 · MAF-66 · Co dia ASR_1(큰 전하 · G ≈ 1 셋)은 **P6 가 하위 절반**이어야 한다(서술 예측, 셋 중 둘 이상).
    출력  `e10c_surface_field.py` · `e10c_surface_field.json`(구조별 P6~P8 · 점 수 · Ewald 수렴) + 우편함. 판정은 종합자(`E10B_G_PREDICTOR_20260925.md` 에 §로).
    비용  24구조 × 수천 점 × 최대 4800원자 Ewald(numpy) — 옮길 실측 없음, **추정 1~3 h(출처: 없음, 같은 계 실측 전)**. 30 분 안에 첫 구조 시간을 재서 우편함에 견적 갱신.

## laptop 4차 [2026-09-25 07:30, 예측자 값 0건] — **E-10d** 흡착 자리 가중 전기장 (분석, RASPA 0)
    왜    E-10c: 접근면 평균 장(P6)은 띠(0.45), ZIF-77 은 장이 강한데 G ≈ 1. 가설: G 를 정하는 것은 **LJ 가 CO₂ 를 붙드는 자리**의 장이지 면 평균이 아님.
    양    E-10c 의 적응 점(같은 스크립트·같은 점) 각각에서 **CO₂ O 자리 LJ 탐침 에너지** U_LJ(p)(UFF_MOF 혼합 규칙의 O_co2 × 골격, 12 Å 절단·꼬리 보정 없음 — 우리 자와 같은 절단). 가중 w = exp(−U_LJ/k_B·298 K).
          **P9(주) = √(Σ w|E|² / Σ w)** · P10 = P9/P6(자리 집중비). 구현 세부(탐침 원자 정의·겹침 점 처리)는 **G 와 맞추기 전에** 우편함에.
    예측(등록)  **ρ(G, P9) ≥ 0.6 (n 24)** 그리고 **ZIF-77 의 P9 순위가 P6 순위(21/24)보다 12 이상 내려감**(장이 자리에 없다 — ZIF-77 이 가설의 급소). 기각: ρ(G, P9) < 0.4 또는 ZIF-77 P9 순위 ≥ 16/24(자리 가중으로도 ZIF-77 을 못 설명 → 남는 것은 CO₂ 배향/사중극자 짝 — 점 탐침 모형 밖). 띠는 판정 불가. 부트스트랩 병기, 60점판 쓰지 않음(적응판만 — E-10c 에서 차 ≤ 0.03 확인).
    출력  `e10d_site_field.py` · `e10d_site_field.json` + 우편함. ρ 는 계산하지 말 것(판정 종합자 — E-10c 와 같은 분리).
    비용  E-10c 벽시계 4 분(같은 기기·같은 점 실측) + LJ 합 → **≈ 10~20 분**(LJ 는 Ewald 보다 싸다 — 옮긴 값 아님, 같은 스크립트 확장).

## laptop 5차 [2026-09-25 07:38] — **T-J1′** 이원 공동 지표 S_mix/S_Henry (Junseok R1 §T-J1′ + R3 J-13 대조 교체 — **등록된 지 오래, 미착수**; 예측·기각은 그 원문 그대로, 이 배정은 자·운영만 정함)
    대상 10  우리 5 `charged_v3/{base,nbIm100,saIm050,mslm050,sa50nb50}_DDEC6.cif` + CoRE 5 `core_pop_cifs/` — L < 0.2 셋 `2016_Co__sql_2_FSR_19`(2D) · `2024_Ni__sql_2_FSR_4`(2D) · `2017_Zn__dia_3_FSR_1`(3D, **주 대상**) + 대조 둘 `2012_Co__dia_3_ASR_3` · `2010_Zn__pts_3_ASR_1`(R3 J-13 교체판).
    자    이원 GCMC CO₂/N₂ = 0.15/0.85, 전압 1 bar, 298 K, 5,000+15,000, UFF_MOF(md5 8e8ec933), DDEC6, 12 Å, Ewald 1e-6, `unit_cells()`, 강체. S_mix = (N_CO₂/N_N₂)/(0.15/0.85). S_Henry = 같은 구조 E-10/E-1/우리 Widom 기존값(행에 출처 파일 기록).
    드라이버  `run_tj1_mix.py`(새로, `run_humid_wc.py` 의 MolFraction 블록 형 · 성분 2개). **§0 결함 방지 필수**: 이어받기·신규 둘 다 `'Simulation finished'` 표지 + 두 성분 적재 둘 다 있을 때만 ok(`run_aryl_gcmc.finished()` 와 같은 조건), `check=False` 금지 또는 반환코드 검사. **LPT = N_super 내림차순**, `submit`+`as_completed` 중간 저장.
    예측(원문)  L < 0.2 셋 S_mix/S_Henry **< 0.5**, 우리 다섯·대조 둘 **> 0.7**. 기각: L < 0.2 셋 **모두** ≥ 0.8 → J-13 철회. 2D 둘은 층간 틈 단서 표지(맹점 ③).
          종합자 병기(판정 아님): 2016_Co__sql_2_FSR_19 · 2010_Zn__pts_3_ASR_1 은 PLD 3.3~3.64(N₂ 탐침 통로 없음 — E-2b 규칙 후보 대상 18/68 중 둘)라 **S_Henry 자체가 탐침 규약값**. S_mix 는 GCMC 도 차단 없음이라 같은 맹점을 공유 — 비의 뜻이 우리 5와 다름을 판정문에 적는다.
    출력  `results_tj1_mix_laptop.json`(name · N_CO2 ± · N_N2 ± · S_mix ± (오차 전파) · S_Henry(출처) · 비 · L · dim · status · minutes · finished) + 우편함 착수·완주.
    비용  **옮긴 값**: 단일 성분 0.15 bar GCMC 1.5~20.2 h/작업(CLAUDE.md §5, v3 조성) — 이원·1 bar 는 흡착 분자 수가 늘어 더 길 수 있음. 벽시계 = max(최장 단일, 합/8) ≈ **15~25 h**(최장 단일이 묶을 공산 큼 — v3 GME 가 가장 무거움). 첫 2 h 진행률로 견적 갱신.
    **[보완 2026-09-25 07:41 — T-J1′ 자료 0건, Junseok 07:40 지적 수용(d5f3df77)]** 대조 둘(`2012_Co__dia_3_ASR_3` PLD 3.408 · `2010_Zn__pts_3_ASR_1` 3.339)이 **둘 다** PLD 3.3~3.64 띠 — "대조 > 0.7" 이 탐침 규약값끼리의 비가 된다. 원 대조는 그대로 두고 **깨끗한 대조 1행 추가**: `2019_Ni__pcu_3_ASR_1`(3D · PLD 3.69 · LCD 5.93 · S 44.4 · L 0.769 · 176원자 — `core_pop_annotated.json` 에서 3D·PLD ≥ 3.64·L > 0.7 중 S 최대). 예측은 원 대조와 같음(**> 0.7**). 기각 기계(L < 0.2 셋)는 불변. 대상 10 → 11.

## HKHOME 2차 [2026-09-25 07:53, 자료 0건 — 이 27조성의 OFF 값은 저장소에 없음] — **E-14** 우리 v3 조성의 G 지도 (전하 OFF Widom)
    왜    E-10b~d 결론: G 는 기술자로 안 선다 → **직접 잰다.** 설계 물음 그 자체 — 우리 치환기의 선택도 이득이 정전기(G)인가 기하 바닥(S_OFF)인가. 지금 G 가 있는 우리 조성은 saIm050(4.85, E-1) 하나.
    대상  results_v3.json 31 중 **관문 통과 + OFF 없음 = 27**(mslm075·saIm075·saIm100 관문 탈락 제외, saIm050 은 E-1 값 재사용). `charged_v3/<name>_DDEC6.cif`.
    자    `run_magi5_offwidom.py`(laptop E-1 러너 — 머리말 관문: 골격 전하 비영 0 · LJ 줄 · md5 · finished) 를 import 하는 `run_magi5_e14_offwidom.py`. S_ON 은 results_v3.json(같은 자 Widom, 행에 출처). G = S_ON/S_OFF.
    예측(등록)
      (1) base G ∈ **[1.8, 2.8]**(같은 gme 계 ZIF-68 2.40, E-4).
      (2) **기하 바닥 거의 불변**: S_OFF 가 base S_OFF 의 [0.67, 1.5] 배 안에 27 중 ≥ 2/3. 기각: 1/3 넘게 밖.
      (3) 그러므로 **ρ(G, S_ON) ≥ 0.8**(n 28 = 27 + saIm050; 이득은 정전기). 기각: ρ < 0.5(이득이 기하). 띠 판정 불가. 부트스트랩 병기.
      (4) 비극성 치환(brbIm·fbIm·mbIm 전 분율) G 가 base G 의 ±20 % 안(12 중 ≥ 10). 극성 순서(최고 분율 기준): saIm025 > nbIm100 ≥ mslm050 > cf3Im075 > cnbIm100 > base — 순위는 차 ≥ 1.5 단위(합성 ±)일 때만.
      (5) mbIm025 이상치(S_ON 30.4 대 mbIm050 19.7): 초과는 **기하**(S_OFF 가 mbIm050 보다 1.5 단위 이상 위, G 는 base ±20 %). 기각: G 가 초과를 설명.
    출력  `results_magi5_e14_offwidom_hkhome.json` · 판정 `MAGI5_E14_VERDICT_20260925.md`. §7 개정(14:00)에는 도착분까지로.
    비용  saIm050 OFF 40 분/작업(E-1 laptop 실측, 같은 계 v3 gme 4800원자 — **다른 기기에서 옮긴 값**) × 54 ÷ 8워커 ≈ **4.5 h**(묶는 쪽 = 작업합; 최장 단일 ≈ 40~60 분).

## Junseok 5차 [2026-09-25 08:06, 자료 0건] — ① 새 대조 `2019_Ni__pcu_3_ASR_1` `-ha -block 1.82` 1건(Junseok 제안) → ② **E-15** CoRE 열역학 상위군의 G (전하 OFF Widom)
    ①    예측(Junseok, 결과 전): PLD 3.69 → 1.82 에서 channel ≥ 1 · 구 0. 기각이면 T-J1′ 새 대조도 탐침 규약값 → laptop 에 알림(판정에 병기). 표본 50,000.
    ② 왜  E-10b~d: G 는 기술자로 안 선다 → 직접 잰다. CoRE 상위 68(S ≥ 65.2) 중 PLD ≥ 3.64(탐침 규약값 아님) **50행**, G 있는 4 제외 **46행**(3D 12 · 2D 34; anion_removed 1). 이들이 선택도를 정전기로 얻는가 기하로 얻는가 — §7 개정의 "그 위" 문장의 뜻을 정한다.
    자   `run_magi5_offwidom.py` + `run_magi5_e10_offwidom.py` 방식 래퍼(`run_magi5_e15_offwidom.py`, Junseok 작성; 대상 = core_pop_annotated 에서 S ≥ 65.2 · PLD ≥ 3.64 · E-1/E-10 OFF 없음). 머리말 관문(골격 전하 비영 0 · LJ · md5 · finished) 그대로. S_ON = core_pop_annotated 같은 자 값. LPT = N_super.
    예측(등록)
      (1) 3D 12 행 **G 중앙 ≥ 2**. 기각: < 1.5(열역학 상위 3D 도 이득이 기하).
      (2) ρ(G, S_ON) 46 행 ≥ 0.4(바닥이 CoRE 사이에서 달라 E-14 예측 0.8 보다 약함). 기각: ρ < 0. 부트스트랩 병기.
      (3) ASR/FSR 짝(같은 골격, anion_removed 없음)의 G 가 1.5 단위(합성 ±) 안 — 무료 재현 검사. 기각: 짝의 1/3 넘게 밖.
      (4) 서술: 2D 중앙 G 대 3D 중앙 G(맹점 ③ 층간 틈이 기하 몫이면 2D < 3D).
    출력 `results_magi5_e15_offwidom_junseok.json` + 우편함. 판정 종합자.
    비용 CoRE 소셀 OFF Widom ≈ 17.5 분/작업(E-1 CoRE 행, laptop 실측 — **다른 기기에서 옮긴 값**) × 92 ÷ 10워커(Junseok SMT 실측 6→10 +55 %) ≈ **2.7 h**. 최장 단일 ≈ 30~40 분(N_super 최대 행).
    **[① 결과 · Junseok 08:16 58630362]** 2019_Ni__pcu_3_ASR_1 `-block 1.82`: 2 channels · 1 pocket · 구 296(대부분 r 0.1, 최대 1.94, 셀 가운데, 부피 ≤ 셀 4 %) → 예측 "구 0" **기각**(Junseok 스스로). N₂ 통로는 있음 → **탐침 규약값 전부는 아님, 일부 오염.**
    **③ 추가 [2026-09-25 08:16, 자료 0건] — E-15 뒤(Zeo++ 라 RASPA 0 일 때)**: 같은 구조 `-block 1.65` + 정식 짝 차단 Widom(CO₂@1.65 · N₂@1.82, E-2b 드라이버·관문). **예측: S_정식 / S_ON(44.4) ∈ [1.0, 1.4]**(N₂ 만 잃는 작은 공동). 기각: > 1.4 → T-J1′ 새 대조도 오염 대조로 표지(판정에 병기, 원 대조와 같은 급). < 1.0 이면 CO₂ 도 그 공동에 앉던 것 — 그대로 적음. 견적 ≈ 7 + 15 분(Junseok).

## laptop2 3차 [2026-09-25 08:24, 자료 0건] — **E-14b** 설계 경계 두 조성의 G (Widom ON/OFF, 같은 실행)
    왜    E-14(데스크탑)는 results_v3 31 만 본다. 관문 통과 조성 중 **S 가 가장 높은 경계** 둘은 거기 없다: `sa50nb50`(risk_results_v3ens50nb50 pass, LCD 감소 9.9 %) · `saIm0583`(v3ensA·grid·sub 셋 다 pass, 15.5~15.7 %). saIm0625 부터는 관문 탈락(20.6~21.2 %). 두 경계가 G 로 선택도를 얻는지가 §7 설계 문장의 끝점.
    자    `run_magi5_widom.py --cif charged_v3/<n>_DDEC6.cif --tag e14b_<n> --workers 4 --temp 298`(ON·OFF 4작업/구조, Q_st 정정판 드라이버) × 2 = 8작업. 출력 `results_magi5_e3_e14b_<n>_widom_<host>.json`.
    예측(등록)  (1) **G(saIm0583) ≥ G(saIm050) = 4.85**(술포네이트 ↑ → 정전기 ↑; 차가 1.5 단위 안이면 "같음"). 기각: 1.5 단위 넘게 아래. (2) **G(sa50nb50) ∈ [3.5, 6]**(술포 50 % 가 G 를 정하고 니트로는 ≈ ZIF-68 급 2.4 를 얹지 못함 — 곱이 아님). 기각: > 6(곱셈형 합성). (3) S_ON 이 results_v3ens* 값과 1.5 단위 안(재현). 관문 표지는 행에 그대로(`status` 는 계산 표지 — CLAUDE.md §2).
    비용  E-11c 4작업 42 분(같은 기기·4워커) 이지만 v3 gme 4800원자는 MOF16 512 보다 무거움 — saIm050 OFF 40 분/작업(laptop E-1, 옮긴 값) × 8 ÷ 4 ≈ **1.5 h**.

## laptop2 4차 [2026-09-25 10:21, 자료 0건 — 이 10 실현의 OFF 값 없음] — **E-14c** 배치 산포 속 G: sa50nb50 대 saIm050 (앙상블 각 5)
    왜    E-14b: sa50nb50 G 5.87 대 saIm050 4.85 — 실현 하나씩. 앙상블 S_ON 산포(52~88)가 커서 차가 조성인지 배치인지 못 가름. "술포 + 니트로 조합이 술포 단독보다 G 를 올린다" 가 §7 설계 문장의 핵심이라 배치 단위로 잰다.
    대상  `charged_v3/sa50nb50e{1..5}_DDEC6.cif` · `charged_v3/saIm050e{1..5}_DDEC6.cif` — 10 전부 관문 pass(risk_results_v3ens50nb50 · v3ens0500). S_ON = `results_v3ens_mix10.json` 같은 이름 행(같은 자 Widom, 행에 출처). 실현 0(원판)은 E-14b·E-1 값으로 더해 각 n = 6.
    자    전하 OFF Widom — `run_magi5_offwidom.py` import 래퍼 `run_magi5_e14c_offwidom.py`(E-10/E-15 방식, 머리말 관문 그대로). 20작업.
    예측(등록)  (1) **배치 평균 G(sa50nb50) − G(saIm050) ≥ 1.5 배치 단위**(분모 = 두 군 실현 SD 의 합성, CLAUDE.md §2 · RULER_DECISION §7) — 니트로가 G 를 올림. **± 자 단위도 병기**. 기각: < 1.5 배치 단위 → "조합의 G 이득은 배치 산포 안".
                (2) G 의 실현 간 변동계수(SD/평균)가 S_ON 의 변동계수보다 작다(두 군 모두) — G 가 S 보다 배치에 둔감. 기각: 한 군이라도 G CV ≥ S_ON CV.
    출력  `results_magi5_e14c_offwidom_<host>.json` + 우편함. 판정 종합자(`MAGI5_E14_VERDICT §E-14c`).
    비용  laptop2 E-14b 실측 56 분/구조(4작업 · 4워커 — **같은 기기·같은 계**) → 작업당 ≈ 56 분 × 20 ÷ 6워커(물리 6) ≈ **3.1 h**(작업합이 묶음; 최장 단일 ≈ 1 h).

## Junseok 6차 [2026-09-25 10:49, 자료 0건 — 재실행 값 없음] — **E-15b** 이상치 `2017_Cd__hcb_2_ASR_1`(G 15.7) 재현 + 정체 (③ Ni pcu 뒤)
    왜    E-15 에서 한 행만 G 15.7 ± 3.1(나머지 46행 최대 4.97). ON 값은 core_pop 옛 실행 하나(K_H(CO₂) 1.07e-3 — ZIF-7 탐침급), 조성 Cd₂H₅₀C₆₂O₁₂(N 0), 짝 FSR 없음(FSR_1 은 ASR_2 의 짝 — 다른 조성). CLAUDE.md §0 "좋은 결과는 기준을 의심".
    ①    `run_magi5_widom.py --cif core_pop_cifs/2017_Cd__hcb_2_ASR_1.cif --tag e15b_cdhcb --workers 4 --temp 298`(ON·OFF 같은 실행, 새 씨앗). 출력 `results_magi5_e3_e15b_cdhcb_widom_junseok.json`.
    ②    정체(계산 0, Junseok 자리 = 자료 역설계): CoRE 메타 슬라이스로 DOI·원 조성·용매/음이온 처리 확인(laptop E-1 의 identity_note 방식). `-ha -res` 로 PLD/LCD 재확인(Zeo++ 1건, RASPA 0 일 때).
    예측(등록)  (1) S_ON 이 224.0 과 1.5 단위 안 · G 가 15.7 과 1.5 단위 안(값은 우리 자에서 실재). 기각: 어느 쪽이든 밖 → 옛 값은 씨앗/실행 인공물, E-15 표에서 이 행 교체.
                (2) 정체는 **결과 전 예측 없음**(서술) — 다만 N 0 · 높은 K_H 는 "음이온/리간드 일부 삭제된 ASR" 을 의심케 함(맹점 ⑥ 계열); 확인되면 E-15 에서 표지.
    비용  4 Widom × CoRE 소셀 ≈ 20~40 분(E-15 같은 기기 실측 평균 146.9 분 × 10워커 ÷ 92작업 ≈ 16 분/작업 — **같은 기기·같은 계**) + 정체 확인 ≈ 30 분.
    **[③ 결과·판정 2026-09-25 11:00 — Junseok c7e49f1a · 표지 2/2 · N 2368/2368]** Zeo++ 1.65: 1 channel · 0 pocket(CO₂ 는 가운데 공동까지 닿음) / 1.82: 2 channel · 1 pocket · 구 296. CO₂@1.65 K_H = 차단 없음의 0.9997(0.03 단위) · N₂@1.82 K_H = 차단 없음의 0.943(−5.7 %, 6.9 단위). **S_정식 47.06 ± 0.46 · S/S_ON = 1.060 ± 0.017 ∈ [1.0, 1.4] → 성립.** T-J1′ 새 대조 `2019_Ni__pcu_3_ASR_1` 은 **"깨끗한 대조(N₂ 쪽 공동 몫 5.7 %)"** 로 판정문에 표지. 원 대조 둘(PLD 3.3~3.64)은 "탐침 규약값 대조" 표지 그대로.

## Junseok 7차 [2026-09-25 11:10, 자료 0건] — **E-16** 설계 표본 `2017_Zn__dia_3_ASR_1`/`FSR_1` 정체 + 물 (E-15 §2 — 46행 중 3D 로 "바닥 × G" 를 함께 가진 유일 행)
    왜    E-15: 우리보다 높은 길 = G ≈ 5 를 지키며 기하 바닥 ×2.5. 3D 로 그 둘을 함께 가진 행은 `2017_Zn__dia_3_ASR_1`(S_OFF 41.6 · G 3.30 · PLD 3.81 · L 0.139 · Zn₄H₇₂C₈₈S₈N₁₆O₁₆ — 술포 계열) 하나. FSR_1 은 T-J1′ 주 대상(laptop 진행 중). 이것이 실재 물질의 성질인지 먼저 확인한다(E-15b 의 교훈 — CoRE 처리 인공물 가능).
    ①    정체(계산 0): CoRE 메타로 DOI · 원 조성 · ASR/FSR 처리 · **골격 형식 전하 산수**(E-15b 방식 — 짝이온 삭제 여부) · 원 논문의 CO₂ 등온선이 있으면 우리 적재와 대조(E-8 규칙, 같은 온도 없으면 방향만).
    ②    물(조건부): v3w 프로토콜 물 Widom 1건(`run_tb2_water_kh.py` 형, TIP5P-Ew 5자리, Hw/Lw none, 298 K) — **착수 전 머리말 관문 필수**: RASPA 가 인쇄한 Hw–Hw·Ow–Hw LJ 가 none(0)인가. **관문 실패면 멈추고 우편함**(힘장 수정은 환경 변경 — CLAUDE.md §9 경계 ①, 사용자 결정). 참조: saIm050 K_H(H₂O) 2.56e-4 · K_H(CO₂) 1.76e-4(지수 1.46).
    예측(등록)  ① 서술(결과 전 예측 없음) — 다만 **형식 전하 ≠ 0 이면 E-15 §2 의 "유일 3D 표본" 문장 철회**. ② 물 경쟁 지수 K_H(H₂O)/K_H(CO₂) **≥ saIm050 의 1.46**(좁은 술포 공동은 물을 더 붙듦). 기각: 1.5 단위(합성 ±) 넘게 아래 → "좁은 술포 3D 는 물에 덜 취약" (설계에 유리한 반례).
    출력  우편함 + `results_magi5_e16_zndia_water_junseok.json`(② 한 경우). 판정 종합자(E-15 판정문 §4).
    비용  ① ≈ 30 분 · ② 물 Widom 1건 ≈ 20~60 분(Junseok 물 러너 RH0 1작업 58.5~59.8 분 실측은 GCMC — Widom 은 더 짧을 것, **옮긴 값 아님, 추정**).
    **[보완 2026-09-25 11:16 — E-16 ② 자료 0건(11:14 착수, 결과 미도착) · Junseok 11:15 지적 수용(67ffa719)]**
      ⓐ **정정**: 위 "술포 계열" 은 종합자 오기 — S₈ 은 티오펜 고리 S, O₁₆ 은 카복실레이트(10.1021/acsami.6b11797, Zn(bib)(bdtdc), 형식 전하 0). 예측 ② 의 근거 문장("좁은 **술포** 공동은 물을 더 붙듦")도 전제가 틀림 → 예측 방향은 유지하되 근거를 "열린 Zn(has_OMS)·카복실레이트 O 가 좁은 공동에 노출" 로 바꿔 적음(방향 불변).
      ⓑ **판별력 보완**: 참조 saIm050 물 K_H 가 한 씨앗 ± 67 % 라 기각이 어떤 결과로도 불가능(판별력 0). 참조를 **같은 구조 4씨앗 평균**으로 교체 — `v3w_water_kh/…seedfixed` 1 + `v3w_water_kh_ours` 3 = 2.354e-4, 평균의 ± = ±̄/√4 = 4.92e-5(21 %; 씨앗 간 SD 8 %). 참조 지수 = 2.354e-4 / 1.757e-4 = **1.34 ± 0.28**. 판정 식 = 평균 대 단일(RULER_DECISION §7 187줄 계열): 단위 = d / √(±_ref² + ±_new²).
      **등록(교체)**: 새 지수 ≥ 1.34 − 1.5 단위 안(= "같거나 위") → 성립. **1.5 단위 넘게 아래 → 기각**("좁은 3D 카복실레이트는 물에 덜 취약"). 1.5 단위 넘게 위 → 성립(강한 형).

## Junseok 8차 [2026-09-25 11:27, 자료 0건 — 이 11행의 물 K_H 없음] — **E-17** CoRE 3D 열역학 상위 12행의 물: 정전기 이득(G)은 물 벌점을 같이 가져오는가
    왜    E-16: 유일 3D 표본의 물 지수가 saIm050 의 1/19. 이것이 그 행만의 일인지, "CO₂ 를 세게 붙드는 3D 골격" 의 일반 성질인지 — 설계 교환(G ↔ 물)의 모양을 정한다.
    대상  E-15 의 3D 12행 중 E-16 을 뺀 **11행**(core_pop_cifs; ASR/FSR 짝 포함 — 짝은 재현 검사로 겸함). 행마다 CoRE 메타 **has_OMS** 표지를 붙인다(맹점 ⑨ 확장 — 열린 금속).
    자    E-16 과 같음(v3w 물 Widom, 머리말 관문 착수 전·후). 출력 `results_magi5_e17_core3d_water_junseok.json`(행: K_H(H₂O) ± · K_H(CO₂) ON(annotated) · 지수 · G(E-15) · S_OFF · has_OMS · 관문).
    예측(등록)  (1) **ρ(K_H(H₂O), G) ≥ 0.5**(12행 = 11 + E-16; 정전기 자리가 물도 붙듦 — 교환이 있다). 기각: ρ < 0(G 가 높은 골격이 물을 덜 붙듦 — 교환 없음, 설계에 유리). 띠 판정 불가. 부트스트랩 병기.
                (2) 지수 K_H(H₂O)/K_H(CO₂) 12행 중앙 ≤ saIm050 참조 1.34(CoRE 3D 상위는 CO₂ 를 더 세게 붙들어 지수가 낮다). 기각: 중앙 > 1.34.
                (3) 짝(ASR/FSR) K_H(H₂O) 1.5 단위 안(재현).
    비용  E-16 10.3 분/건(같은 기기·같은 규약 실측) × 11 ÷ 동시 6 ≈ **25~40 분**.

## 사용자 결정 뒤 배정 [2026-09-25 12:02 — `MAGI5_USER_DECISIONS_20260925.md`]
### HKHOME 3차 — **E-18** 셀 자유 이완 도구(유연 골격) — E-14 뒤, RASPA 0 일 때 (자료 0건)
    도구  관문 ⑤ 의 LAMMPS UFF4MOF box/relax 경로(`risk_screen.py`, lammps-interface 패치판)를 **구조 산출용**으로 재사용 — 새 이완 코드 없음. 바깥 루프 상한 12 대신 **수렴(EDiff < 1e-4 kcal/mol) 또는 상한 50** · 산출 셀·좌표를 CIF 로.
    검증 관문(먼저)  CALF-20(`external_cif/CALF20_Zn2tz2ox_guestfree_P1.cif`) 이완 셀이 실험 셀(CCDC 2084733) 대비 **a·b·c 각 ≤ 3 % · 부피 ≤ 5 %**. 밖이면 도구 불합격 — 여기서 멈추고 기록(UFF4MOF 가 이 골격을 못 잡음).
    그다음(합격 시)  MOF16 C11·C12 두 정렬 셀 자유 이완 → Zeo++ PLD/LCD → PACMAN → Widom ON/OFF. 예측(등록): **C11·C12 의 G 가 셀 자유 이완 뒤 서로 1.5 단위 안으로 모인다**(고정셀의 정렬 민감도는 셀 구속 때문). 기각: 여전히 1.5 단위 밖. PLD 는 서술(논문 NLDFT 5.2 Å 쪽으로 가는지).
    비용  관문 ⑤ MAF-66 18 분(2432원자, 상한 12 — 같은 기기) → CALF-20 352원자 수 분 · MOF16 512원자 ×2 ≈ 30~60 분 + Widom 8작업 ≈ 1 h.
### HKHOME 4차 — **E-7** DFT 물 결합 오차(pyscf, 설치 확인 뒤 · E-18 과 코어 나눔) — 설계 등록은 설치 확인 뒤 별도 문서(`E7_DFT_WATER_REGISTRATION_20260925.md`, 자료 0건 시점). 자리: −SO₃H O · 트리아졸 N · NH₂ · −NO₂ O · Zn–카복실레이트 · **열린 Zn(E-16 추가)**. 양 ΔE_err = E_DFT − E_UFF_MOF/TIP5P(같은 클러스터 기하). 문턱은 두 판(5 kJ/mol 차 · 2배) 병기, 판정 문턱은 사용자 7번 결정 뒤.
### Junseok 9차 — **E-8c** 상위 68 행의 `formal_charge_nonzero` 채우기(E-17 뒤, 계산 0) — E-15b/E-16 방식(CoRE 메타 DOI · 링커 형식 전하 산수). 18 행 probe_convention 과 겹치는 것 포함. 출력 `core_pop_formal_charge_junseok.json`(name · 값 · 근거 · DOI) → 종합자가 annotated 에 병합. 예측(서술 외 하나): **상위 68 중 True ≥ 3 행**(이미 확인 3 — 더 나오면 모집단 문장에 병기). 기각 없음(계수).
    **[E-8c 결과 2026-09-25 12:13 — Junseok 40d6689d]** 상위 68: True 3(Cd hcb ASR_1 · **Zn pts 2010 ASR_1·FSR_1 — 새로**) · False 64 · None 1(2017_Cd__kgd_2_FSR_1, O²⁻/OH⁻/물 구별 불가). 등록 "True ≥ 3" → **3, 성립(계수)**. annotated 병합(확인 6행과 충돌 0). 파급: E-1 Zn pts 제외 · E-10 A 절 조인 판 → 두 판정문에 정정 블록.

## Junseok 10차 [2026-09-25 12:29, 자료 0건 — 새 씨앗 값 없음] — **E-19** 우리 경계 조성의 물 경쟁 지수 다씨앗 확인 (사용자 지시 "유휴 로컬 파악해서 계산 분담")
    왜    E-14 §1-3: 우리 조성에선 G 가 물을 끌고 오지 않는다(ρ 0.07) — 그러나 물 K_H 는 한 씨앗 판. 설계 문장을 가르는 두 조성: **mslm050**(G 4.69 · 지수 0.685 ± 0.11 — saIm050 의 절반) · **sa50nb50**(G 5.87 최고 · 지수 2.55 ± 1.1 — 가장 나쁠 수 있음).
    대상  `charged_v3/{mslm050,sa50nb50,nbIm100,nbIm050}_DDEC6.cif` × **새 씨앗 3** = 12작업(기존 seedfixed 1 과 합쳐 각 4씨앗 — saIm050 · base 는 이미 4씨앗).
    자    E-16/E-17 과 같은 v3w 물 Widom(TIP5P-Ew 5자리 · Hw/Lw none · 298 K · 착수 전·후 머리말 관문). 지수 = K_H(H₂O) 4씨앗 평균 / K_H(CO₂)(results_v3; sa50nb50 은 E-14b ON 1.872e-4). 평균의 ± = ±̄/√4. 단위 = d/√(±₁² + ±₂²)(RULER_DECISION 187줄).
    예측(등록)  (1) **지수(mslm050) 가 saIm050 참조 1.34 ± 0.28 보다 1.5 단위 넘게 낮다**. 기각: 1.5 단위 안 → "mslm050 의 물 이점은 씨앗 잡음".
                (2) **지수(sa50nb50) 가 saIm050 보다 1.5 단위 넘게 낮지 않다**(니트로 조합의 G 이득은 물 벌점을 같이 가져온다). 기각: 1.5 단위 넘게 낮음 → 조합이 G·물 둘 다 유리.
                (3) 서술: 6조성(4씨앗 평균) ρ(K_H(H₂O), G).
    출력  `results_magi5_e19_water_seeds_junseok.json` + 우편함. 판정 종합자(`MAGI5_E14_VERDICT §E-19`).
    비용  v3 gme 4800원자 물 Widom — Junseok 기기 실측 없음(E-16/17 은 CoRE 소셀 10 분/건). **첫 작업 시간을 재서 30 분 안에 견적 우편함**. 추정 1~3 h(출처: 없음).
