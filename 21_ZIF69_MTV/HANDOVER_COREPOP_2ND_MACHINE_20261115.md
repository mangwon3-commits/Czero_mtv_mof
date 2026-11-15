# COREPOP-H323 — 두 번째 새 기기(예전에 지인 도움 계산을 한 기기): 남은 묶음의 "무거운 구조" 를 맡는 법

2026-11-15 20:48 KST · laptop2(Balthasar) 작성 · 사용자 지시. 값은 읽지 않음. 계산의 정의(`ASSIGN_COREPOP_HUMID323_20261114.md`)와 배정 §4-보완(b06 ~ b10 은 가벼운 구조 / 무거운 구조로 나눔)은 그대로입니다. 환경 구축 · 글 올리기 · 함정은 `HANDOVER_COREPOP_NEWMACHINE_20261115.md`(아래 "새 기기 글")를, 계정과 호스트 커밋 감시는 `HANDOVER_COREPOP_16GB_20261115.md`(아래 "16 GB 글")를 따릅니다. **이 글은 이 기기에서 달라지는 것만** 덮어씁니다.

## 0. 사용자 지시 (원문 · laptop2 세션 11-15)
- "나머지 한 대도 가능하다 응답 옴. 두번째 .md써."
- "그쪽은 좀 더 스펙이 좋을거임. 이전에 지인 도움 계산이었어"

## 1. 이 기기가 맡는 몫 — 무거운 구조
- 16 GB 기기(pc3)는 b06 ~ b10 의 가벼운 구조 31종을 맡습니다(16 GB 글 §5). 남은 무거운 구조 105종은 메모리가 큰 기기의 몫입니다. 이 기기는 사양이 더 좋다고 하므로 무거운 구조 쪽에 섭니다.
- 무거운 구조가 어려운 까닭은 Zeo++ 막음 호출의 메모리입니다. 호출 하나의 최대 RSS 는 단위셀 부피로 정해지고(16 GB 글 §1-2), 가드는 가용 메모리가 5 GB 아래로 내려가면 그 호출을 kill 합니다. 그래서 **호출 하나의 한도는 비었을 때의 MemAvailable − 5 GB** 이고, 이 한도를 넘는 구조는 가드에 걸려 결과에서 빠집니다.
- 분할표(`corepop_light_keys_b06_b07_b08_b09_b10.json` · 06e0ffb5)의 예측 최대(`pred_peak_GB`)로 보면, 한도가 클수록 빠지는 구조가 줄어듭니다.

  | 묶음 | 무거운 구조 | 예측 최대 가운데값 | 예측 최대의 최댓값 | 10 GB 초과 | 14 GB 초과 | 17 GB 초과 |
  |---|---|---|---|---|---|---|
  | b06 | 27 | 8.2 GB | 12.9 GB | 1 | 0 | 0 |
  | b07 | 24 | 8.0 GB | 15.3 GB | 6 | 2 | 0 |
  | b08 | 25 | 8.1 GB | 19.7 GB | 8 | 2 | 1 |
  | b09 | 22 | 8.6 GB | 27.3 GB | 10 | 8 | 3 |
  | b10 | 7 | 12.8 GB | 22.1 GB | 4 | 3 | 2 |

  - 이 수는 예측이 가운데값일 때입니다. 실측은 예측의 1.46배까지 나왔습니다(16 GB 글 §1-2). 그래서 한도에 가까운 구조도 빠질 수 있습니다.
- 그래서 **한도가 10.0 GB 이상이면 이 글대로** 무거운 묶음을 가져갑니다. 10.0 GB 미만이면 착수하지 않고 사용자에게 잰 값을 알립니다. 가벼운 31종은 pc3 몫이므로, 이 기기가 그것을 나눠 맡으려면 사용자 결정이 필요합니다.
- **11-15 20:48 현재 무거운 묶음의 상태**입니다.

  | 묶음 | 상태 |
  |---|---|
  | b03 · b04 무거운 구조 | 랩탑이 b05 뒤에 줄 세움(laptop 11-15 19:14 글) |
  | b06 무거운 27종 | laptop2 가 b02 사슬이 끝나면 착수 글을 먼저 올리고 띄우도록 걸어 둠(11-16 새벽 ~ 아침 예상) |
  | **b07 · b08 · b09 · b10 무거운 구조** | **아직 아무도 안 가져감** |

## 2. 먼저 확인할 것 — 이 기기의 예전 기록
- 사용자가 "이전에 지인 도움 계산" 이라고 한 기기는 저장소 기록으로는 `COMMS/junseok.md` 의 기기로 보입니다. 그 우편함의 08-29 06:30 글에 따르면 호스트 RAM 31.5 GB · WSL 24 GB · 물리 6코어였습니다. 09-05 배정(`ASSIGN_20260905.md`)에는 자격증명 때문에 "정지" 로 적혀 있습니다.
- 그래서 시작하기 전에 `nproc` · `free -g` · `~/mof_project` 의 마지막 커밋(`git -C ~/mof_project log -1 --format='%h %cd'`)으로 이 기록이 이 기기의 것인지 확인합니다. 기록과 다르면 잰 값을 기준으로 삼고, 착수 글에 다르다고 적습니다.
- **기기 이름은 `pc4`** 로 합니다. 점검 도구(`corepop_preflight.sh`)가 `junseok` 을 이미 쓰는 이름으로 거부하기 때문입니다. 결과 파일과 우편함은 `pc4` 이름으로 새로 만들어지고(`COMMS/pc4.md`), `junseok.md` 와 예전 결과 파일은 건드리지 않습니다.

## 3. 설정 · 계정 · 저장소 (환경 변경 · 사용자가 이 기기 세션에 직접 시킨 범위에서만 · CLAUDE.md §9 예외 ①)
- **WSL 메모리**: 24 GB 그대로 둡니다. 예전 기록의 `set_wsl_ram.ps1 -GB 26` 으로 올리지 않습니다. 26 GB 면 윈도우 몫이 5.5 GB 로 줄어, HKHOME 의 WSL 을 죽인 호스트 커밋 문제(16 GB 글 §1-3)에 가까워집니다. 호스트 RAM 이 기록과 다르면 WSL 은 호스트 RAM − 8 GB 이하로 둡니다.
- **페이지 파일 · 디스크 · 계산 중 다른 프로그램**: 16 GB 글 §2 그대로입니다.
- **계정**: 16 GB 글 §3 그대로입니다. Claude Code 는 사용자 계정으로 로그인하고, GitHub push 는 저장소 `Czero_mtv_mof` 하나에만 쓰기 권한이 있는 fine-grained 토큰(만료 14 일 이내)으로 넣습니다. 사용자 기기가 아니므로 계산이 끝나면 Claude Code 를 로그아웃하고 토큰을 지웁니다.
- **저장소**: 예전 클론이 `~/mof_project` 에 있으면 고쳐 쓰지 않고 자리를 비켜 둡니다. 예전 클론에는 그때의 래퍼와 바뀐 파일이 남아 있을 수 있어, 그 위에 master 를 받으면 무엇이 무수정인지 가리기 어렵기 때문입니다.

      mv ~/mof_project ~/mof_project_old_20261115      # 지우지 않고 이름만 바꿈

  그다음 새 기기 글 §3-1 대로 `~/mof_project` 에 새로 클론합니다(WSL ext4 안 · `/mnt/c` 아래 금지).
- **env**: `~/miniconda3/envs/czeromof` 가 이미 있으면 먼저 판을 봅니다.

      ~/miniconda3/bin/conda list -n czeromof | grep -E '^(raspa2|zeopp-lsmo|python|ase) '

  새 기기 글 §3-2 의 판(raspa2 2.0.50 · zeopp-lsmo 0.4.7 · python 3.10 · ase 3.29)과 다르면 그 절대로 맞춥니다.
- **힘장**: 예전 트리를 쓰지 않고 새 기기 글 §3-3 대로 새 클론의 트리를 통째로 복사합니다(md5 8e8ec933). 물 수정판(Hw none / Lw none)이 들어간 판이어야 하기 때문입니다.

## 4. 점검
- `bash ~/mof_project/21_ZIF69_MTV/corepop_preflight.sh pc4 <묶음>` 의 모든 줄이 통과해야 합니다. 16 GB 기기와 달리 "메모리 전체 14 GB 이상" 줄도 통과해야 합니다.
- 점검 도구가 마지막에 찍어 주는 띄우기 명령은 묶음 통째 사슬(`corepop_chain.sh`)입니다. **이 명령은 쓰지 않습니다.** 통째로 돌리면 pc3 몫인 가벼운 구조가 두 번 돌아, 읽기 스크립트가 "같은 구조가 두 번" 으로 멈춥니다(16 GB 글 §5). 띄우는 명령은 §5 의 것을 씁니다.

## 5. 가져가고 띄우기
1. **한도를 잽니다.** 아무것도 안 돌 때(simulate 0 · network 0) 잽니다.

       awk '/^MemAvailable:/{printf "%.1f\n", $2/1048576 - 5}' /proc/meminfo

   10.0 이상이어야 합니다(§1).
2. **누가 무엇을 가져갔는지 master 에서 읽습니다.** 방법은 새 기기 글 §5-1 이고, 무거운 구조의 착수 글은 이렇게 찾습니다.

       cd ~/mof_project && git fetch -q origin
       for f in $(git ls-tree --name-only origin/master 21_ZIF69_MTV/COMMS/ | grep '\.md$'); do git show origin/master:$f | grep '^## \|^> \*\*\[' | grep 'COREPOP' | grep '무거운' | grep 'b0[6-9]\|b10'; done

   무거운 구조를 안 가져간 묶음 가운데 **숫자가 가장 작은 것**을 고릅니다(배정 §4 · §4-보완). laptop2 가 b06 착수 글을 아직 안 올렸다면 b06 도 고를 수 있습니다. 규칙은 착수 글을 먼저 올린 기기가 맡는 것이고, laptop2 의 자동 착수는 다른 착수 글이 보이면 멈추게 되어 있습니다.
3. **키 파일을 뽑습니다.** 16 GB 글 §5 끝의 한 줄을 그 묶음으로 돌립니다(예: b07 → 24종). 결과는 `21_ZIF69_MTV/corepop_rest_keys_<묶음>.json` 입니다.
4. **래퍼 드라이로 입력을 대조합니다.**

       cd ~/mof_project/21_ZIF69_MTV
       COREPOP_MACHINE=pc4 COREPOP_KEYS_FILE=corepop_rest_keys_<묶음>.json COREPOP_ZEO_PAR=1 COREPOP_ZEO_DRY=1 ~/miniconda3/envs/czeromof/bin/python -B -u corepop_blocks_keys.py

   "입력 대조 통과" 줄이 나와야 합니다.
5. **착수 글을 먼저 올립니다**(새 기기 글 §6 의 `corepop_post.sh`).
   - 글에 적는 것: "<묶음> 무거운 구조 N종 · 분할표 06e0ffb5", 키 파일 이름과 md5, 잰 한도, 분할표 예측 최대가 그 한도를 넘는 구조 수, Zeo++ 병렬 1 · 워커 수, §2 에서 확인한 이 기기의 사양.
   - 키 파일 `corepop_rest_keys_<묶음>.json` 을 같이 올립니다.
   - 올린 직후 다시 `git fetch` 로 읽습니다. 같은 묶음의 무거운 구조 착수 글이 내 것보다 먼저 올라와 있으면, 물러난다는 한 줄을 올리고 다음 묶음으로 갑니다.
6. **띄웁니다.**

       mkdir -p ~/.mof_chain && cp ~/mof_project/21_ZIF69_MTV/corepop_chain_keys.sh ~/.mof_chain/
       cd ~/mof_project/21_ZIF69_MTV && RASPA_DIR=$HOME/RASPA/simulations REPO=$HOME/mof_project setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh pc4 corepop_rest_keys_<묶음>.json 1 $(nproc) < /dev/null > /dev/null 2>&1 &

   - **Zeo++ 병렬은 1** 입니다. 래퍼 `corepop_blocks_keys.py` 의 머리말이 무거운 구조에는 병렬 1 을 권합니다. 무거운 호출 둘이 함께 돌면 옆 호출까지 가드에 걸립니다.
   - 워커는 논리 코어 전부입니다.
   - 사슬의 순서는 simulate 0 · network 0 → Zeo++(래퍼 c2a71d4c · 원판 `corepop_blocks.py` c00cd11a 무수정 import) → 세 탐침 ok 구조만 → 스모크 2종 → 본 계산입니다. 띄운 뒤 1분 안에 `chain.log` 에 "simulate 0 · network 0 — Zeo++ 착수" 가 찍히는지 봅니다.
   - 기록은 `~/.mof_chain/corepop_pc4_heavy.{chain,zeo,smoke,gcmc}.log` 입니다. 이 이름에는 묶음이 들어가지 않으므로, **두 번째 묶음을 띄우기 전에 앞 묶음의 기록 넷을 `corepop_pc4_heavy_<앞 묶음>.*.log` 로 옮겨 둡니다.** `chain.log` 는 이어 쓰이고 나머지 셋은 덮어쓰이기 때문입니다.
7. **산출**은 `results_corepop_blocks_pc4_<묶음>_heavy.json` · `results_corepop_e_humid3_323_pc4_<묶음>.json` + `_audit.json` 입니다. 실행 폴더는 `humid_wc_runs_v3w_323/corepop_e3_323_pc4_<묶음>/` 입니다.
8. **끝나면** 완주 글(표지만)과 결과 파일을 올리고(새 기기 글 §6), 2번으로 돌아가 다음 무거운 묶음을 가져갑니다. 가드에 걸려 빠진 구조는 Zeo++ 끝 글과 완주 글에 이름을 적습니다. 그 구조의 처리는 종합자 몫입니다.

## 6. 도는 동안 볼 것
- **호스트 커밋**: 16 GB 글 §6 그대로입니다(80 % 를 넘으면 윈도우 쪽 프로그램을 닫고, 90 % 에 가까우면 사용자에게 알립니다. 사슬은 죽이지 않습니다). 이 기기는 Zeo++ 호출 하나가 17 GB 안팎까지 갈 수 있으므로, Zeo++ 단계 동안은 1시간마다 봅니다.
- **진행 세기**: 새 기기 글 §7 대로 실행 폴더의 `Simulation finished` 를 셉니다. `.gcmc.log` 의 작업 줄은 끝에서만 찍힙니다.

## 7. 견적 (출처 같이 · 다른 기기에서 옮긴 값)
- **Zeo++**: 무거운 묶음 하나는 22 ~ 27종 × 탐침 3 = 66 ~ 81호출을 하나씩 돌립니다(b10 은 21호출). 랩탑 b05 의 직렬 재시도는 무거운 호출 43개가 약 6.7 h, 곧 호출당 약 9분이었습니다(laptop 11-15 15:12 · 18:36 글). 그래서 **약 10 ~ 13 h** 로 봅니다.
- **GCMC**: 막음 ok 구조 수만큼 돕니다. 같은 6코어 12스레드인 laptop2 b02 에서는 워커 12 로 2.8 ~ 7.5 h 에 끝난 작업 외에 19 h 넘게 도는 작업이 다섯 있었습니다(laptop2 의 11-15 20:27 실측 · 시간만 셈). 무거운 구조는 셀이 커서 더 길 공산이 큽니다. 그래서 끝은 가장 긴 작업 하나가 정하며 **15 ~ 25 h** 로 봅니다.
- **합**: 묶음 하나 약 25 ~ 38 h 입니다. b07 의 가장 큰 셀(2021[Cu][pcu]3[FSR]3 · 9,405 Å³)은 무거운 쪽이라 b07 을 맡으면 그 작업이 끝을 정할 수 있습니다(새 기기 글 §5 의 ⚠).

## 8. 하지 않는 것 (새 기기 글 §8 · 16 GB 글 §8 에 더해)
- 분할표의 `keys`(가벼운 구조)를 이 기기에서 돌리지 않습니다. pc3 몫입니다.
- `corepop_chain.sh` 로 묶음을 통째로 돌리지 않습니다.
- WSL 메모리를 26 GB 이상으로 올리지 않고, `ZEO_GUARD_MB` · `COREPOP_START_MB` 를 낮추지 않으며, Zeo++ 병렬을 2 이상으로 하지 않습니다.
- 예전 클론(`~/mof_project_old_20261115`) · 예전 결과 · `COMMS/junseok.md` 를 지우거나 고치지 않습니다.
- 점검 도구 · 사슬 · 래퍼 · 실행기 · 분할표를 고치지 않습니다.

## 9. 이 기기 세션에 붙여 넣을 한 줄
```
CLAUDE.md, 21_ZIF69_MTV/HANDOVER_COREPOP_2ND_MACHINE_20261115.md, 21_ZIF69_MTV/HANDOVER_COREPOP_16GB_20261115.md, 21_ZIF69_MTV/HANDOVER_COREPOP_NEWMACHINE_20261115.md, 21_ZIF69_MTV/ASSIGN_COREPOP_HUMID323_20261114.md 를 읽고, 이 기기 이름은 pc4 로 해서 2번째 기기 글 §2 확인 → §3 설정·계정·저장소 → §4 점검 → §5 대로 한도를 재고 무거운 구조를 안 가져간 가장 작은 묶음을 착수 글로 가져가 띄워 줘
```

## 10. 이 글이 기대는 파일과 시험
| 파일 | md5 | 무엇 |
|---|---|---|
| `corepop_light_keys_b06_b07_b08_b09_b10.json` | 06e0ffb5 | 분할표(HKHOME 11-15 18:10 · 한도 6.0 GB · 가벼움 31 · 무거움 105) |
| `corepop_chain_keys.sh` · `corepop_blocks_keys.py` | e5f65f5a · c2a71d4c | 키 파일 사슬 · 래퍼 |
| `corepop_preflight.sh` · `corepop_post.sh` | 13a6dd41 · 101672d3 | 점검 · 게시(랩탑) |

- laptop2 에서 한 것: 분할표에서 묶음별 무거운 구조 수와 예측 최대를 셌습니다(§1 의 표). b07 무거운 키 파일(24종)도 뽑아 보았습니다.
- **안 해 본 것**: 래퍼 드라이입니다. 래퍼가 자기 폴더의 대상 목록을 읽는데, laptop2 의 저장소에는 b02 가 도는 동안 경로 지정 checkout 을 하지 않는 규칙 때문에 래퍼가 아직 없습니다. 래퍼 드라이는 HKHOME 과 랩탑이 키 파일로 통과시켰습니다(16 GB 글 §10 · `HANDOVER_COREPOP_HEAVY_LAPTOP_20261115.md` §4). 이 기기에서 다르게 움직이면 `COMMS/pc4.md` 에 적어 주십시오.
