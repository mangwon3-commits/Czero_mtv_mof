## 2026-11-16 13:45 — [COREPOP-H323] **pc4 — 착수 글: b10 무거운 구조 7종 가운데 3종(2011[Zn][pcu]3[ASR]8 · 2011[Zn][pcu]3[FSR]8 · 2007[Zn][pcu]3[ASR]3) · 키 파일 corepop_rest_keys_b10_pc4.json 05eeeae4 · 나머지 4종은 한도 초과 예측으로 미룸(시도하지 않음)** · 사용자 결정 · WSL 그대로(한도 9.2 GB) · 이 글 바로 뒤에 띄웁니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · pc5 · 사용자
**요약**: b06 이 끝나(df8a105f) 2번째 기기 글 §5-8 대로 다음 무거운 묶음을 봤습니다. b07(HKHOME) · b08(랩탑) · b09(laptop2) 는 가져갔고 b10 무거운 7종은 아무도 안 가져갔습니다. 이 기기의 한도 9.2 GB 로는 7종 대부분이 가드에 걸릴 것이라 사용자에게 알렸고, 사용자가 **WSL 은 그대로 두고, 분할표 예측 × 1.17(16 GB 글 §1-2 의 보통 잔차) ≤ 9.3 GB 인 3종만** 가져가라고 정했습니다. **나머지 4종(2015[CrMn][noa]3[FSR]1 · 2021[Cd][kag]3[ASR]1 · 2022[Zn][rtl]3[ASR]1 · 2015[CrMn][nod]3[ASR]1)은 한도 초과 예측으로 미룹니다 — pc4 는 시도하지 않으며, 이 4종은 아직 아무도 가져가지 않은 상태입니다.** 키 파일은 b10 전체로 오해되지 않도록 표준 이름(corepop_rest_keys_b10.json)을 쓰지 않았고, 미룬 4종을 파일 안 `deferred` 에 적었습니다. 사슬 · 래퍼 · 실행기 · 분할표는 손대지 않았습니다. 값은 읽지 않습니다.
**답 필요**: 예 — 종합자: 미룬 b10 4종을 맡을 기기(예측 최대 12.8 ~ 22.2 GB · 한도 17 GB 이상 기기가 필요할 공산)

    가져감  13:3x origin/master 5a0f4f9e 에서 b10 무거운 착수 글 없음 · pc5 몫(corepop_medium_keys_pc5_20261115.json)에 b10 구조 없음 → 2번째 기기 글 §5-3 새 한 줄과 같은 7종
    고른 규칙 pred_peak_GB × 1.17 ≤ 9.3(사용자 결정 11-16 13:3x)
            가져감 3종  2011[Zn][pcu]3[ASR]8 6.54 → 7.65 · 2011[Zn][pcu]3[FSR]8 6.54 → 7.65 · 2007[Zn][pcu]3[ASR]3 6.70 → 7.84 GB (부피 4,197 ~ 4,297 Å³)
            미룸 4종    2015[CrMn][noa]3[FSR]1 12.79 → 14.96 · 2021[Cd][kag]3[ASR]1 14.26 → 16.68 · 2022[Zn][rtl]3[ASR]1 20.97 → 24.53 · 2015[CrMn][nod]3[ASR]1 22.15 → 25.92 GB
            ⚠ 가장 큰 잔차(× 1.46)로는 3종도 9.55 ~ 9.78 GB 라 가드에 걸릴 수 있습니다. b06 에서도 예측 아래였던 2020[Cd][sod]3[ASR]1 이 물 탐침 약 10 GB 로 빠졌습니다(df8a105f 글)
    한도    simulate 0 · network 0 에서 MemAvailable − 5 = 9.28 GB(13:3x) → 내림 9.2 · WSL 15.5 GB 그대로(사용자 결정)
    키 파일 corepop_rest_keys_b10_pc4.json 05eeeae4 · keys 3 · from 분할표 06e0ffb5 · minus pc5 키 파일 · rule · deferred 4 · 래퍼는 'keys' 만 읽음(corepop_blocks_keys.py:22 · corepop_chain_keys.sh:26) · 이 글과 같이 올림
    드라이  래퍼 COREPOP_ZEO_DRY=1: 입력 대조 통과 · zip 524개 중 대상 3/3 · 묶음 b10 · 원자 수 = NAtoms(82 ~ 106) · 계획 9건 · 병렬 1
    폴더    3종의 corepop_zeo_runs/<파일 이름>/ 없음 · results_corepop_*pc4_b10* 없음 · corepop_e3_323_pc4_b10 없음 · b06 기록 넷은 corepop_pc4_heavy_b06.*.log 로 옮김(§5-6)
    파일    corepop_chain_keys.sh e5f65f5a(저장소 판과 cmp 같음) · corepop_blocks_keys.py c2a71d4c · corepop_blocks.py c00cd11a · master 5a0f4f9e 와 같음
    WSL     ⑦-4 🔴 그대로(예약 작업 없음 · 사용자 선택 "창을 열어 둔 채")
    커밋    호스트 커밋 착수 전 39.5/58.7 GB(67 %)
    명령    cd ~/mof_project/21_ZIF69_MTV && RASPA_DIR=$HOME/RASPA/simulations REPO=$HOME/mof_project setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh pc4 corepop_rest_keys_b10_pc4.json 1 28 < /dev/null > /dev/null 2>&1 &
    산출    results_corepop_blocks_pc4_b10_heavy.json · results_corepop_e_humid3_323_pc4_b10.json + _audit.json · humid_wc_runs_v3w_323/corepop_e3_323_pc4_b10/
    견적    이 기기 b06 실측(같은 기기 · 다른 구조)에서: Zeo++ 9호출 × 약 5.5 분 ≈ 50 분(부피가 b06 가운데쯤이라 4 ~ 6 분/호출) · GCMC 3작업 한 물결 · b06 작업 0.44 ~ 1.39 h → 합 약 1.5 ~ 2.5 h · 끝 11-16 15:30 ~ 16:30

---

## 2026-11-16 13:30 — [COREPOP-H323] **pc4 — b06 무거운 구조 Zeo++ 끝 · 완주(감사 n 24 · n_ok 24 · 씨앗 서로 다름) · 빠진 구조 셋: 2021[Zn][scu]3[ASR]1 · 2018[Zn][pcu]3[ASR]3 · 2020[Cd][sod]3[ASR]1(가드 kill · 재시도에서도 실패)** · 사슬 8 h 51 m(Zeo++ 7.40 h + GCMC 1.45 h) · 값은 읽지 않았습니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · 사용자
**요약**: 11-15 22:39 에 띄운 b06 무거운 27종 사슬이 11-16 07:30 에 끝났습니다. Zeo++ 81호출 가운데 74호출 ok, 가드 kill 로 끝까지 실패한 것이 7호출(구조 셋)입니다. 셋 가운데 둘은 착수 글에서 분할표 예측이 잰 한도 9.3 GB 를 넘는다고 적은 구조이고, 2020[Cd][sod]3[ASR]1 은 예측 아래였지만 물 탐침 최대가 약 10 GB 였습니다. 이 셋의 처리는 종합자 몫입니다. 막음 ok 24종의 GCMC 는 24/24 완주했습니다. 이 글은 Zeo++ 끝 글과 완주 글을 하나로 합쳤습니다(이 세션이 Zeo++ 끝 때 깨어 있지 않았음). 착수 글 머리의 22:45 는 실제 게시 22:38(7697f54a)입니다.
**답 필요**: 아니오(빠진 세 구조의 처리는 종합자 몫)

    Zeo++   22:39:01 → 06:03:01 · 26,636 s(7.40 h) · 병렬 1 · 81호출 · ok 74 · 첫 판 실패 9 → 재시도 9 중 ok 2(2020[Cd][sod]3[FSR]1 물 · 2024[Zn][crb]3[ASR]15 물) · 끝까지 실패 7
            실패(전부 "멈춤!" = 가드 kill · 재시도 포함): 2021[Zn][scu]3[ASR]1 세 탐침(최대 9.7 ~ 11.1 GB) · 2018[Zn][pcu]3[ASR]3 세 탐침(9.7 ~ 11.5 GB) · 2020[Cd][sod]3[ASR]1 물(첫 판 · 재시도 약 10.1 GB · CO2 · N2 는 ok)
            사슬 기록: "전부 ok False · 막음 필요 구조 수 {'1.65': 2, '1.82': 0, '1.30': 3} · 막음 ok 구조 24"
            예측 대조: 분할표 pred_peak_GB 가 9.3 을 넘은 2종은 둘 다 빠짐 · 2020[Cd][sod]3[ASR]1 은 예측 아래였으나 빠짐(예측식 쪽 기록용)
    스모크  06:03:18 rc=0 n_ok=2(기대 2) · 값은 옮기지 않음
    GCMC    06:03 → 07:30:03 · 워커 28 · 24작업 한 물결 · 사슬 기록 "본 계산 끝 rc=0"
            입력 대조(한 작업): NumberOfInitializationCycles 5000 · NumberOfCycles 15000 · 323.0 K · 100000 Pa · y 0.150000 / 0.111141 / 0.738859 · Ewald 1e-6 · UnitCells 2 2 2
            완주 표지: 24/24 .data 에 "Simulation finished" · 작업 시간(.data total time) 0.44 ~ 1.39 h · 작업합 17.5 h · 끝은 가장 긴 작업(1.39 h)이 정함
    감사    {"n": 24, "n_ok": 24, "seeds_distinct": true, "loading_line_counts_all_1": true, "component2_N2_seen_all": true}
    견적    착수 글의 25 ~ 38 h(다른 기기에서 옮긴 값) → 실측 8.85 h. Zeo++ 는 호출당 약 5.5 분(옮긴 값 9 분) · GCMC 작업이 b03 HKHOME 값(가운데 2.27 h)보다 짧았음. 이 기기(i7-14700F) 속도가 옮긴 기기들과 다른 것으로 봅니다 — 옮긴 견적은 과대였습니다
    커밋    호스트 커밋 착수 전 33.1/58.7 GB(56 %) · 03:41 40.0/58.7(68 %) · 13:18 39.2/58.7(67 %) — 80 % 넘은 관측 없음(1시간마다 보지는 못함 · 관측 세 번)
    파일    results_corepop_blocks_pc4_b06_heavy.json c65c1a6f · results_corepop_e_humid3_323_pc4_b06.json a6c3568d · _audit.json 747895e1 · 비어 있지 않은 .block 74개(27종 폴더 · corepop_zeo_runs/<구조>/block<r>/)
    폴더    humid_wc_runs_v3w_323/corepop_e3_323_pc4_b06/ · corepop_zeo_runs/ 는 지우지 않았습니다 · 사슬 기록 ~/.mof_chain/corepop_pc4_heavy.{chain,zeo,smoke,gcmc}.log

---

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
