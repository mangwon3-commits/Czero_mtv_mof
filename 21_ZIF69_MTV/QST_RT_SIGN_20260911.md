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
    러너 9파일  21_ZIF69_MTV/run_aryl_gcmc.py:278 · 21_ZIF69_MTV/charge_and_run.py:234 · 07_Bracketed_MTV/run_widom_batch.py:141,142(**CO₂·N₂ 둘 다**) ·
                13_PACMAN/run_raspa_ddec6.py:140 · 14_Strategies/run_raspa_strat.py:140 · 14_Strategies/oms_sensitivity.py:150 · 17_NestEffect/run_raspa_nest.py:140 · 18_PoreNarrowing/charge_and_run.py:212
                (+ Melchior 가 든 run_gcmc_v2.py:129 · run_gcmc_v3.py:163 — 데스크탑 grep 패턴에 안 잡힘, 확인 필요)
    결과 JSON   `Qst_CO2` 보유 **20개**(results_v3·v3grid·v3cliff·v3ens0583/075/nb050·v3pctl·v4mix·aryl_results·candidate_results·zif69_results·v3_smoke 등)
    문서        Q_st/지렛대 언급 md **52개**, 절대값 인용 줄 **33**(22.42·28.51·29.51·31.07·지렛대 배수·TSA/VSA)
    하류        `tsa_vsa_lever.py:137` `lev = exp(Q_st/R·(1/298−1/373))` — Q_st 가 지수 안 → 공통 배수 **1.495**: base 지렛대 6.2→9.2, saIm050 10.1→15.1; TSA/VSA 절대 배수 base 2.1→3.1, saIm050 3.4→5.0.

## 3. 바뀌는 것 / 안 바뀌는 것
    불변   조성 간 Q_st **차**(치환 축 대 모체 배치 단위 등 모든 차 기반 판정) · 순위 · K_H · 선택도 · 로딩 · 지렛대의 조성 간 **비** · "TSA 지렛대는 Q_st 와 함께 커지고 VSA 는 고정" 논지의 모양
    이동   Q_st **절대값** 전부 +4.955 (base 22.42→27.38 · saIm050 28.51→33.47 · saIm0583 29.31→34.27 · saIm100 31.07→36.03) · 벤치마크 대역 대조(V5 "하단" 문구) · TSA 지렛대·TSA/VSA **절대 배수** · 그 수를 인용한 포스터·판정 문장

## 4. 조치 — **사용자 결정(09-12) 전 실행 금지** (결과 뒤 자 변경이 아니라 상수 정정이지만 20 JSON·장표를 건드림)
    권고(첫 줄)  (a) 러너 9파일 식을 `−u + R_GAS*TEMP` 로 고치고 머리말에 이 문서 링크 (b) JSON 은 **덮어쓰지 않고** 사이드카 키 `Qst_CO2_rt_corrected = Qst_CO2 + 4.9554` + `WARN_qst_rt` 추가(물 힘장 `WARN_forcefield` 관례) (c) 문서의 절대값 인용 33줄에 "(+4.96 보정 전)" 각주 일괄 (d) 포스터 Q_st·지렛대 절대 수 갱신 (e) CLAUDE.md §0 에 다섯 번째 결함으로 추가(경위: 상수 오프셋은 차이 검사를 통과한다)
    대안         (b′) JSON 값을 직접 고치고 git 이력으로 원본 보존 — 사이드카보다 단순하나 "결과 파일 사후 수정" 전례를 만든다.
    금지         결정 전 어느 JSON·장표도 고치지 않는다. 새로 내는 Q_st 는 이 문서를 인용해 "보정 전/후" 를 병기.

## 5. 왜 살아남았나
    상수 오프셋은 차이 기반 검사·순위 검사·재현성 검사를 전부 통과한다. 절대값은 문헌 대역 안이었다. 러너 식이 디렉터리 여섯에 복사돼 "여러 곳이 같은 값" 이 검증처럼 보였다.
    잡힌 경로: T-NF-0q 가 물 Widom 에너지를 **응집 에너지(ΔH_vap)와 절대값으로** 견주려다 RT 규약을 다시 유도함 — 절대값을 요구하는 비교가 처음 생긴 자리.
