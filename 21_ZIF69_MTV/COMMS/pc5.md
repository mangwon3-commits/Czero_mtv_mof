## 2026-11-16 01:19 — [COREPOP-H323] **pc5 — 착수 글: b08 · b09 중간 구조 5종(키 파일 c001941e 그대로 · 잰 한도 6.0 GB)** · 메모리 16 GB 노트북 첫 글 · 이 글 바로 뒤에 띄웁니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · pc4 · 사용자
**요약**: PC5 글(`HANDOVER_COREPOP_PC5_20261115.md`) §3 ~ §5 와 16 GB 글 §2 · §4 대로 이 기기를 갖추고 점검했습니다. 점검의 실패는 16 GB 글 §4 가 허용한 "메모리 전체 12 GB" 한 줄뿐이고, 비었을 때 잰 한도가 6.0 GB 라 키 파일 5종을 그대로 가져갑니다. b08 · b09 의 큰 기기 몫(21종씩)과 겹치지 않습니다. 사슬 · 래퍼 · 실행기 · 키 파일은 손대지 않았습니다. COMMS.md ⑦-4 에 따라 WSL 을 붙잡는 예약 작업을 사용자 승인으로 걸었습니다. 값은 읽지 않습니다.
**답 필요**: 아니오(이 기기에서 다르게 움직이면 이 우편함에 적겠습니다)

    기기    pc5 · 윈도우 11 Home 노트북(삼성 960XFG) · Intel Core i5-1340P(lscpu 실측 — PC5 글의 "i3-1340P" 는 오기로 보임) · 코어 12 · 논리 16 · 호스트 RAM 15.6 GB · C: 여유 31 GB(df /mnt/c)
            WSL 3.0.5 · Ubuntu 24.04(오늘 새로 설치) · .wslconfig memory=12GB · swap=8GB(16 GB 글 §2 그대로) · free -g total 11 · nproc 16
    전원    AC 연결(배터리 77 %) · 전원 모드 "최고 성능" · AC 절전 · 최대 절전 · 화면 끄기 모두 "안 함"(powercfg 값 0) · 윈도우 업데이트 일시 중지(11-17 01:12 KST 까지)
            ⚠ 덮개 닫기(AC)는 착수 시점에 아직 "절전"(값 1)입니다 — 사용자에게 "아무것도 안 함" 으로 바꿔 달라고 알렸고, 그때까지 덮개를 열어 둡니다. 바뀐 것을 확인하면 Zeo++ 끝 글에 적겠습니다
    env     ~/miniconda3 = Miniforge 26.9.4-2(Miniconda 대신 · 채널 conda-forge 만 · 설치 파일 sha256 을 GitHub 릴리스 digest 와 대조 · pc3 와 같은 판) · czeromof: python 3.10.22 · raspa2 2.0.50 · zeopp-lsmo 0.4.7 · ase 3.29.0 · numpy 2.2.6
            힘장 트리 00_Migration/raspa_share/raspa 통째 복사 · force_field_mixing_rules.def 8e8ec933 · C_co2 0.6512 · C_co2 29.933/2.745 · N_n2 38.298/3.306 · 물 5자리 · 빈 PATH 에서 simulate True(새 기기 글 §3-4)
    계정    GitHub 은 Czero_mtv_mof 하나 · Contents 읽기/쓰기 fine-grained 토큰(사용자가 만들어 직접 넣음) · git 이름은 다른 기기와 같음 · 연락은 이 우편함으로
    점검    corepop_preflight.sh pc5 b08 · pc5 b09(13a6dd41): 둘 다 점검 실패 1 = "!! 메모리 전체 12 GB …" 한 줄(16 GB 글 §4 의 허용 줄) · 그 밖의 [1]~[6] 전부 ok · Zeo++ 드라이 b08 32/32 · b09 32/32
            (처음 두 번은 "C: 여유 15 GB < 20 GB" 도 실패였음 — 사용자 승인으로 임시 파일 · 안 쓰는 zip 13.7 GB 를 지운 뒤 C: 여유 29 GB 로 ok)
    한도    simulate 0 · network 0 에서 MemAvailable − 5 = 6.006 · 6.017 · 6.087(세 번 · 마지막 01:1x) → 내림 6.0 ≥ 6.0 → 진행(PC5 글 §5-2)
            한도가 6.0 에 붙어 있어 걸릴 기대는 PC5 글 §1 의 0.3종보다 나쁘면 나빴지 좋지 않습니다. 걸린 구조가 있으면 Zeo++ 끝 글에 이름을 적습니다
    키 파일 corepop_medium_keys_pc5_20261115.json c001941e · 5종(b08 4 · b09 1) · 예측 최대 4.52 ~ 5.01 GB(PC5 글 §1) · 새로 만든 키 파일 없음
    파일    corepop_chain_keys.sh e5f65f5a · corepop_blocks_keys.py c2a71d4c · corepop_blocks.py c00cd11a · corepop_humid323_targets.json f0cbc615 · corepop_post.sh 101672d3 · corepop_rest_keys_b08.json 8f075da3 · corepop_rest_keys_b09.json 5d475e88 (무수정)
    드라이  래퍼 COREPOP_ZEO_DRY=1: 입력 대조 통과 · zip 524개 중 대상 5/5 · 묶음 b08 · b09 · 원자 수 = NAtoms(104 ~ 210) · 계획 15호출 · 병렬 1 · rc 0
    가져감  01:19 origin/master cb5d18af 에서 b08 · b09 의 큰 기기 착수 글 없음 · pc5 몫 5종을 가져간 글 없음
            laptop2 11-15 23:51 글이 "b02 뒤 차례는 b08 무거운 구조 21종" — PC5 글 §5-3 의 21종과 맞음(옛 한 줄의 25 · 22종 아님)
    폴더    5종의 corepop_zeo_runs/<파일 이름>/ 없음 · results_corepop_*pc5* 없음 · humid_wc_runs_v3w_323/corepop_e3_323_pc5_* 없음 · ~/.mof_chain/corepop_pc5_heavy.* 없음
    WSL     COMMS.md ⑦-4: 예약 작업 ClaudeWslHold(사용자 승인 11-16 01:1x) · 저장소 00_Migration/tools/wsl_hold.ps1 4d675522 무수정 사본 + 이 기기 실행기(CLAUDE_WSL_DIST=Ubuntu-24.04) · make_task.ps1 과 같은 설정(로그온 + 5분 · IgnoreNew · PT0S)
            01:17:07 "hold loop started" · WSL 안 sleep infinity 붙음 · 계산이 끝나면 예약 작업을 지웁니다
    커밋    호스트 커밋 착수 전 15.2/20.8 GB(73 %) — Discord · Steam · Epic · Overwolf · Riot 을 사용자 지시로 닫은 뒤 값(닫기 전 18.5 GB · 90 %). 16 GB 글 §6 대로 몇 시간마다 봅니다
    명령    mkdir -p ~/.mof_chain && cp ~/mof_project/21_ZIF69_MTV/corepop_chain_keys.sh ~/.mof_chain/
            cd ~/mof_project/21_ZIF69_MTV && RASPA_DIR=$HOME/RASPA/simulations REPO=$HOME/mof_project setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh pc5 corepop_medium_keys_pc5_20261115.json 1 $(nproc) < /dev/null > /dev/null 2>&1 &
            ($(nproc) = 16 · 실행기가 작업 수 5 로 줄임)
    기록    ~/.mof_chain/corepop_pc5_heavy.{chain,zeo,smoke,gcmc}.log(꼬리표 heavy 는 고정 · 16 GB 글 §5-4)
    산출    results_corepop_blocks_pc5_b08_b09_heavy.json · results_corepop_e_humid3_323_pc5_b08_b09.json + _audit.json
    견적    Zeo++ 15호출 직렬 1 ~ 2 h — PC5 글 §6(419호출로 맞춘 시간 식 · 평균 기기 속도에서 약 64 분 · 다른 기기에서 옮긴 값 · 모바일 CPU 발열 감안)
            GCMC 5작업 · 한 물결 — HKHOME b03 작업 0.68 ~ 14.01 h(중앙 2.27 · 16워커 · 다른 기기 · 다른 구조)에서 옮김. 작업합 ÷ 워커 < 최장 작업 → 가장 긴 작업 하나가 정함 · 3 ~ 15 h
            합 4 ~ 17 h → 끝 11-16 05시 ~ 18시. 이 기기의 속도 자료는 없어 범위는 옮긴 값입니다

---

# pc5 우편함 — pc5 만 씁니다

이 파일은 **pc5 만** 씁니다. 규약은 `21_ZIF69_MTV/COMMS.md`. 최신 글이 위에 옵니다.
