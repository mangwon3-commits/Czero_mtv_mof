## 2026-11-15 22:45 — [COREPOP-H323] **pc4 — 착수 글: b06 무거운 구조 27종 · 분할표 06e0ffb5(키 파일 corepop_rest_keys_b06.json a2bf9a38) · 잰 한도 9.3 GB — 2번째 기기 글 §1 의 10.0 GB 미만이나 사용자 승인으로 착수** · 두 번째 새 기기 첫 글 · 이 글 바로 뒤에 띄웁니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · 사용자
**요약**: 2번째 기기 글(`HANDOVER_COREPOP_2ND_MACHINE_20261115.md`) §2 ~ §5 대로 이 기기를 갖추고 점검했습니다. 점검은 [1] ~ [6] 전부 ok 입니다. 무거운 구조 착수 글이 b06 ~ b10 어디에도 없어(laptop2 의 b06 착수 글도 없음) 가장 작은 b06 의 무거운 27종을 가져갑니다. **laptop2 는 b06 자동 착수를 이 글을 보고 멈춰 주십시오**(2번째 기기 글 §5-2). 잰 한도 9.3 GB 는 §1 의 10.0 GB 에 못 미칩니다. 사용자에게 알렸고, 사용자가 "9.3 GB 그대로 b06 착수" 를 골랐습니다(22:3x). 분할표 예측 최대가 9.3 GB 를 넘는 구조는 27종 중 2종이고, 가드에 걸려 빠지는 구조는 Zeo++ 끝 글에 이름을 적습니다. ⚠ COMMS.md ⑦-4: 이 기기에는 WSL 을 붙잡는 예약 작업도 .wslconfig 도 없습니다. 사용자에게 알렸고, 사용자가 "창을 열어 둔 채 착수" 를 골랐습니다 — **창이 닫히면 계산이 사라질 수 있는 🔴 상태**입니다. 사슬 · 래퍼 · 실행기 · 분할표는 손대지 않았습니다. 값은 읽지 않습니다.
**답 필요**: 아니오(laptop2 는 b06 자동 착수 중지 · 이 기기에서 다르게 움직이면 이 우편함에 적겠습니다)

    기기    pc4 · 윈도우 데스크톱(배터리 없음) · Intel i7-14700F 물리 20(P 8 · E 12) · 논리 28 · 호스트 RAM 31.7 GB · C: 여유 127 GB
            WSL2 Ubuntu 22.04 · .wslconfig 없음(WSL 기본 = 호스트의 절반) · free -m total 15,844 · nproc 28 · WSL 메모리는 올리지 않음(2번째 기기 글 §3 · 사용자 선택)
    §2      COMMS/junseok.md 의 기기(물리 6 · WSL 24 GB)와 다릅니다: ~/mof_project 없음(예전 클론 없음 → 옮길 것 없음) · 물리 20코어 · WSL 15.5 GB. 호스트 RAM 31.5 GB 만 기록과 비슷. 잰 값을 기준으로 삼습니다
    env     ~/miniconda3(conda 26.1.1) · czeromof 새로 만듦: python 3.10.22 · raspa2 2.0.50 · zeopp-lsmo 0.4.7 · ase 3.29.0(conda-forge)
            힘장 00_Migration/raspa_share/raspa 통째 복사 · force_field_mixing_rules.def 8e8ec933
    계정    Claude Code 사용자 계정 · GitHub fine-grained 토큰(사용자가 줌 · 디스크에 저장하지 않고 명령마다 헤더로만 넘김) · git 이름은 다른 기기와 같음(저장소 로컬 설정)
            ⚠ 토큰이 Czero_mtv_mof 외에 저장소 하나를 더 읽을 수 있습니다(16 GB 글 §3 의 "저장소 하나" 조건과 다름 · 사용자에게 알림)
    점검    corepop_preflight.sh pc4 b06(13a6dd41): 점검 통과 · [1] ~ [6] 전부 ok · "메모리 전체 15 GB · 여유 14 GB" 줄 ok · b06 Zeo++ 드라이 32/32 · 계획 96건
            도구가 찍어 준 통째 사슬 명령(corepop_chain.sh)은 쓰지 않습니다(2번째 기기 글 §4)
    한도    simulate 0 · network 0 에서 MemAvailable − 5 = 9.3 GB(22:1x) · 9.30 GB(22:37) → §1 기준 10.0 미만 · 사용자 승인으로 착수
            분할표 pred_peak_GB(b06 무거운 27종): 가운데값 8.25 · 최댓값 12.94 · 9.3 초과 2종(2018[Zn][pcu]3[ASR]3 12.94 · 2021[Zn][scu]3[ASR]1 9.98) · ×1.46 로 보면 18종이 9.3 초과 가능
    키 파일 corepop_rest_keys_b06.json a2bf9a38 · 27종 · 16 GB 글 §5 끝의 한 줄 그대로 뽑음(분할표 06e0ffb5 · light False · batch b06) · 이 글과 같이 올림
    파일    corepop_chain_keys.sh e5f65f5a · corepop_blocks_keys.py c2a71d4c · corepop_blocks.py c00cd11a · corepop_light_keys_b06_b07_b08_b09_b10.json 06e0ffb5 · corepop_post.sh 101672d3 (master 62dad1e4 와 같음 · 무수정)
    드라이  래퍼 COREPOP_ZEO_DRY=1: 입력 대조 통과 · zip 524개 중 대상 27/27 · 묶음 b06 · 원자 수 = NAtoms(176 ~ 384) · 계획 81건 · 병렬 1
    가져감  22:3x origin/master 62dad1e4 에서 b06 ~ b10 의 무거운 착수 글 없음(2번째 기기 글 §5-2 의 grep) · pc3 의 가벼운 31종과는 겹치지 않음
    폴더    27종의 corepop_zeo_runs/<파일 이름>/ 없음 · results_corepop_*pc4* 없음 · humid_wc_runs_v3w_323/corepop_e3_323_pc4_b06 없음 · ~/.mof_chain/corepop_pc4_heavy.* 없음
    WSL     COMMS.md ⑦-4 🔴: 예약 작업 없음 · vmIdleTimeout 설정 없음 · 대화형 창(Claude Code)만 붙잡음 · 사용자 선택 "창을 열어 둔 채 착수"
    커밋    호스트 커밋 착수 전 33.1/58.7 GB(56 %) · Zeo++ 단계 동안 1시간마다 봅니다(2번째 기기 글 §6)
    명령    mkdir -p ~/.mof_chain && cp ~/mof_project/21_ZIF69_MTV/corepop_chain_keys.sh ~/.mof_chain/
            cd ~/mof_project/21_ZIF69_MTV && RASPA_DIR=$HOME/RASPA/simulations REPO=$HOME/mof_project setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh pc4 corepop_rest_keys_b06.json 1 28 < /dev/null > /dev/null 2>&1 &
    기록    ~/.mof_chain/corepop_pc4_heavy.{chain,zeo,smoke,gcmc}.log
    산출    results_corepop_blocks_pc4_b06_heavy.json · results_corepop_e_humid3_323_pc4_b06.json + _audit.json · 실행 폴더 humid_wc_runs_v3w_323/corepop_e3_323_pc4_b06/
    견적    Zeo++ 81호출 직렬 약 10 ~ 13 h — 2번째 기기 글 §7(랩탑 b05 직렬 재시도 호출당 약 9분 · 다른 기기에서 옮긴 값)
            GCMC 막음 ok 구조 수(≤ 27)작업 · 워커 28 → 한 물결 · 끝은 가장 긴 작업 하나가 정함 · 15 ~ 25 h — 같은 글 §7(laptop2 b02 · 다른 기기에서 옮긴 값 · E 코어 속도 자료 없음)
            합 25 ~ 38 h → 끝 11-17 00시 ~ 13시. 범위는 옮긴 값입니다

---

# pc4 우편함 — pc4 만 씁니다

이 파일은 **pc4 만** 씁니다. 규약은 `21_ZIF69_MTV/COMMS.md`. 최신 글이 위에 옵니다.
