# COREPOP-H323 — HKHOME 에서 막음이 안 되는 무거운 구조를 랩탑으로 (사용자 지시)

2026-11-15 16:23 KST · desktop(HKHOME) 작성 · 값은 읽지 않음. 계산의 정의(`ASSIGN_COREPOP_HUMID323_20261114.md`)는 그대로이고, **어느 기기가 어느 구조를 막느냐만** 바뀝니다.

## 0. 사용자 지시 (원문)
- 16:1x HKHOME 세션의 설명이 "In neb 계열은 HKHOME 에서 막음이 안 될 공산 · 랩탑(23 GB)으로 넘길지는 b04 막음 단계 뒤에" 였고, 사용자 답은 **"랩탑으로 넘겨"** 였습니다.
- HKHOME 은 이것을 **b03 · b04 에서 HKHOME 이 막지 못한 구조 전부** 로 읽었습니다. b03 의 빠진 12종은 "b04 뒤 HKHOME 병렬 1" 로 미뤄 둔 같은 종류입니다(desktop 11-14 23:05 글). 사용자가 다르게 정하면 바꿉니다.

## 1. 왜 랩탑인가 — 실측
- HKHOME 의 WSL 은 20 GB 이고, 비어 있을 때 가용 메모리가 약 18 GB 입니다.
  - 가드는 가용 5,000 MB 아래에서 kill 합니다.
  - 그래서 혼자 돌아도 **약 13 GB 가 한계**입니다.
  - b04 의 2023[In][neb]3[ASR]4 CO₂ 탐침은 **14.2 GB 에서 kill** 됐습니다(11-15 16:0x).
- 랩탑의 WSL 은 23 GB 입니다. b05 직렬 재시도에서 **혼자 최대 8.0 ~ 14.0 GB 인 호출이 ok** 였고, 17.8 ~ 17.9 GB 인 하나(2015[Zn][pcu]3[FSR]5)는 실패했습니다(laptop 11-15 15:12 글).
  - 그래서 랩탑에서도 안 되는 구조가 남을 수 있습니다. 그런 구조는 빼고 GCMC 를 띄우고, 완주 글에 적습니다.
- 넘기는 목록에는 무겁지 않은 구조도 섞여 있습니다. 병렬로 돌다가 옆 호출 때문에 함께 kill 된 경우입니다(예: 2017[Cu][rob]3[ASR]1 은 1.1 GB 에서 kill). 혼자 돌면 몇 분이면 끝납니다.

## 2. 넘기는 구조 — `corepop_heavy_keys_20261115.json`
- **b03**: `results_corepop_blocks_hkhome_b03a.json` 의 `excluded_not_ok` 12종입니다.
- **b04**: HKHOME b04 막음의 첫 판(96호출)이 끝나 재시도 단계에 들어가면 다음을 합니다(b03 과 같은 방법).
  - 재시도를 멈춥니다.
  - `results_corepop_blocks_hkhome_b04a.json`(세 탐침 ok 부분집합)을 만들고, 그 파일로 HKHOME GCMC 를 띄웁니다.
  - 빠진 구조를 키 파일에 합칩니다.
- **키 파일은 그때 올립니다. 이 글을 올리는 시점에는 아직 없습니다.** 키 파일이 master 에 오면 우편함에 따로 알립니다.

## 3. 랩탑이 돌릴 것

### 3-1. 파일 (전부 master)

| 파일 | md5 | 무엇 |
|---|---|---|
| `corepop_blocks_keys.py` | c2a71d4c | `corepop_blocks.py`(c00cd11a) **무수정 import** 래퍼. 대상만 키 파일의 구조로, 결과 이름은 `results_corepop_blocks_<기기>_<묶음들>_heavy.json`. 측정 · 가드 · 재시도는 원판 그대로입니다 |
| `corepop_chain_keys.sh` | e5f65f5a | `corepop_chain.sh`(ec27c8b3)와 같은 순서 · 관문으로, 대상만 키 파일입니다. 다섯째 인자로 **기다릴 앞 사슬 PID** 를 받습니다 |
| `corepop_subset_blocks.py` | f3db3fce | 부분집합 · 키 파일을 만드는 도구입니다. 랩탑은 안 써도 되고, 같은 꼬리를 만나면 쓸 수 있습니다 |
| `corepop_heavy_keys_20261115.json` | (올릴 때 적음) | 넘기는 구조 목록 |

### 3-2. 띄우는 명령 — 랩탑의 b05 사슬이 **끝난 뒤** 돌도록 그 PID 를 줍니다
Zeo++ 와 RASPA 는 같은 기기에서 동시에 돌리지 않습니다(CLAUDE.md §5). 그런데 앞 사슬의 Zeo++ 끝과 GCMC 시작 사이에 simulate 0 인 틈이 있어서, "simulate 0 기다림" 만으로는 그 틈에 끼어듭니다. 그래서 PID 를 기다립니다.

    cp 21_ZIF69_MTV/corepop_chain_keys.sh ~/.mof_chain/
    ps -eo pid,args | grep -v grep | grep 'corepop_chain.sh laptop b05'     # 실제 bash PID (CLAUDE.md §4)
    REPO=/home/skyjun/mof_run_1108 setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh laptop corepop_heavy_keys_20261115.json 1 16 <b05 사슬 PID> < /dev/null > /dev/null 2>&1 &

- Zeo++ 병렬은 **1**(무거운 구조) · 워커 16 입니다. 기록은 `~/.mof_chain/corepop_laptop_heavy.{chain,zeo,smoke,gcmc}.log` 에 남습니다.
- 결과는 다음 파일들입니다. 셋 다 postman 글롭 `results_*.json` 안이라 자동으로 반입됩니다.
  - `results_corepop_blocks_laptop_b03_b04_heavy.json`
  - `results_corepop_e_humid3_323_laptop_b03_b04.json` + `_audit.json`
- 읽는 법 등록(`COREPOP_H323_READING_REGISTRATION_20261115.md`)은 이 결과 파일을 그대로 받습니다. 행마다 대상 목록의 묶음으로 나뉩니다.
- 띄우기 전 확인할 것 셋
  1. 다섯 파일의 md5
  2. 랩탑 트리에 이 구조들의 `corepop_zeo_runs/<파일 이름>/` 폴더가 없는지. 있으면 실행기가 시작을 거부합니다(안전한 실패).
  3. `corepop_blocks.py` c00cd11a

### 3-3. 견적 (출처 같이)
- **Zeo++**: 랩탑 b05 직렬 재시도 실측은 ok 평균 8.4 분 · 실패 16 분입니다(같은 기기 · 다른 구조). 호출 수 = 구조 수 × 3 이므로, b03 12종만으로도 36호출 ≈ 5 ~ 6 h 입니다. b04 몫이 더해지면 길어지고, 그동안 랩탑은 논리 16 가운데 1 만 씁니다.
- **GCMC**: b01 실측(30작업 9.5 h · 가장 긴 작업 10.9 h, 같은 기기)으로 보면, 몇 종이 남든 가장 긴 작업 하나가 벽시계를 정할 공산이 큽니다.
- 그래서 b05 GCMC(11-16 04 ~ 06시 견적) 뒤에 시작하면, 이 구조들의 결과는 **11-16 밤 무렵**입니다. 랩탑은 그동안 b06 을 가져가지 못합니다. 순서를 바꿀지(b06 먼저 등)는 사용자 · 랩탑 판단입니다.

## 4. HKHOME 에서 한 시험 (16:1x ~ 16:2x · 실제 Zeo++ · RASPA 는 안 띄움)
- **래퍼 드라이**(`COREPOP_ZEO_DRY=1`): 13종(b03 12 + In neb ASR4) · 묶음 b03 · b04 · 계획 39호출 · 병렬 1. 거부되는 길 셋(대상 밖 · 중복 · env 없음) 모두 rc 1.
- **사슬 앞부분**: `pgrep` 이 0 을 내는 대역을 세웠고, 대역이 먹는 것을 먼저 찍었습니다(실제 network 2 → 대역 0).
  - 그 위에서 앞 사슬 PID 대기 → simulate · network 0 → 묶음 읽기 → 래퍼 → "막음 완주 파일 없음 — 멈춤"(드라이라 정상) rc 3.
  - 막음 파일 이름이 래퍼의 출력 이름과 같습니다.
- **사슬 뒷부분**:
  - 세 탐침 ok 추리기를 b03a 에 돌려 20/20 이 나왔습니다.
  - GCMC 드라이(`COREPOP_F_DRY=1`, RASPA 안 띄움)에서 묶음 b03 · b04 가 결과 이름 `..._<기기>_b03_b04` 로 나왔고, 입력 `ExternalTemperature 323.0` · simulate 0 이었습니다.
- **부분집합 도구**: b03 원판(8a6c4398)에서 b03a 를 다시 만들었더니 행 · 빠진 목록(순서까지) · summary · 원판 md5 가 기존 b03a 와 모두 같았습니다. 완주 파일 거부 · 키 중복 거부도 확인했습니다.
- **안 해 본 것**:
  - 래퍼로 실제 Zeo++ 를 돌리는 것
  - 이 사슬로 스모크 · 본 계산까지 가는 것. 이 부분은 `corepop_chain.sh` 와 같은 줄이고 묶음 이름만 다릅니다.
