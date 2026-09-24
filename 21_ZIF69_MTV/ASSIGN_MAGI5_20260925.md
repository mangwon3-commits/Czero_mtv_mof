# 배정 — MAGI-005 권고안 실행 (2026-09-25 01:17, 데스크탑 종합자, HEAD b8293db5) — **사용자 승인 00:4x "일단 권고안대로 실행하고, 각각 로컬에 작업 할당"**

**등록 근거**: `MAGI/MAGI-005_selectivity-design.md` §6-5 등록안 E-1~E-9 · §7 권고안. 예측·기각 조건은 **각 자리의 R3 에 자료 0건 시점으로 이미 등록**돼 있으므로 이 문서는 배정이고 문턱을 새로 만들지 않습니다.
**대상 기기**: 랩탑(E-1) · Junseok(E-2) · laptop2(E-9 + E-4 준비) · HKHOME(E-8 + 관문 ⑤ 대기). **사용자·협력 랩**: E-3(MAF-66 CIF 입수) · E-6(실험 한 줄).
**규율**: CLAUDE.md §1 고정값(사이클·힘장 md5 8e8ec933·전하·Ewald·12 Å) · 머리말 관문(`ff_gate`) 착수 직후 확인 · 완주 표지(`Simulation finished`)로만 회수 · 결과는 `21_ZIF69_MTV/results_*.json`(postman 글롭 안) · 러너는 **공용 파일을 고치지 말고 사본으로**(러너가 도는 기기 없음 — `bgstate` 00:0x) · 견적은 출처 병기.

## E-1 (랩탑, Melchior) — P6′ 창 안 3D 강체 대조: 골격 전하 OFF Widom, 6작업 ≈ 1 h

    대상(ON 값은 이미 있음 — 다시 안 돌림)
      `core_pop_cifs/2010_Zn__pts_3_ASR_1.cif`   Zn pts 2010, **카복실레이트**([[J-8]]), S_ON 145.5 ± 4.7, LCD 4.00 / PLD 3.34, L 0.83
      `core_pop_cifs/2012_Co__dia_3_ASR_3.cif`   Co dia 2012, 이미다졸레이트형(N–N 0), S_ON 34.1 ± 0.6, LCD 4.27 / PLD 3.41
      `charged_v3/saIm050_DDEC6.cif`            우리 넓은 GME 대조, S_ON 65.2 ± 2.1 (results_v3)
    ★ 착수 전 관문(D-2 의 교훈 — 계산 0)
      Zn pts 2010 의 정체·상: `23_SCREENING/data/CR_meta_data_SI_slice.json` 에서 (연도 2010 · Zn · 원자 수 · LCD ± 0.1) 로 짝짓기 → DOI·MOFid. J R3 는 "2010년 후보 0" 이라 했으니
      30분 안에 안 닫히면 **그대로 돌리되 결과 행에 `identity: 미확인` 표지**. CIF 결합 분석(ase)으로 2D/3D·N–N·N–H 를 찍어 행에 기록.
    자   Widom CO₂·N₂, 초기화 3,000 + 15,000, 298 K, UFF_MOF, 12 Å, Ewald 1e-6, `unit_cells()` 규칙 — `run_core_pop.py` 의 프로토콜 그대로.
         **OFF = `UseChargesFromCIFFile no`(ChargeMethod Ewald 유지, 흡착질 전하 유지)** — `run_density_map.py:90` 의 q_off 규약과 동일(밀도맵 정전기 분율과 같은 자).
         공용 러너를 고치지 말고 `run_magi5_offwidom.py` 사본을 만들어 환경변수/옵션으로 `UseChargesFromCIFFile no` 를 쓰십시오. 머리말 관문(ff_gate) 통과 확인을 로그에.
    출력 `21_ZIF69_MTV/results_magi5_e1_offwidom_laptop.json` — 행마다 name · cif · charges('off') · KH_CO2 ± · KH_N2 ± · dU_CO2 ± · dU_N2 ± · S_OFF ± · (참조) S_ON ± · ln S_OFF / ln S_ON · identity · dim · status · seed · ff_md5.
    판정(M R3 P6′ 등록 그대로 — 결과 전 고정)
      Zn pts:   ln S_OFF ≥ 0.5 × ln S_ON  → "창 안 고선택도의 절반 이상이 비정전기(N₂ 입체 억제)"     기각: 절반 넘게 잃음 → D-4 읽기 기각
      saIm050:  ln S_OFF < 0.5 × ln S_ON  → "넓은 공동의 선택도는 절반 넘게 정전기"(M-2)
      Co dia:   서술 — 같은 창에서 145 와 34 를 가르는 것이 전하인지(OFF 뒤 가까워짐) 기하인지(OFF 뒤에도 갈림)
      판정 불가 띠 0.4~0.6 × ln S_ON(단일 실현·± 폭). **판정문은 종합자가 씁니다** — 랩탑은 결과 JSON + 한 줄 보고(값·표지)만.
    비용 6 Widom × ≈ 21.5 CPU·분(§AV 실측, CoRE 구조 — 옮긴 값) ÷ 8워커 → **≈ 1 h 벽시계**(범위 0.5~2 h, N_super 비례).

## E-2 (Junseok) — P8 base · nbIm100 의 N₂ Widom ΔU, 2작업(+검산 2)

    대상 `charged_v3/base_DDEC6.cif` · `charged_v3/nbIm100_DDEC6.cif`(= ZIF-78 조성). 전하 ON(정상). 자는 E-1 과 같음.
    할 것 N₂ Widom 에서 **⟨U⟩(dU_N2) ± 를 뽑는다**. `run_core_pop.py` 는 CO₂ 만 dU 를 저장합니다(`kc[2]`) — N₂ 쪽 parse 가 같은 값을 내는지 먼저 확인(`run_aryl_gcmc.parse`);
          내면 그 값을, 아니면 `run_widom_tnf.py` 형으로 N₂ 성분 Widom 을 돌려 출력에서 host–adsorbate 평균 에너지를 읽는다. 검산: K_H(N₂) 가 `results_v3.json` 의 값(base 2.9e-6 급)과 1.5 단위 안이어야 함 — 아니면 자가 다른 것.
    출력 `21_ZIF69_MTV/results_magi5_e2_n2du_junseok.json` — name · KH_N2 ± · dU_N2 ± · (참조) dU_CO2(= −(Q_st 보정 − RT), results_v3) · ΔΔU = dU_N2 − dU_CO2 · ff_md5 · seed · status.
    판정(M R3 P8 등록 그대로) ΔΔU ∈ [10, 15] kJ/mol → 273 K 헨리 선택도 = 298 K 의 1.45~1.74배(가정 제거). 밖이면 그대로 적고 A-3 환산 문장을 그 값으로 다시.
    비용 Widom 2~4건 ≈ 30~60분(§AV 옮긴 값; 이 기기 Widom 은 **미확인** — `MACHINE_CAPABILITIES §6`: 첫 건 실측이 곧 이 기기의 Widom 확인).
    부수(선택) 시간이 남으면 `2016[Co][pts]3[ASR]5`(Co(p-Me₂-bdp) 수축상) N₂·CO₂ Widom 을 **BlockPockets 없이/있이** 비교할 수 있는지 RASPA 입력을 검토만(계산은 사용자 결정 뒤 — 맹점 ① 의 자).

## E-9 + E-4 준비 (laptop2, Balthasar) — 계산 0 → 기하만

    E-9 srs Zn(pur)(OAc) 정체 — `10.1039/d3qi01092a`(Inorg. Chem. Front. 2023, HSTC-1) **본문·SI** 를 읽어:
        ① 활성화(용매 제거) 절차와 활성화상의 조성 — **아세테이트가 남는가**(전하 균형: Zn²⁺ + pur⁻ + OAc⁻) ② 상전이·유연성·PXRD 변화 ③ 물 안정성·물 등온·습도 자료
        ④ 기체 흡착 자료(CO₂·N₂ 있으면) ⑤ SI 구조 둘(공간군 2 대 9)이 같은 상인지 ⑥ 합성 조건(상용 시약 여부).
        산출 `21_ZIF69_MTV/E9_SRS_IDENTITY_20260925.md`(자기 가지 푸시 → 종합자 반입). 결론 한 줄: **관문 ⑤·T-J1′ 로 갈 자격이 있는가**(아세테이트 잔존 + 유연 보고 없음 = 있음).
        걸리면(아세테이트 소실·상전이 보고) 여기서 멈추고 서술만 — R3 의 순서 규칙 그대로.
    E-4 준비(사다리 앞단의 **위험 없는 앞부분만**; 이완·PACMAN 은 E-1 결과 뒤 — 권고 4)
        `00_Migration/raspa_share/raspa/structures/mofs/cif/` 의 비-RHO 11: ZIF-2 · -3 · -6 · -10 · -20 · -77 · -68 · -8 · -90 · -7 (+ 우리 base 는 있음) 에 대해
        ① `audit_external_cif.py --no-write` 류 감사(원소·고아·부분점유·게스트 잔재) ② 그래프 연결성 ③ Zeo++ `network -ha -res` LCD/PLD(v1 규모라 메모리 작음; RASPA 안 도는 동안만)
        산출 `21_ZIF69_MTV/E4_LADDER_GEOMETRY_20260925.md` + `e4_ladder_geometry.json`(name · file · 감사 결과 · LCD · PLD · 원자 수 · 비고). ZIF-7 은 "맹점 탐침" 표지.
    비용 읽기 1~2 h · 감사/Zeo++ 11구조 ≈ 1 h(v1 규모 Zeo++ 는 3.2 GB/건 — 08-19 실측; v3 급 9.5 GB 아님).

## E-8 (HKHOME, 종합자) — 자 보강 · 문서

    ① `core_pop_merged.json` 은 **.gitignore 규칙으로 미추적**(확인 2026-09-25 01:19) → 추적되는 병합·주석본 `core_pop_annotated.json` 을 만들어 열 추가: `dim`(키의 차원 숫자) · `series`(ASR/FSR 번호 제거) · `anion_removed`(같은 계열 ASR/FSR 조성 차: 원소 합 차이) · `L`(n(0.15)/(K_H·15 kPa), core_wc 조인) · `flexible`(문헌 표지, 지금은 Co(bdp) 계열만 `collapsed`)
    ② 상위 68(S ≥ 65.2)·48(S > 75.8)의 ASR/FSR 짝 조성 차 계수 → 맹점 ⑥ 의 크기
    ③ T-C4 문서 줄(CoRE ZIF-2 행 값, 두 척도, 이완 규범 차) · 관문 ⑤ 는 E-9 통과 시 srs 에 실행(데스크탑만)
    ④ 판정문: E-1·E-2 결과가 오면 `MAGI5_E1_VERDICT_…` · `MAGI5_E2_VERDICT_…`(등록된 문턱 그대로)

## 사용자·협력 랩 (기기 배정 아님)

    E-3  MAF-66 [Zn(atz)₂] CIF 입수 — Lin 2012 *Inorg. Chem.* 51, 9950 SI / CSD refcode. 입수 전 착수 불가(PLD ≥ 3.3 관문이 첫 단계).
    E-6  실험 한 줄 — 298 K · RH90 · CO₂ 15 % · 7일 → PXRD + 전후 0.15 bar 등온선(≥ 80 %). 시료: ZIF-69 모체 · 술폰화 ZIF-69 · MAF-66 · srs · (보류) Co(p-Me₂-bdp).
    안건  §9-10 ②·④ 정의 · 가중치표/비대칭 존폐 · E-7 문턱(5 kJ/mol 차 vs 2배) · "ZIF" 범위(순수 아졸레이트 / N₃O 포함)

## 끝나면

    각 기기: 결과 JSON(글롭 안) 또는 문서(가지 푸시) + `COMMS/<기기>.md` 한 줄(값·완주 표지·소요 시간 실측). 종합자가 판정문을 쓰고 이의 창을 엽니다.
    시한 없음(상한) — 끝나는 즉시. 기기가 비면 다음 등록 배정(`ASSIGN_DENSW_20260924.md` 잔여 등)으로 돌아갑니다.

### E-8 ①② 결과 (2026-09-25 01:20, HKHOME)
    ① `core_pop_annotated.json`(추적) — 열: dim · series · formula · n_015bar · L · flexible · asr_fsr_pair · anion_removed · asr_fsr_sel. `core_pop_merged.json` 은 `.gitignore:196` 규칙으로 미추적(E-8 ① 은 이 주석본으로 갈음).
    ② 같은 계열·같은 셀(6 파라미터 0.3 % 안)의 ASR/FSR 짝 **180** 중 조성이 다른 짝 **14**(ASR 이 배위 리간드/음이온을 지운 후보). 그중 상위 68(S ≥ 65.2)에 닿는 짝 **4**, 상위 48(S > 75.8) **3**:
       2024[Zn][srs]3 ASR1/FSR1 32.5/269.6 · ASR2/FSR2 30.0/333.8 (O8·C8·H12 제거 = 아세테이트, **10배**) · 2016[Co][sql]2 ASR17/FSR17 243.7/268.7 (H2·O1 = 물 1) · 2020[Cu][kgm]2 43.3/70.1 (H12·O6 = 물 6).
       → 맹점 ⑥ 의 크기: 상위군에서는 srs 한 계열이 결정적이고 나머지는 물 분자 차이(1.1~1.6배). 첫 휴리스틱(계열 안 원소 집합 차, 84행)은 링커가 다른 형제를 뒤섞어 **과대**였음 — 셀 일치로 좁힘.
