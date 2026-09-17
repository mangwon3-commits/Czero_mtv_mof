# 🔴 결함 — Widom Q_st 의 RT 부호 오류: 저장소의 모든 Q_st 가 2RT = 4.955 kJ/mol 낮다 (2026-09-11 06:22, 종합자; 발견 랩탑 Melchior T-NF-0q ①)

**한 줄**: 러너가 `Q_st = −ΔU − RT` 로 계산했다. RASPA 정의(`dH = <U_gh>−<U_h> − <U_g> − RT`, `Q = −H`)로는 강체 분자에서 **`Q_st = −ΔU + RT`** 다.
차이 = 2RT = 4.9554 kJ/mol(298.15 K). **부호 오류이고 상수 오프셋**이다. CLAUDE.md §0 의 유형("실패가 결과처럼 보이는 것") — 조성 간 차이 검사를 전부 통과하고, base 22.42 가 문헌 ZIF CO₂ Q_st 대역(20~30)에 그럴듯하게 앉아 절대값 감각으로도 안 걸렸다.

## 1. 증명 (Melchior, T-NF-0k Widom 출력)
    출력 줄   `[water] Average <U_gh>_1-<U_h>_0:  -1440.5051902517 [K]  ( -11.9770298700 kJ/mol)`
    검산      −1440.505 K × R = −11.9770 kJ/mol = 괄호값 → **괄호는 ΔU 의 단위환산**(dH 였다면 −14.4547)
    dH        −11.9770 − 2.4777 = −14.4547 (발열, 음수) → **Q_st = +14.4547**
    저장소 식 −u − RT = 11.9770 − 2.4777 = **9.4993** → 차 **4.9554 = 2RT**
    파서      `'<U_gh>_1-<U_h>_0:' in line` → 괄호 첫 수(음부호 포함) = u = ΔU. 읽기 확정.
    미확인    같은 파일 안 독립 대조(GCMC `Enthalpy of adsorption` 절)는 Widom 전용 실행에서 −nan 이라 불가. (1) 의 산술만으로 결론은 선다.

## 2. 범위 (종합자 grep, 06:22)
    러너 **10곳**(종합자 9 + Melchior 산출물 기준 재훑기 06:24: `rg.R_GAS*rg.TEMP` 모듈한정 호출이 상수 표현식 grep 에 안 잡혔음)
      kc[2] 계열  21_ZIF69_MTV/run_aryl_gcmc.py:278 · run_gcmc_v2.py:129 · run_gcmc_v3.py:163 · run_candidate_gcmc.py:64(→ candidate_results.json) · charge_and_run.py:234
      kc[1] 계열  13_PACMAN/run_raspa_ddec6.py:140 · 14_Strategies/run_raspa_strat.py:140 · 14_Strategies/oms_sensitivity.py:150(u) · 17_NestEffect/run_raspa_nest.py:140 · 18_PoreNarrowing/charge_and_run.py:212
      u_c/u_n     07_Bracketed_MTV/run_widom_batch.py:141,142(**CO₂·N₂**)
      ⚠ 튜플 첨자가 계열마다 다름(kc[2]/kc[1]/u) — **일괄 치환 금지**, 줄마다 손으로.
    러너 아닌 곳 셋(코드만 고치면 안 따라옴)
      ① 07_Bracketed_MTV/run_widom_batch.py:140 주석 `# Qst = -(U_gh - U_h) - RT` — **틀린 식을 명시한 주석**(오타가 아니라 개념 오류의 증거). 같이 고칠 것.
      ② 21_ZIF69_MTV/regen_energy.py:64 하드코딩 `QST = {'base': 21.08, 'saIm050': 25.17, 'saIm075': 26.63}` — 재생에너지는 Q_st 절대값에 직접 걸림. **이 수는 results_v3.json(22.42/28.51)과 다르므로 출처(v2?) 확인 뒤** 2RT 를 더할지 판단.
      ③ 20_ParentScan/cavity_model.py:137 `예상 Qst = 14.04 × 증폭비 + 9.84` — 계수가 틀린 Q_st 에 맞춰졌다면 Q_st 를 고치는 순간 모형이 어긋남. **"JSON 에 상수 더하기" 로 안 끝나는 지점.**
    결과 JSON   `Qst_CO2` 보유 **20개**(results_v3·v3grid·v3cliff·v3ens0583/075/nb050·v3pctl·v4mix·aryl_results·candidate_results·zif69_results·v3_smoke 등)
    문서        Q_st/지렛대 언급 md **52개**, 절대값 인용 줄 **33**(22.42·28.51·29.51·31.07·지렛대 배수·TSA/VSA)
    하류        `tsa_vsa_lever.py:137` `lev = exp(Q_st/R·(1/298−1/373))` — Q_st 가 지수 안 → 공통 배수 **1.495**: base 지렛대 6.2→9.2, saIm050 10.1→15.1; TSA/VSA 절대 배수 base 2.1→3.1, saIm050 3.4→5.0.

## 3. 바뀌는 것 / 안 바뀌는 것
    불변   조성 간 Q_st **차**(치환 축 대 모체 배치 단위 등 모든 차 기반 판정) · 순위 · K_H · 선택도 · 로딩 · 지렛대의 조성 간 **비** · "TSA 지렛대는 Q_st 와 함께 커지고 VSA 는 고정" 논지의 모양
    이동   **Q_st 목표대(30~40, `QST_WINDOW_20260822`)도 같은 Q_st 로 유도된 내부 모형이다**(laptop2 6d8ffee, 06:27): 회귀 ln K_H = −13.979 + 0.4511·(Q_st/RT) · 반트호프 b(T) = b(298)·exp[(Q_st/R)(1/T−1/298)] · 목적함수 E = Q_st + 67.5/WC → 허용 창 30.2~46.3.
           회귀 항은 절편이 상쇄하지만 **반트호프의 exp 안 Q_st 는 상쇄되지 않아**(같은 물질이 28.75→33.7 이면 b(373)/b(298) 0.0969→0.0648, WC 커짐) E_new(Q) ≠ E_old(Q−Δ)+Δ. → **목표대는 단순 평행이동으로 못 옮기고 보정과 함께 다시 유도해야 한다. 그 전까지 목표대 대비 판정은 "판정 불가".**
           금지 오독: "보정하면 saIm0583 29.31→34.27 로 목표대 안" — FINAL_VERDICT_20260821 이 인정한 유일한 한계("Q_st 28.75 로 목표대에 못 듦, 주어진 제약 안의 최선")를 지우는 읽기. 다만 DECISION_RULE 은 "Q_st 는 지표 후보가 아님", V5 는 "하드컷 아님" 이라 흔들리는 것은 관문·순위가 아니라 서술 문장 하나(그리고 MAGI-004 §6 (i) 의 이음새).
    이동   Q_st **절대값** 전부 +4.955 (base 22.42→27.38 · saIm050 28.51→33.47 · saIm0583 29.31→34.27 · saIm100 31.07→36.03) · 벤치마크 대역 대조(V5 "하단" 문구) · TSA 지렛대·TSA/VSA **절대 배수** · 그 수를 인용한 포스터·판정 문장

## 4. 조치 — **사용자 결정(09-12) 전 실행 금지** (결과 뒤 자 변경이 아니라 상수 정정이지만 20 JSON·장표를 건드림)
    권고(첫 줄)  (a) 러너 10곳 식을 `−u + R_GAS*TEMP` 로 고치고 머리말에 이 문서 링크 (b) JSON 은 **덮어쓰지 않고** 사이드카 키 `Qst_CO2_rt_corrected = Qst_CO2 + 4.9554` + `WARN_qst_rt` 추가(물 힘장 `WARN_forcefield` 관례) (c) 문서의 절대값 인용 33줄에 "(+4.96 보정 전)" 각주 일괄 (d) 포스터 Q_st·지렛대 절대 수 갱신 (e) CLAUDE.md §0 에 다섯 번째 결함으로 추가(경위: 상수 오프셋은 차이 검사를 통과한다) (f) 러너 아닌 곳 셋(주석·하드코딩·모형 계수) 별도 처리 (g) **`QST_WINDOW` 목표대 재유도**(보정 Q_st 로 회귀·반트호프·E 다시) — 그 전까지 목표대 대비 문장은 판정 불가로 표기
    감사 방법   상수 표현식(`R_GAS * TEMP`)으로 찾으면 별칭·모듈한정·상수 재정의에 뚫린다 — **산출물(`qst… =`)로 훑는다**(Melchior). 이번에 그 차이가 3곳(run_gcmc_v2/v3·run_candidate_gcmc)이었다.
    대안         (b′) JSON 값을 직접 고치고 git 이력으로 원본 보존 — 사이드카보다 단순하나 "결과 파일 사후 수정" 전례를 만든다.
    금지         결정 전 어느 JSON·장표도 고치지 않는다. 새로 내는 Q_st 는 이 문서를 인용해 "보정 전/후" 를 병기.

## 5. 왜 살아남았나
    상수 오프셋은 차이 기반 검사·순위 검사·재현성 검사를 전부 통과한다. 절대값은 문헌 대역 안이었다. 러너 식이 디렉터리 여섯에 복사돼 "여러 곳이 같은 값" 이 검증처럼 보였다.
    잡힌 경로: T-NF-0q 가 물 Widom 에너지를 **응집 에너지(ΔH_vap)와 절대값으로** 견주려다 RT 규약을 다시 유도함 — 절대값을 요구하는 비교가 처음 생긴 자리.

## 6. 조치 실행 — **사용자 결정 2026-09-18 "일단 부호 결함 조치해"** (종합자, 2026-09-18 00:29)
    (a) 러너 10곳 + widom_batch 2줄 → `−u + R_GAS*TEMP` 로 정정, 각 줄에 이 문서 링크 주석. 산출물(`qst… =`) 기준 grep 으로 잔존 0 확인(Melchior 방식). 컴파일 검사 통과.
        run_aryl_gcmc·run_candidate_gcmc 의 "비교 기준 Qst 31.07" 출력 문자열 → 36.03(보정 후; 보정 전 31.07) 병기.
        ⚠ `21_ZIF69_MTV/charge_and_run.py`·`18_PoreNarrowing/charge_and_run.py` 는 root 소유였음 — 디렉터리 권한으로 파일 교체(os.replace), 소유가 mangwon1 로 바뀜.
        **돌고 있는 러너(run_humid_wc*, relax, charge_v3, risk_screen)는 Q_st 를 계산하지 않음** — grep 0. 데스크탑 T-RT-1b·랩탑 T-RT-1·laptop2 §AK 무영향.
    (b) JSON **21개**(§2 는 20개라 했으나 `results_tb5.json` 이 하나 더, 그리고 `oms_sensitivity.json` 은 키가 `Qst`) — 원값 **그대로**, 사이드카 `Qst_CO2_rt_corrected`/`Qst_N2_rt_corrected`/`Qst_rt_corrected` = 원값 + **4.955420**(2·R·298.0 — 러너 TEMP 가 전부 298.0, 298.15 아님) **212개 키** + 파일당 `WARN_qst_rt`. 검산 base 22.4196 → 27.3750.
    (c) md **35줄**(18파일)에 "⟨Q_st 절대값은 RT 부호 정정 전, +4.96 — QST_RT_SIGN_20260911⟩" 꼬리표 — COMMS/·SESSION_LOG 는 역사 기록이라 제외. 대상 수: 22.42·28.51·29.31·29.51·31.07.
    (e) CLAUDE.md §0 다섯 번째 결함으로 추가(4건 → 5건).
    (f) ① widom_batch 주석·docstring 정정. ② `regen_energy.py` QST 하드코딩(21.08/25.17/26.63): 출처 미확인(results_v3 22.42/28.51 과 다름, NEXT_STEPS 에 26.63/31.07 이 v2 이전 수로 등장) — **값 안 건드리고 인용 금지 주석**. ③ `cavity_model.py` 계수 — 보정 전 척도임을 주석. `tsa_vsa_lever.py` ROWS — 보정 전, ×1.495 주석.
    **안 한 것(별도 등록 필요)**
    (d) 포스터·장표 Q_st·지렛대 절대 수 갱신 — 장표 파일이 이 저장소 밖(노션·PDF). 노션 현황 정리본·발표 가이드는 이미 "Q_st 는 차이로만, 목표대 판정 안 함" 으로 적혀 있어 당장 틀린 문장은 없음.
    (g) **`QST_WINDOW` 목표대 재유도** — 회귀·반트호프·E 를 보정 Q_st 로 다시. 자료 0건 등록이 필요한 별도 일. 그 전까지 "목표대 진입/미달" 은 판정 불가 그대로(CLAUDE.md §0 에 박음).
        **[09-18 00:4x 실행]** `QST_WINDOW_RT_20260918.md` · `qst_window_rt.py`: 옛 표 재현 → 보정 척도 최적 41~43, 하한 35~36.5(+5.0, 평행이동과 거의 같음). **물질도 창도 같이 +5** — saIm050·0583 은 여전히 아래(33.5·34.3 대 35.5), saIm100 안. §3 의 "금지 오독" 확인됨. 관문 읽기(권고 35~45 평행이동)는 사용자 안건 §5.
