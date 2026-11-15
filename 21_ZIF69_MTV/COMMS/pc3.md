## 2026-11-15 21:52 — [COREPOP-H323] **pc3 — 착수 글: b06 ~ b10 의 가벼운 구조 31종(분할표 06e0ffb5 그대로 · 잰 한도 6.1 GB · 내려놓는 구조 없음)** · 메모리 16 GB 새 기기 첫 글 · 이 글 바로 뒤에 띄웁니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc4 · 사용자
**요약**: 16 GB 글(`HANDOVER_COREPOP_16GB_20261115.md`) §2 ~ §5 대로 이 기기를 갖추고 점검했습니다. 점검의 실패는 그 글 §4 가 허용한 "메모리 전체 12 GB" 한 줄뿐이고, 비었을 때 잰 한도가 6.0 GB 이상이라 분할표의 `keys` 31종을 그대로 가져갑니다. 다른 기기의 무거운 구조 몫과는 겹치지 않습니다. 사슬 · 래퍼 · 실행기 · 분할표는 손대지 않았습니다. COMMS.md ⑦-4 에 따라 WSL 을 붙잡는 예약 작업을 사용자 승인으로 걸었습니다. 값은 읽지 않습니다.
**답 필요**: 아니오(이 기기에서 다르게 움직이면 이 우편함에 적겠습니다)

    기기    pc3 · 윈도우 11 데스크톱(배터리 없음 · AC 절전 안 함) · AMD Ryzen 5 5600X 물리 6 · 논리 12 · 호스트 RAM 15.9 GB · C: 여유 689 GB
            WSL2 Ubuntu 24.04(오늘 새로 설치) · .wslconfig memory=12GB · swap=8GB(16 GB 글 §2 그대로 · 착수 전에 이미 맞춰져 있었음) · free -g total 11 · nproc 12
    env     ~/miniconda3 = Miniforge 26.9.4-2(Miniconda 대신 · 사용자 선택 · 채널 conda-forge 만) · czeromof: python 3.10.22 · raspa2 2.0.50 · zeopp-lsmo 0.4.7 · ase 3.29.0 · numpy 2.2.6
            힘장 트리 00_Migration/raspa_share/raspa 통째 복사 · force_field_mixing_rules.def 8e8ec933
    계정    Claude Code 사용자 계정 · GitHub 은 Czero_mtv_mof 하나 · Contents 읽기/쓰기 fine-grained 토큰(사용자가 만들어 직접 넣음) · git 이름은 다른 기기와 같음
    점검    corepop_preflight.sh pc3 b06(13a6dd41): 점검 실패 1 = "!! 메모리 전체 12 GB …" 한 줄(16 GB 글 §4 의 허용 줄) · 그 밖의 [1]~[6] 전부 ok · b06 Zeo++ 드라이 32/32 · 계획 96건
    한도    simulate 0 · network 0 에서 MemAvailable − 5 = 6.08(21:2x) · 6.111 ~ 6.115 GB(21:3x 세 번) → 내림 6.0 ~ 6.1 ≥ 6.0 → 분할표 그대로 · 내려놓는 구조 없음
    키 파일 corepop_light_keys_b06_b07_b08_b09_b10.json 06e0ffb5 · keys 31(b06 5 · b07 8 · b08 7 · b09 10 · b10 1) · 분할표 예측 최대의 최댓값 4.02 GB · 새로 만든 키 파일 없음
    파일    corepop_chain_keys.sh e5f65f5a · corepop_blocks_keys.py c2a71d4c · corepop_blocks.py c00cd11a · corepop_light_keys.py e2bdd36c · corepop_humid323_targets.json f0cbc615 · corepop_post.sh 101672d3 (master fc5f4ae3 와 같음 · 무수정)
    드라이  래퍼 COREPOP_ZEO_DRY=1: 입력 대조 통과 · zip 524개 중 대상 31/31 · 묶음 b06 · b07 · b08 · b09 · b10 · 원자 수 = NAtoms(50 ~ 192) · 계획 93호출 · 병렬 1 · rc 0
            래퍼 머리줄은 "무거운 구조 31" 로 찍힘 — 16 GB 글 §5-4 ⚠ 의 고정 꼬리표
    가져감  21:35 origin/master fc5f4ae3 에서 b06 ~ b10 의 가벼운 · 무거운 착수 글 없음. laptop2 의 b06 무거운 자동 착수와 pc4(무거운 쪽)는 이 31종과 겹치지 않음
    폴더    31종의 corepop_zeo_runs/<파일 이름>/ 없음 · results_corepop_*pc3* 없음 · humid_wc_runs_v3w_323/corepop_e3_323_pc3_* 없음 · ~/.mof_chain/corepop_pc3_heavy.* 없음
    WSL     COMMS.md ⑦-4: 예약 작업 ClaudeWslHold(사용자 승인 11-15 21:3x) · 저장소 00_Migration/tools/wsl_hold.ps1 4d675522 무수정 사본 + 이 기기 경로 실행기(CLAUDE_WSL_DIST=Ubuntu-24.04) · make_task.ps1 과 같은 설정(로그온 + 5분 · IgnoreNew · PT0S)
            21:34:50 "hold loop started" · WSL 안 sleep infinity 붙음 · 계산이 끝나면 예약 작업을 지웁니다
    커밋    호스트 커밋 착수 전 11.6/26.4 GB(44 %) · 16 GB 글 §6 대로 몇 시간마다 봅니다
    명령    mkdir -p ~/.mof_chain && cp ~/mof_project/21_ZIF69_MTV/corepop_chain_keys.sh ~/.mof_chain/
            RASPA_DIR=$HOME/RASPA/simulations REPO=$HOME/mof_project setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh pc3 corepop_light_keys_b06_b07_b08_b09_b10.json 1 12 < /dev/null > /dev/null 2>&1 &
    기록    ~/.mof_chain/corepop_pc3_heavy.{chain,zeo,smoke,gcmc}.log(꼬리표 heavy 는 고정 · 16 GB 글 §5-4)
    산출    results_corepop_blocks_pc3_b06_b07_b08_b09_b10_heavy.json · results_corepop_e_humid3_323_pc3_b06_b07_b08_b09_b10.json + _audit.json
    견적    Zeo++ 93호출 직렬 3.5 ~ 4.5 h — 16 GB 글 §7(HKHOME b04 · 3 GB 안팎 호출 135 ~ 150 s · 병렬 2 · 다른 기기에서 옮긴 값)
            GCMC 31작업 · 워커 12(3물결) — HKHOME b03 작업 0.68 ~ 14.01 h(중앙 2.27 · 16워커 · 다른 기기 · 다른 구조)에서 옮김. 작업합 약 31 × 2.27 ≈ 70 h ÷ 12 ≈ 5.9 h < 최장 작업 → 가장 긴 작업 하나가 정할 공산 · 10 ~ 15 h
            합 15 ~ 20 h → 끝 11-16 13시 ~ 18시. 이 기기(5600X)의 속도 자료는 없어 범위는 옮긴 값입니다

---

# pc3 우편함 — pc3 만 씁니다

이 파일은 **pc3 만** 씁니다. 규약은 `21_ZIF69_MTV/COMMS.md`. 최신 글이 위에 옵니다.
