# COREPOP-H323 — CoRE 모집단 3D 의 323 K 습윤 3성분 흡착점 (사용자 직접 지시 · 세 기기 분할)

2026-11-14 17:30 KST · desktop(HKHOME) 작성 · **자료 0건**(이 계열의 결과는 아직 한 행도 없음).

## 0. 사용자 지시 (원문)
- 17:1x "그리고 CORE 기존 데이터도 323K로 조정할수 있는 방법 있을까?"
- 17:2x "급한 계산이니까, 다른 로컬에도 코어 최대로 해서 CoRE 기존 데이터 323K, 3성분 습윤 조건으로 계산 다시 돌려서 컴퓨팅 분할시켜 진행해줘"
- 17:3x "일단 가능한 만큼 넣고, 다른 로컬 기기를 붙히면 더 줄일 수 있나?" · "2D라 계산 자체가 의미없는 데이터들 제외한 재료들을 감안하면?"
- 같은 날 "코어 16까지 쓸수있지않았니?" (HKHOME 논리 16 사용)

## 1. 대상 — `corepop_humid323_targets.json` (296종 · 묶음 b01~b10)
- `core_pop_annotated.json` 행 중 status ok · `probe_convention` False · `formal_charge_nonzero` False(CLAUDE.md §2) · **`dim == 3` 만**(2D 제외, `run_coremix_s60.py` 와 같은 열) · **CORE22 22종 제외**(323 K 습윤이 이미 끝남: §F 선택도 66/66 · H 회수량 22/22).
- 순서 = 298 K 건조 Widom selectivity(§AV 우리 자) 큰 순. **우선순위를 정하는 데만 쓰고 판정에는 쓰지 않습니다.** 끝난 만큼 쓰는 계산이라 겨룰 가능성이 큰 구조부터.
- 32종씩 묶음 b01~b09, b10 은 8종. CIF 는 `core_pop_cifs.zip` 바이트(md5 · 원자 수 대조).

## 2. 조건 — CORE22 §F 와 같음
323 K · 100 kPa · y CO₂ 0.150000 / N₂ 0.738859 / 물 0.111141(RH 90 %) · 5,000 + 15,000 · UFF_MOF · 12 Å · Ewald 1e-6 · CoRE CIF 전하 · 단위셀은 래퍼 규칙 · TIP5P-Ew(Hw/Lw none, 파일 관문). Zeo++ `-block` 세 탐침(CO₂ 1.65 · N₂ 1.82 · 물 1.30 Å · 50,000 표본 · 단위셀) — 구 0 이면 그 성분 막음 없음.
**다른 점 하나: 구조당 1씨앗(r1).** CORE22 는 3씨앗입니다. 1씨앗 행의 ± 는 RASPA 한 번의 ± 입니다.

## 3. 실행기 (원판 무수정 · 사본)
| 파일 | md5 | 원판 |
|---|---|---|
| `corepop_blocks.py` | c00cd11a | `core22_blocks_laptop.py` — 묶음 · 병렬(`COREPOP_ZEO_PAR`) · 새 호출은 MemAvailable ≥ 8,000 MB 일 때만 · simulate 있으면 멈춤 · 실패 호출은 끝에서 한 번에 하나로 재시도 |
| `run_corepop_e_humid3.py` | e05cbc1b | `run_core22_e_humid3.py`(d24e8e2d) — 대상 목록 · 막음 표 여러 파일 · 반복 수 env |
| `run_corepop_e_humid3_323.py` | 75307c47 | `run_core22_e_humid3_323.py`(b975bd93) — import 대상 · env 이름 · 이름만 |
| `corepop_chain.sh` | ec27c8b3 | 한 묶음 사슬: simulate 0 → Zeo++ → 막음 ok 구조 → 스모크 2종(10 사이클) → 본 계산 |
래퍼 `run_znbdt_e_humid3.py`(97023663) · `run_znbdt_e_humid3_323.py`(7f83dc3c) · 러너는 무수정 import. HKHOME 드라이런: 입력이 CORE22 §F 실제 입력과 사이클 줄만 다름(드라이 10 사이클), 323 K 세 값 확인 통과.

## 4. 기기 분담 — 각 기기가 자기 묶음의 Zeo++ 와 GCMC 를 둘 다 (기기 사이 의존 없음)
| 기기 | 첫 묶음 | Zeo++ 병렬 | 워커 | 띄우는 명령 |
|---|---|---|---|---|
| 랩탑 (물리 8 · 논리 16 · 23 GB) | **b01** | 3 | 16 | `bash ~/.mof_chain/corepop_chain.sh laptop b01 3 16` |
| laptop2 (물리 6 · 논리 12 · 15 GB) | **b02** | 2 | 12 | `bash ~/.mof_chain/corepop_chain.sh laptop2 b02 2 12` |
| HKHOME (물리 8 · 논리 16 · 19 GB) | **b03** (323 K Widom 7건 뒤 자동) | 2 | 16 | `bash ~/.mof_chain/corepop_chain.sh hkhome b03 2 16` |
- 띄우기: `cp 21_ZIF69_MTV/corepop_chain.sh ~/.mof_chain/` 뒤 `setsid nohup bash ~/.mof_chain/corepop_chain.sh <기기> <묶음> <병렬> <워커> < /dev/null > /dev/null 2>&1 &`. `REPO`(기본 `~/mof_project`) · `PY`(기본 `~/miniconda3/envs/czeromof/bin/python`) 는 env 로 덮을 수 있음.
- 받을 파일(러너가 도는 기기는 pull 대신): `git fetch` 뒤 `git show origin/master:21_ZIF69_MTV/<파일> > 21_ZIF69_MTV/<파일>` — 위 다섯 파일. 띄우기 전에 md5 를 위 표와 대조.
- **다음 묶음 b04~b10**: 자기 묶음이 끝난 기기가 **착수 글을 먼저 올려 가져감**(먼저 올린 기기가 그 묶음을 맡음). 숫자 순서대로.
- 상한: 각 기기 논리 코어 전부(사용자 지시). Zeo++ 와 RASPA 는 같은 기기에서 동시에 돌지 않음(사슬이 Zeo++ 를 simulate 0 에서만 띄움 · CLAUDE.md §5).

## 5. 견적 (출처 같이)
- Zeo++: CORE22 막음 실측(랩탑 66호출 · 평균 161 s · 최대 RSS 6.4 GB) → 묶음 96호출 ÷ 병렬 2~3 = **1.4~2.1 h**.
- GCMC: CORE22 §F HKHOME 실측(24작업 · 8워커 · 6.3 h → 작업당 약 2.1 h, 같은 조건 · 비슷한 N_super)에 논리 16 경합을 얹음 → 32작업 = 16워커 2물결 **6~8 h** · laptop2 12워커 3물결 **9~11 h**. 랩탑 두 대는 다른 기기라 위쪽을 열어 둠.
- 그래서 11-15 09:00 까지 b01 · b02 · b03 (≈ 96종) 과 b04~ 일부. 296종 전부는 세 기기로 약 30 h(11-16 새벽).
- 기기를 하나 더 붙이면(논리 16 급): GCMC 용량 +35 % 안팎 → 전체 약 22 h. 새 기기는 `NEW_MACHINE_20260822.md` 로 RASPA · 힘장(Hw/Lw none) · Zeo++ 를 갖추는 데 1~2 h.

## 6. 읽는 법 — **아직 등록 안 됨**
판정 · 읽는 법은 종합자 몫입니다. 첫 결과를 읽기 전(자료 0건)에 등록합니다(CLAUDE.md §2 · MAGI §9-6). 기기는 완주 글에 표지(완주 · 적재 줄 · N₂ 성분 · 막음 등식 · 씨앗)만 적고 값 · 평균 · 순위는 적지 않습니다.

## 7. 산출
`results_corepop_blocks_<기기>_<묶음>.json` · `results_corepop_e_humid3_323_<기기>_<묶음>.json` + `_audit.json`(postman 이 반입 · 안 돌면 완주 글과 함께 손으로). 실행 폴더 `humid_wc_runs_v3w_323/corepop_e3_323_<기기>_<묶음>/` 와 `corepop_zeo_runs/` 는 남겨 둠.
