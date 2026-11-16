# COREPOP-H323 — b09 무거운 구조 나누기 · 끊어도 남는 실행 (사용자 지시 2026-11-16)

2026-11-16 15:16 KST · desktop(HKHOME) 작성 · **값 0건 읽음**(이 글의 숫자는 메모리 · 시간 · 표지뿐).

## 0. 지시 원문
- 15:0x "b09는 지금 나눠서 최대한 계산하자. 중간에 끊어도 중단한 지점까지는 보존할 수 있게 해줘"

## 1. 왜 나누나
- laptop2 의 b09 무거운 구조 21종 사슬(10:02 시작)이 4 h 동안 **세 탐침이 다 된 구조가 0** 입니다(master 중간 파일 `results_corepop_blocks_laptop2_b09_heavy.json`, elapsed 14,268 s).
  - 2015[Zn][hww]3[ION]4 · [ION]2 는 세 탐침 모두 가드 kill(-9)입니다.
  - Cd ins 두 구조와 Zr hex [ASR]1 은 물 탐침(1.30 Å)만 가드 kill 됐습니다. 물 탐침이 가장 무겁습니다.
  - 그래서 laptop2 의 실질 한도는 약 8 GB 로 봅니다. 남은 15종 대부분이 그 위입니다.
- b09 는 298 K 건조 선택도 순위 261~288위입니다. 등록된 첫 읽기(b01~b03)에는 들지 않습니다.

## 2. 분담
예측 최대 메모리 = exp(−6.9187 + 1.05443 ln V) × 1.17 GB입니다. V 는 단위셀 부피(Å³)이고, desktop 적합(n 105)입니다.
기기 한도는 HKHOME 약 13 GB(b07 가드 kill 13.4~14.1 실측), pc4 9.3 GB(사용자 결정), 랩탑 약 17.5 GB(실패 17.5 · 17.8 실측)입니다.

| 기기 | 키 파일 (md5) | 구조 (예측 GB) | 언제 |
|---|---|---|---|
| HKHOME | `corepop_b09_keys_hkhome.json` (d43be8f7) | 2020[Zr][hex]3 [ASR]1 · [FSR]1 (9.2) · 2017[Cd][met]3[ASR]1 (12.1) · 2017[Ag][sqc]3 [ASR]1 · [FSR]1 (10.1) — **5종** | 11-16 15:14:56 착수 |
| pc4 | `corepop_b09_keys_pc4.json` (d1cb3aca) | 2019[Cd][ins]3 [FSR]2 · [ASR]2 (8.7) · 2021[Cd][pcu]3 [FSR]2 · [ASR]2 (8.2) · 2020[Co][pts]3 [FSR]1 · [ASR]1 (6.1) · 2013[Cd][rtl]3[ASR]2 (6.9) — **7종** | 지금 도는 b10 사슬이 끝난 뒤 |
| 랩탑 (선택) | `corepop_b09_keys_laptop.json` (7750c8be) | 2015[Zn][hww]3[ION]2 (14.5) · 2021[Cd][kag]3[FSR]1 (16.7) — **2종** | 무거운 17종 GCMC 가 끝나 비었을 때만 |
| 시도 안 함 | `corepop_b09_skipped.json` (79110527) | 2015[Zn][hww]3[ION]4 (19.4) · 2016[Ti][srs]3[ASR]1 (23.2) · 2015[Zr][ftw]3[ASR]2 (31.9) · 2017[Co][tfz]3[ASR]1 (20.1) · 2020[Fe][tbo]3 [FSR]2 · [ASR]2 · [FSR]1 (19.5) — **7종** | 예측이 17.5 GB 를 넘어 어느 기기도 못 함 |
| laptop2 | — | b09 사슬을 멈춤. b02 의 마지막 작업과 그 러너는 그대로 둡니다. | 이 글을 받는 대로 |

- 원래 목록은 `corepop_rest_keys_b09.json`(5d475e88) 21종이고, 위 네 묶음이 그것을 겹침 없이 나눕니다.
- **같은 구조가 두 기기의 GCMC 결과에 들어가면 안 됩니다.** 그래서 laptop2 의 사슬은 꼭 멈춰야 합니다. 멈추지 않으면 Co pts · Cd rtl 이 pc4 와 겹칩니다.

## 3. 끊어도 남게 하는 방법 — `corepop_chain_perkey.sh` (8169fa70)
- `corepop_chain_keys.sh`(e5f65f5a)와 순서 · 관문이 같습니다: simulate 0 · network 0 → Zeo++ 막음(병렬 1) → 세 탐침 ok 구조만 → 스모크(최대 2종) → 본 계산.
- **다른 것은 본 계산 하나입니다.** 러너(`run_znbdt_e_humid3.py`)는 작업이 전부 끝난 뒤에야 결과 · 감사를 씁니다. 그래서 한 러너에 여러 구조를 넣으면, 끊을 때 끝난 구조까지 잃습니다.
  - 이 사슬은 구조마다 러너를 하나씩 띄웁니다(`COREPOP_F_MACHINE=<기기>_sNN`, 워커 1, 30 초 간격).
  - 결과는 구조마다 `results_corepop_e_humid3_323_<기기>_sNN_b09.json` + `_audit.json` 으로 생깁니다.
  - 끊으면 그때 돌던 구조만 잃습니다. 러너 · 래퍼 · Zeo++ 래퍼는 고치지 않았습니다(md5 e05cbc1b · 75307c47 · 97023663 · 7f83dc3c · c00cd11a · c2a71d4c).
- **Zeo++ 는 원판대로 호출마다 저장됩니다.** Zeo++ 단계에서 끊기면 이렇게 살립니다.
  - `python corepop_subset_blocks.py subset <막음 파일>` 로 세 탐침 ok 구조만 담은 `…a.json`(finished 붙음)을 만듭니다.
  - `ZEO_BF=<그 a 파일>` 을 주고 이 사슬을 다시 띄우면 Zeo++ 를 건너뛰고 스모크와 본 계산만 합니다.
- 끊는 법: 사슬 bash → 러너 파이썬 → `simulate` 순서로 **PID 로** 끊습니다(CLAUDE.md §4). PID 는 `~/.mof_chain/corepop_<기기>_perkey.pids` 에 적힙니다. 끊긴 구조를 다시 돌릴 때는 기기 이름을 새로 줍니다. 러너가 같은 폴더면 거부합니다.
- 예행(HKHOME, 러너 · Zeo++ 자리에 대역): 세 길을 다 쟀습니다.
  - ① 5종 중 1종이 물 탐침 실패 → 4종만 본 계산에 들어갔고, MAXPAR 2 가 지켜졌고, 대괄호 든 키가 그대로 넘어갔습니다.
  - ② `ZEO_BF` 로 1종 → 스모크 기대 1 · rc 3 이 로그에 그대로 찍혔습니다.
  - ③ finished 없는 막음 파일 → exit 3 으로 멈췄습니다.

## 4. 기기별로 붙여 넣을 줄
- **laptop2**: `21_ZIF69_MTV/COREPOP_B09_SPLIT_20261116.md 읽고 §2 laptop2 몫대로: b09 무거운 구조 사슬(corepop_chain_keys_overlap.sh) bash · 그 Zeo++ 파이썬 · network 만 PID 로 끄고(b02 러너와 simulate 는 그대로), 막음 중간 파일을 마지막으로 올리고 멈춘 글 남겨`
- **pc4**: `21_ZIF69_MTV/COREPOP_B09_SPLIT_20261116.md 읽고 §2 pc4 몫대로: git fetch 뒤 corepop_chain_perkey.sh · corepop_b09_keys_pc4.json 을 git show 로 받아 md5 대조하고, 지금 도는 b10 사슬의 bash PID 를 기다릴 PID 로 줘서 띄우고 착수 글 올려`
- **랩탑 (비었을 때만)**: `21_ZIF69_MTV/COREPOP_B09_SPLIT_20261116.md 읽고 §2 랩탑 몫대로: 무거운 17종 GCMC 가 끝났으면 corepop_chain_perkey.sh 를 laptop 이름 · corepop_b09_keys_laptop.json 으로 띄우고(아직 돌면 그 사슬 bash PID 를 기다릴 PID 로), 착수 글 올려`
- 띄우는 명령(세 기기 공통 · `REPO` · `PY` 는 env 로 덮을 수 있음):
  `cp 21_ZIF69_MTV/corepop_chain_perkey.sh ~/.mof_chain/ && setsid nohup bash ~/.mof_chain/corepop_chain_perkey.sh <기기> $HOME/mof_project/21_ZIF69_MTV/corepop_b09_keys_<기기>.json [<기다릴 bash PID>] < /dev/null > /dev/null 2>&1 &`

## 5. 견적 (출처 같이)
- Zeo++ 호출 시간은 같은 계열의 실측에서 왔습니다.
  - HKHOME b07: 부피 5,000~6,500 Å³ 에서 호출당 약 7~11분입니다. 15호출이면 **약 2~3 h** 입니다.
  - pc4 b06: 같은 부피대에서 호출당 약 4~6분입니다. 21호출이면 **약 1.5~2 h** 입니다.
- GCMC 도 실측에서 왔습니다. 무거운 구조 한 작업이 HKHOME b07 에서 최장 약 4.7 h, pc4 b06 은 24작업 전체가 1.45 h 였습니다.
  - 구조마다 러너가 하나이므로 벽시계는 **최장 단일 작업**이 정합니다.
- 그래서 HKHOME 은 11-16 20~23시, pc4 는 b10 이 16:30 에 끝난다면 20~21시로 봅니다.

## 6. 읽기와의 관계
- 이 결과는 등록된 첫 읽기(b01~b03)에 들지 않습니다. 모집단 읽기에 넣을 범위와 마감 시각은 **값을 읽기 전에** 따로 등록합니다(CLAUDE.md §2).
- 기기는 완주 글에 표지만 적습니다(완주 · 적재 줄 · N₂ 성분 · 막음 등식 · 씨앗). 값 · 평균 · 순위는 적지 않습니다.
