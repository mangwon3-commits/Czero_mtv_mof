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

## 사용자 항목 (배정 아님 — 권고 첫 줄)
    E-7 DFT 물·CO₂ 결합에너지(J R3 2순위, 문턱 5 kJ/mol) — **어느 기기에도 DFT 코드 없음**(xtb 만). 권고: **E-3b 결과 뒤 결정** — R₂₉₈ < 0.67 이면 pyscf 설치(환경 변경, 데스크탑) 승인 요청; 아니면 보류.
    E-6 실험 한 줄(RH90·CO₂ 15 %·7 일 PXRD) — 시료: ZIF-69 모체 · 술폰화 ZIF-69 · MAF-66. srs 제외(자격 없음).
    MAF-66 활성화상 = 1t 인지 — ESI 의 활성화 PXRD 와 1t 시뮬레이션 PXRD 대조(사용자가 ESI 보유) [미확인].
    규약: §9-10 ②·④ 정의 · 가중치표/비대칭 존폐 · "ZIF" 범위 — 권고: 가중치 불곱·비대칭 유지 · "ZIF" = 순수 아졸레이트 + 아졸레이트-O 치환(N₃O 혼합 배위는 인접 후보로 표기).

## 일정
    결과 예상: laptop ~03:30 · Junseok E-3b ~03:00, E-2b ~04:30 · laptop2 ~07:00 · HKHOME E-9b ~04:00. **14:00 종합 갱신**(늦게 오는 것은 그 뒤 판으로).
