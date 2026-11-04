# ASSIGN — ZNBDT-C2 후속 세 건 · 밤샘 위임 결정표 (2026-11-05 02:4x · 종합자 등록 · 자료 0건)

**사용자 위임 11-05 02:3x**: *"30분마다 우편함 읽어서, 08:30 전까지 계산 완료됐으면 30분 단위로 명령 우편함에 내려줄 수 있어? 각 로컬들도 30분마다 읽어오라 할게."* → 종합자가 02:30~08:00 매 30분 master 를 읽고 `COMMS/cloud.md` 에 ★ 명령을 냅니다. **이 문서가 밤에 낼 수 있는 명령의 전부입니다** — 여기 없는 것은 아침에 사용자 몫(등록 층 · 순위표 · 포스터 · ′1~′6 은 밤에 손대지 않음). 규약 §11-5-2(보완 단계) · §10 시간창(02:00~10:00 자율) 안.
결과를 읽기 전에 읽는 법을 적습니다. ZNBDT-C2(`ASSIGN_ZNBDT_C2_20261105.md`, HKHOME 02:06) 는 지금 돌고 있고 값은 아직 없습니다(02:11 반입 파일 6행 pending — 종합자가 메타만 확인).

## 1. 명령 #1 — laptop2: N₂ · CO₂ 질량중심 밀도 격자 (관측 · 판정 없음) — **지금 착수**

| 항목 | 내용 |
|---|---|
| 구조 4 | `charged_v3/e22_parent_DDEC6.cif` · `e24i_cn_open_DDEC6.cif` · `e24i_ch3_open_DDEC6.cif` · `znbdt_c2_apolarU_DDEC6mod.cif`(md5 3e079487) |
| 조건 | 혼합 CO₂/N₂ 0.15/0.85 · 100 kPa · 298 K · 5,000+15,000 · 1씨앗(관측용 — 산포는 재지 않음, 그래서 수치 비교에 쓰지 않음) · UFF_MOF · 전하 ON · 컷오프 12 · 2×2×2 규약 그대로 |
| 격자 | `ComputeDensityProfile3DVTKGrid yes` · COM 격자(`COMDensityProfile_CO2.vtk` · `_N2.vtk`) · 격자점은 `run_density_map.GRID` 그대로 |
| 러너 | `run_density_map` 모듈을 **무수정 import** 하는 얇은 실행기(성분 둘 · 몰분율만 바꿈). 무수정 import 가 안 되면 저장소 밖 사본에 바꾼 줄을 적고 dry(입력만) 먼저. 둘 다 안 되면 우편함에 적고 멈춤 — 그것도 답 |
| 완주 | `Simulation finished` 표지 + 두 성분 적재 줄 각 1 + VTK 존재(존재만으로는 안 됨 — CLAUDE.md §0 09-24 결함) · rc 0 |
| 산출 | `density_znbdt_c2/<tag>/VTK/System_0/COMDensityProfile_*.vtk` + `results_znbdt_c2_density_laptop2.json`(표지 수 · 적재 · 시간) → master |
| 견적 | 출처 = 같은 계 E-24i 혼합 실측(HKHOME 53~80 분/작업) → laptop2 6코어 4작업 동시 ≈ 1.5 h(최장 단일 작업이 묶음) |

**읽는 법(종합자 · 서술만)**: N₂ COM 밀도 차 격자 (−CN − 모체) · (apolarU − 모체) · (−CH₃ − 모체). N₂ 가 비는 자리가 **막대 축 주위에서 셋 다 같으면 모양**, **−CN 에만 니트릴 N 곁에서 비고 apolarU 에서 사라지면 극성**(CO₂ 가 그 자리를 차지하는지 CO₂ 차 격자로 함께 봄). 문턱 없음 · 순위 없음 — ZNBDT-C2 의 수치 판독(§2-4)을 **그림으로 뒷받침하거나 어긋남을 보이는** 용도. `export_diff_vtk.py` 규약(COM 하드코딩) 그대로.

## 2. 명령 #2 — HKHOME: apolarU 323 K S_mix 3씨앗 (Caspar ③ 온도 의존) — **조건: ZNBDT-C2 완주 뒤**

| 항목 | 내용 |
|---|---|
| 러너 | `run_znbdt_b_mix323.py` 사본 `run_znbdt_c2_b_mix323.py` — 대상만 `charged_v3/znbdt_c2_apolarU_DDEC6mod.cif`(md5 3e079487) · 출력 `results_znbdt_c2_b_mix323_hkhome.json` · 나머지(323 K · 0.15/0.85 · 100 kPa · 5,000+15,000 · 3씨앗 · 15 s 간격) B 와 같음 |
| 완주 | B 와 같은 표지(status ok · rc 0 · 씨앗 고유 · 두 성분 적재 각 1줄) |
| 견적 | B 실측 41~42 분/작업 · 3 동시 → ≈ 45 분 |

**읽는 법(자료 0건 등록)**: r_T = N_N₂(323)/N_N₂(298)(298 은 ZNBDT-C2 apolarU S_mix 3씨앗 평균). 기준(R4 §4-1 · HKHOME R3): 모체 **1.00** · −CN **1.24** · −Br 1.19. 자 = 씩 ± 전파(B 와 같은 식) · 문턱 1.5 단위.
- apolarU 의 r_T 가 모체와 1.5 단위 안이고 −CN 과 1.5 단위 밖 → **"−CN 의 323 K 풀림은 전하가 만든 경쟁 몫"**(Caspar ③ 의 극성 쪽 표지).
- −CN 과 1.5 단위 안이고 모체와 밖 → **풀림은 전하 없이도 남음 — 모양/다른 원인**.
- 둘 다 안 또는 둘 다 밖 → 판별 불가(서술만). 보조: S_mix(323)/S_mix(298) 비(−CN 0.591 · 모체 0.669).
ZNBDT-C2 주 판독(§2-4)과 **따로** 적고, 둘이 어긋나면 어긋난다고 적습니다(한 수로 다른 층을 말하지 않음 — R4 교훈 ㄱ).

## 3. 명령 #3 — −NO₂ 열린 자리 선별 (빌드 · 이완 · 관문 (0a)(0b) 만) — **빌드 = 랩탑(E 완주 뒤) · 이완·관문 = HKHOME(C2 완주 뒤)**

> **[03:0x 기기 변경 — 랩탑 02:5x 보고: 랩탑에 xtb 없음(`MACHINE_CAPABILITIES.md`)]** 랩탑은 빌드와 빌더 충돌 검사까지만 하고 `znbdt_no2_screen/E24i_ZnDia_NO2_open.cif` · `znbdt_no2_build.json` 을 master 로. **이완 + (0a)(0b) 는 HKHOME** 이 C2 완주 뒤(1코어 · 약 3분 · #2 와 같이 돌아도 됨) `relax_tnf.py --job e24i_no2_open=znbdt_no2_screen/E24i_ZnDia_NO2_open.cif` → `znbdt_c2_screen/screen_measure.py` 와 같은 측정으로 잇고 `results_znbdt_no2_screen_hkhome.json` 을 올립니다. 문턱 · 산출 항목은 아래 그대로(바뀐 것은 기기만).

| 항목 | 내용 |
|---|---|
| 빌드 | `build_znbdt_c1_bdtdc.py`(HKHOME 61b4ee4a) 사본 → `KINDS=('NO2',)` · `B.SMILES['NO2']='c1ccccc1[N+](=O)[O-]'`(E-22 NO₂ 와 같은 조각) · 출력 `znbdt_no2_screen/` · 이름 `e24i_no2_open` |
| 이완 · 관문 | `relax_tnf.py` GFN-FF 고정셀 → (0a) 이종–H ≥ 1.8 · 변위 ≤ 1.0 / (0b) `clash_gate.check` 겹침 < 0.4 — ZNBDT-C2 §0 선별과 같은 코드 · 같은 문턱 |
| 산출 | 랩탑: `znbdt_no2_screen/E24i_ZnDia_NO2_open.cif` · `znbdt_no2_build.json` / HKHOME: `results_znbdt_no2_screen_hkhome.json`(거리 · 겹침 · 최악 짝 · 자리별) → master. **전하 · Widom · GCMC 는 하지 않음** |
| 견적 | 같은 계 실측(HKHOME C1 빌드~이완 3.2 분 + 측정) → ≈ 15 분 |

**뜻**: ZNBDT-C2 가 극성 쪽이면 다음 설계는 "극성을 키우되 물을 덜 끄는 자리" 이고 −NO₂ 가 첫 후보입니다(R4 §5-1 · ASSIGN_C1 §3). 들어가는지(관문)만 밤에 봅니다. 통과/탈락 어느 쪽도 **설계 결정이 아니라 가능성 표**입니다 — 다음 걸음은 아침 사용자.

## 4. 결정표 — ZNBDT-C2 주 판독(U판, `ASSIGN_ZNBDT_C2` §2-4)에 따라 종합자가 밤에 하는 것

| C2 판독 | 종합자 | 기기 명령 |
|---|---|---|
| 모양 | 재계산 대조 · ★ 판독 글 | #2 · #3 그대로(온도 의존과 −NO₂ 가능성은 어느 쪽에서도 쓸모) |
| 중간(f 병기) | 같음 | 같음 |
| 극성 | 같음 | 같음 — #3 의 의미가 커짐(아침 권고 첫 줄에 올림) |
| 판별 불가(U≠I) | 재계산 대조 · "보정 방식에 민감" 기록 | #2 보류(apolarU 하나로 못 읽음) · #3 그대로 · 아침 사용자 |
| 미완주(08:00 까지) | pending 수만 기록 | 없음 |

**어느 경우에도 밤에 하지 않는 것**: 순위표 재생성 · 포스터 · 등록 보완 ′1~′6 · 새 설계 후보의 전하·GCMC 착수 · 등록 층(문턱) 변경 · 기기 재기동.

## 5. 절차

- 기기는 **매 30분 `git fetch origin master` 뒤 `COMMS/cloud.md` 의 ★ 글**을 읽고, 착수 · 완주 · 막힘을 자기 우편함에 **한 줄**(시각 · PID · 표지)로. 조건부 명령(#2 · #3)은 조건이 차면 **종합자 글을 기다리지 않고** 착수해도 됩니다 — 이 문서가 이미 명령입니다.
- 종합자는 매 30분 읽고, 바뀐 것이 있을 때만 씁니다. 08:30 아침 보고에 전부 모읍니다.
- 판정은 종합자, 값과 관문은 기기(§11-5-2-5). HKHOME 은 사용자 지시대로 C2 보고를 사용자에게 하고, 결과 파일은 postman 으로 master 에 옵니다 — 종합자는 그 파일을 읽습니다.
