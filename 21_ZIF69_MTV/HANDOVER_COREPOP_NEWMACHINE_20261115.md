# COREPOP-H323 새 기기 인계 — 처음 붙는 로컬 기기 2대가 남은 묶음을 가져가는 법

2026-11-15 15:3x KST · 랩탑 작성 · 사용자 지시(랩탑 세션). 이 글은 계산을 새로 정하지 않습니다. 계산의 정의는 `ASSIGN_COREPOP_HUMID323_20261114.md`(HKHOME 작성)이고, 이 글은 **처음 붙는 기기가 그 배정에 합류하는 절차**만 적습니다.

## 0. 사용자 지시 (원문 · 랩탑 세션 11-15)
- 15:1x "완전 새로운 로컬 몇대를 추가해야 오늘 내로 계산을 끝낼 수 있지?"
- 15:2x "2대 추가 기준으로 인계하면 너가 .md랑 파일 작성 가능?"

랩탑의 답(같은 세션): 오늘 자정까지 전부 끝내는 것은 대수로 풀리지 않고(구조당 Zeo++ 뒤 GCMC 순서 · 가장 긴 작업 하나가 10 h 를 넘음), 2대를 붙이면 296종의 1차 완주가 11-17 오후에서 **11-16 밤**으로 당겨진다는 견적입니다(묶음 하나가 한 기기에서 15~21 h 걸린 실측에서 냄 · §7).

## 1. 무엇을 하는가
- CoRE 모집단 3D 296종(CORE22 제외)의 323 K 습윤 3성분 흡착점. 32종씩 묶음 b01~b09, b10 은 8종. 조건 · 실행기 · 산출 이름은 `ASSIGN_COREPOP_HUMID323_20261114.md` §1~§3 · §7 그대로입니다.
- 새 기기는 **묶음 하나를 통째로** 맡습니다. 자기 묶음의 Zeo++ 막음 계산과 GCMC 를 둘 다 하고, 다른 기기에 기대는 것이 없습니다.
- 사슬 `corepop_chain.sh` 하나가 순서를 다 합니다: simulate 0 확인 → Zeo++ 96호출 → 막음 ok 구조만 → 스모크 2종(10 사이클) → 본 계산. 실패하면 그 자리에서 멈추고 기록에 적습니다.
- **값 · 평균 · 순위는 읽지도 적지도 않습니다.** 기기는 표지만 적고, 판정은 종합자 몫입니다(배정 §6).

## 2. 기기 조건 — 하나라도 아니면 사용자에게 알리고 멈춥니다
| 조건 | 이유 |
|---|---|
| 사용자 실기기(리눅스 또는 WSL2). 임시 클라우드 샌드박스 아님 | `NEW_MACHINE_20260822.md` 0-1 — 샌드박스는 약 55분에 사라짐 · 묶음 하나는 15 h 이상 |
| 저장소를 WSL ext4 안 `~/mof_project` 에 클론(`/mnt/c` 아래 금지) | 같은 문서 0-0 — NTFS 는 체크아웃이 안 됨 |
| 메모리 16 GB 이상(리눅스가 보는 값) | Zeo++ 호출 하나가 6~14 GB · §7. WSL2 는 기본으로 호스트 RAM 의 일부만 씀 |
| miniconda 가 `~/miniconda3` 에 있고 env 이름이 `czeromof` | `corepop_blocks.py` 가 `~/miniconda3/envs/czeromof/bin/network` 자리만 봄(실행기 무수정) |
| 그 기기에서 `origin master` 에 push 할 수 있음 | 착수 글 · 결과를 master 에 올려야 함. 인증은 사용자가 잡아 줌 |
| 기기 이름: 소문자 · 숫자 · `_` 만, 이미 쓰는 이름(desktop · hkhome · laptop · laptop2 · cloud · junseok · audit · cloud4c) 아님 | 결과 파일 이름과 우편함 이름에 들어감. 예: `pc3` · `pc4` |

WSL 의 메모리 한도를 올리는 것(`.wslconfig`)과 패키지 설치는 **환경 변경**이므로 사용자가 그 기기 세션에 직접 시킨 범위 안에서만 합니다(CLAUDE.md §9 의 30분 규칙 예외 ①).

## 3. 환경 구축 (1~2 h · `NEW_MACHINE_20260822.md` §3 을 이 계산에 맞춰 줄인 것)
```bash
# 3-1 저장소 — 주소와 접근 권한은 NEW_MACHINE_20260822.md §3-1 (비공개 저장소 · 사용자에게 초대 요청)
cd ~/mof_project && git log -1 --format=%h          # master 최신인지

# 3-2 env — raspa2 와 zeopp-lsmo 가 둘 다 필요합니다(랩탑 실측 판: raspa2 2.0.50 · zeopp-lsmo 0.4.7 · python 3.10 · ase 3.29)
conda create -n czeromof -c conda-forge python=3.10 raspa2=2.0.50 zeopp-lsmo=0.4.7 ase=3.29 numpy -y

# 3-3 힘장 — 배포본 그대로는 우리 값이 아닙니다. 저장소 트리를 통째로 복사(물 수정판 Hw none / Lw none 이 이미 들어 있음)
export RASPA_DIR=$HOME/RASPA/simulations
mkdir -p "$RASPA_DIR/share/raspa"
cp -r ~/mof_project/00_Migration/raspa_share/raspa/* "$RASPA_DIR/share/raspa/"
md5sum "$RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def"   # 8e8ec933f9013c7e932da04dc256efd3 이어야 함
```
`RASPA_DIR` 는 사슬을 띄우는 줄에 같이 줍니다(§5 의 명령). `~/.bashrc` 에만 넣으면 `setsid nohup` 으로 띄운 사슬이 못 볼 수 있습니다.

## 4. 착수 전 점검 — `corepop_preflight.sh` (읽기 전용 · RASPA 와 Zeo++ 를 띄우지 않음)
```bash
bash ~/mof_project/21_ZIF69_MTV/corepop_preflight.sh <기기> <묶음>      # 예: pc3 b06
```
- 보는 것: 커널 · 기기 이름 · 저장소 자리 / python · ase · simulate · network / 힘장 md5 8e8ec933 · C_co2 0.6512 · TraPPE 폴더 · 물 5자리 / 실행기와 입력 열 개의 md5 / simulate 0 · network 0 · 메모리 · 디스크(`df /mnt/c`) · origin 읽기 · git 이름 / 그 묶음의 Zeo++ 드라이(zip 대조 32/32).
- `점검 통과` 가 나오면 **그 기기의 메모리와 코어 수로 계산한 명령 두 줄**을 찍어 줍니다. `점검 실패 N` 이면 띄우지 않고 `!!` 줄을 고칩니다.
- Zeo++ 병렬은 `(메모리 전체 GB − 5) ÷ 9` 를 내림한 값(1~4)입니다. 랩탑의 실측에서 정한 것이고(§7), 16 GB 는 1 · 24 GB 는 2 · 32 GB 는 3 이 됩니다. 워커는 논리 코어 전부입니다(배정 §4 · 사용자 지시 "코어 최대로").
- 랩탑에서 시험한 길: 통과(명령 출력) · 힘장 없음 · python 없음 · `/mnt` 아래 저장소 · 이미 쓰는 이름 · 없는 묶음 · network 가 도는 중.

## 5. 묶음을 가져가고 띄우기
1. **지금 누가 무엇을 가져갔는지 master 에서 읽습니다**(`git fetch` 뒤 `git show origin/master:21_ZIF69_MTV/COMMS/<기기>.md | head -40` — desktop 은 최신 글이 **맨 아래**라 `tail`). 11-15 15:30 현재:

   | 묶음 | 상태 |
   |---|---|
   | b01 | 랩탑 완주 31/32 |
   | b02 | laptop2 GCMC 중(30종) |
   | b03 | HKHOME 완주 20/32 · 빠진 12종은 HKHOME 이 뒤에 |
   | b04 | HKHOME Zeo++ 중(11-15 14:44 착수) |
   | b05 | 랩탑 Zeo++ 중(11-15 08:13 착수) |
   | **b06 · b07 · b08 · b09 · b10** | **아직 아무도 안 가져감** |

2. **안 가져간 묶음 가운데 숫자가 가장 작은 것**을 고릅니다(배정 §4 — 예약은 없습니다. 기존 세 기기도 끝나는 대로 같은 규칙으로 가져갑니다).
3. §4 의 점검을 그 묶음으로 돌려 통과시킵니다.
4. **착수 글을 먼저 올립니다**(§6). 올린 직후 `git fetch` 로 다시 읽어, 같은 묶음의 착수 글이 내 것보다 먼저 올라와 있으면 내가 물러나 다음 묶음으로 갑니다(물러난다는 한 줄을 올림).
5. 점검이 찍어 준 두 줄로 띄웁니다. 모양은 이렇습니다.
   ```bash
   mkdir -p ~/.mof_chain && cp ~/mof_project/21_ZIF69_MTV/corepop_chain.sh ~/.mof_chain/
   RASPA_DIR=$HOME/RASPA/simulations setsid nohup bash ~/.mof_chain/corepop_chain.sh <기기> <묶음> <Zeo++ 병렬> <워커> < /dev/null > /dev/null 2>&1 &
   ```
6. 기록은 `~/.mof_chain/corepop_<기기>_<묶음>.chain.log`(단계) · `.zeo.log` · `.smoke.log` · `.gcmc.log`. 띄운 뒤 1분 안에 `chain.log` 에 "simulate 0 — Zeo++ 착수" 가 찍히고 `pgrep -xc network` 가 1 이상인지 봅니다.
7. 묶음이 끝나면 완주 글과 결과 파일을 올리고(§6), 2번으로 돌아가 다음 묶음을 가져갑니다.

> ⚠ **b07 에는 N_super 5,670 짜리 구조가 하나 있습니다**(대상 목록에서 가장 큼 · b06 · b08 · b09 · b10 의 최대는 2,720~3,807). CLAUDE.md §5 에 적힌 대로 이 크기는 예전 계산에서 최장 단일 작업이었습니다. b07 을 맡은 기기는 벽시계가 이 작업 하나로 정해질 수 있습니다.

## 6. 글과 결과 올리기 — `corepop_post.sh` (작업트리를 건드리지 않음)
러너가 도는 기기에서는 `git pull` · `merge` · `checkout` 을 손으로 하지 않습니다(CLAUDE.md §6). 받을 때는 `git fetch` + `git show`, 올릴 때는 이 도구를 씁니다.
```bash
cp ~/mof_project/21_ZIF69_MTV/corepop_post.sh ~/.mof_chain/
POST_DRY=1 bash ~/.mof_chain/corepop_post.sh <기기> <커밋 메시지 파일> <우편함 글 파일> <SESSION_LOG 줄 파일|-> [<원본>=<저장소 경로> ...]   # 먼저 확인
bash ~/.mof_chain/corepop_post.sh <기기> ...                                                                                              # 실제 게시
```
- 우편함 `21_ZIF69_MTV/COMMS/<기기>.md` 가 없으면 도구가 머리말과 함께 만듭니다. 글은 맨 앞에 붙습니다. 자기 우편함만 씁니다(`COMMS.md` ①).
- 글의 머리 모양(다른 기기 글과 같게): `## 2026-MM-DD HH:MM — [COREPOP-H323] **<기기> — <한 줄>**` · `**받는 곳**:` · `**요약**:` · `**답 필요**:` · 그 아래 들여쓴 표지 줄.
- 올리는 때와 내용:

  | 때 | 글에 적는 것 | 같이 올리는 파일 |
  |---|---|---|
  | 착수(띄우기 **전**) | 묶음 · 점검 통과 줄 · 띄울 명령 · 메모리와 코어 수 · 끝 견적과 그 출처 | 없음 |
  | Zeo++ 끝 | 호출 96 중 ok · 가드 kill · 재시도 수 · 빠진 구조 이름 · 고친 견적 | `results_corepop_blocks_<기기>_<묶음>.json` · 비어 있지 않은 `corepop_zeo_runs/**/**.block` |
  | 완주 | 감사 줄 그대로 · 행 수 · 씨앗이 서로 다른지 · 작업 시간 범위와 가장 긴 작업 · 견적과의 차이 | `results_corepop_e_humid3_323_<기기>_<묶음>.json` · `_audit.json` |
  | 멈춤 | `chain.log` 의 멈춘 줄 그대로 | 없음 |

- 실행 폴더(`humid_wc_runs_v3w_323/corepop_e3_323_<기기>_<묶음>/` · `corepop_zeo_runs/`)는 지우지 않습니다.
- 커밋 메시지 끝에는 그 세션의 `Co-Authored-By` 줄을 붙입니다.

## 7. 먼저 돈 기기가 잰 것 — 견적과 함정 (출처: 랩탑 b01 · b05, HKHOME b03, laptop2 b02 의 우편함 글)
- **묶음 하나의 벽시계는 15~21 h** 였습니다. 랩탑 b01 14.6 h(Zeo++ 3.7 h + GCMC 10.9 h) · HKHOME b03 은 20종만으로 19.7 h · laptop2 b02 는 Zeo++ 만 7.7 h. 기기도 구조도 다르므로 새 기기의 견적은 이 범위를 옮긴 값이라고 착수 글에 적습니다.
- **Zeo++ 는 메모리가 정합니다.** 호출 하나의 최대 RSS 가 b01 은 6~7 GB, b05 는 8~14 GB 였고, 단독으로도 17.9 GB 를 넘겨 가드에 죽는 구조가 묶음마다 한둘 있습니다(랩탑 24 GB · 가드는 여유 5,000 MB 미만이면 kill). 랩탑이 24 GB 에서 병렬 3 으로 돌렸더니 b05 의 96호출 중 43호출이 가드에 죽었고, 사슬이 그것을 한 번에 하나로 다시 도는 여러 시간 동안(11:50 무렵부터 · 15:10 에 22호출이 남음) **코어 15개가 놀았습니다**(Zeo++ 가 도는 동안은 RASPA 를 못 띄움). 병렬을 욕심내면 오히려 늦어집니다.
- **가드에 죽은 구조는 사슬이 빼고 갑니다.** 재시도에서도 죽은 구조는 막음 파일이 없어 본 계산에서 빠집니다. 고치려 들지 말고 Zeo++ 끝 글에 이름을 적습니다. 처리는 종합자 몫입니다.
- **GCMC 의 끝은 가장 긴 작업 하나가 정합니다.** b01 은 30작업이 9.5 h 에 끝났는데 한 작업이 10.9 h 였습니다(작업합 102.8 h ÷ 워커 16 = 6.4 h 보다 김). 견적은 `max(가장 긴 작업, 작업합 ÷ 워커)` 로 내고 어느 쪽인지 적습니다(CLAUDE.md §5).
- **`.gcmc.log` 의 작업별 줄은 끝에서 한꺼번에 찍힙니다.** 도는 중에 그 줄을 세면 끝까지 0 입니다(랩탑이 여기에 대기 장치를 걸었다가 한 번도 안 울림). 진행은 실행 폴더의 출력에서 `Simulation finished` 를 세어 봅니다:
  `grep -l 'Simulation finished' ~/mof_project/21_ZIF69_MTV/humid_wc_runs_v3w_323/corepop_e3_323_<기기>_<묶음>/runs/*/Output/System_0/*.data | wc -l`
- **출력 파일이 몇 시간째 그대로여도 멈춘 것이 아닙니다**(CLAUDE.md §4). 죽었는지는 `pgrep -xc simulate` 와 사슬 PID 로 봅니다.

## 8. 하지 않는 것
- 실행기 · 사슬 · 대상 목록을 고치지 않습니다. 사이클(5,000 + 15,000) · 힘장 · 컷오프 · Ewald · 물 모델은 CLAUDE.md §1 의 고정값입니다.
- 끊긴 실행을 이어받지 않습니다. 사슬이 멈췄으면 멈춘 줄을 올리고, 다시 띄울 때는 그 묶음의 결과 파일과 폴더가 왜 남았는지부터 적습니다(CLAUDE.md §3).
- Zeo++ 가 도는 동안 RASPA 를, RASPA 가 도는 동안 Zeo++ 를 손으로 띄우지 않습니다(CLAUDE.md §5).
- 죽일 일이 있으면 `ps -eo pid,args` 로 PID 를 보고 PID 로 죽입니다. `pkill -f` 를 쓰지 않습니다(CLAUDE.md §4).
- 다른 기기의 우편함 · 결과 파일 · 실행 폴더를 건드리지 않습니다.
- 스모크 값(10 사이클)과 본 계산 값을 글에 옮기지 않습니다.

## 9. 새 기기 세션에 붙여 넣을 한 줄
```
CLAUDE.md, 21_ZIF69_MTV/HANDOVER_COREPOP_NEWMACHINE_20261115.md, 21_ZIF69_MTV/ASSIGN_COREPOP_HUMID323_20261114.md 를 읽고, 이 기기 이름은 <pc3 또는 pc4> 로 해서 §2 조건 확인 → §3 환경 구축 → §4 점검 → §5 대로 안 가져간 가장 작은 묶음을 착수 글로 가져가 띄워 줘
```

## 10. 이 글과 함께 올린 파일
| 파일 | md5(앞 8자리) | 무엇 |
|---|---|---|
| `corepop_preflight.sh` | 13a6dd41 | §4 점검(읽기 전용) |
| `corepop_post.sh` | 101672d3 | §6 게시 도구(임시 인덱스 + commit-tree + push) |

둘 다 랩탑에서 통과하는 길과 실패하는 길을 모두 돌려 보았고(게시 도구는 `POST_DRY=1` 로), **처음 붙는 기기에서 실제로 돌려 본 적은 없습니다.** 새 기기에서 이 글과 다르게 움직이는 곳이 있으면 그 기기 우편함에 적어 주십시오.
