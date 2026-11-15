## 2026-11-16 05:30 — [COREPOP-H323] **pc5 — 완주: b08 · b09 중간 구조 4종 GCMC(03:15 · 감사 n 4 · n_ok 4 · 씨앗 서로 다름)** · 결과 JSON 과 감사 JSON 첨부 · 이 기기의 COREPOP 몫 끝 · 값은 옮기지 않았습니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · pc4 · 사용자
**요약**: 바로 앞 Zeo++ 끝 글의 막음 ok 4종을 스모크 뒤 한 물결(작업 4 · 워커 16)로 돌려 03:15:19 에 마쳤습니다. 감사 줄의 다섯 표지가 모두 참이고, 행 4개 모두 완주 표지(Simulation finished)가 있습니다. 2014[Zn][unj]3[FSR]1 은 막음이 없어 이 결과에 없습니다(앞 글 · 큰 기기 몫으로 돌려보냄). 키 파일 밖 구조는 돌리지 않았고, 이 기기에 배정된 몫은 여기서 끝입니다.
**답 필요**: 아니오(이 기기의 다음 일은 사용자 · HKHOME 이 정합니다)

    감사    chain.log 그대로: "2026-11-16 03:15:19 본 계산 끝 rc=0 · 감사 {"n": 4, "n_ok": 4, "seeds_distinct": true, "loading_line_counts_all_1": true, "component2_N2_seen_all": true}"
    행      결과 JSON rows 4 · runner_status ok 4 · finished True 4 · ok True 4 · net_charge_ok True 4
            씨앗 1794764230 · 1794764245 · 1794764260 · 1794764275(서로 다름)
            실행 폴더 humid_wc_runs_v3w_323/corepop_e3_323_pc5_b08_b09/runs 4 · Simulation finished 4/4
    관문    gcmc.log · smoke.log 둘 다 force_field_mixing_rules.def md5 8e8ec933 일치
    작업    LPT 순 2016[Cu][nbo]3[FSR]2(N_super 2,928 · 막음 CO2 · N2 · water) → 2015[V][bpq]3[ASR]1 · [FSR]1(각 1,216 · 막음 없음) → 2021[Fe][acs]3[ASR]1(832 · 막음 없음)
            작업 시간(02:37:09 착수 → 각 .data 의 마지막 쓰기 시각 · 근사): Fe acs 0.34 h · V bpq ASR 0.35 h · V bpq FSR 0.35 h · Cu nbo 0.64 h(가장 긺)
            벽시계 38 m 10 s — 가장 긴 작업 하나(Cu nbo)가 정함 · 작업합 1.67 h ÷ 워커 16 = 0.10 h 보다 긺
    견적    GCMC: 착수 견적 3 ~ 15 h(HKHOME b03 · 다른 기기 · 다른 구조에서 옮긴 값) → 실제 0.64 h. 범위보다 한참 아래입니다. 이 4종은 N_super 832 ~ 2,928 로 작고, 옮긴 견적이 그 차이를 반영하지 못했습니다(CLAUDE.md §5 "견적의 출처")
            전체: 착수 01:20:08 → 완주 03:15:19 = 1 h 55 m(착수 견적 4 ~ 17 h)
    메모리  16 GB 글 §6 의 "GCMC 첫 물결 뒤 available ≥ 3 GB" 는 재지 못했습니다(사용자가 자리를 비운 사이 38분 만에 끝남). 05:25 free -m available 11,360 MB
    값      gcmc.log 를 볼 때 값이 든 줄이 화면에 찍혔지만 옮기지 않았습니다
    파일    results_corepop_e_humid3_323_pc5_b08_b09.json(e1f11b75 · 15,204 B · 03:15) · results_corepop_e_humid3_323_pc5_b08_b09_audit.json(067fcf32 · 2,361 B · 03:15)
    폴더    실행 폴더 · corepop_zeo_runs · ~/.mof_chain 기록은 지우지 않았습니다(새 기기 글 §6)
    다음    WSL 유지 예약 작업 ClaudeWslHold 는 사용자 확인 뒤 지웁니다 · GitHub 토큰은 사용자가 지웁니다

---

## 2026-11-16 05:29 — [COREPOP-H323] **pc5 — b08 · b09 중간 5종 Zeo++ 끝(02:36 · 15호출 중 14 ok · 가드 kill 1 · 빠진 구조 1 = 2014[Zn][unj]3[FSR]1 → 큰 기기 몫) · 스모크 통과 · GCMC 4작업도 03:15 완주(바로 다음 글)** · 막음 JSON 과 막음 파일 12개 첨부 · 값은 옮기지 않았습니다
**받는 곳**: HKHOME · 클라우드 종합자 · 랩탑 · laptop2 · pc3 · pc4 · 사용자
**요약**: 착수 글(11-16 01:19) 대로 띄운 사슬이 Zeo++ 15호출을 한 번에 하나씩 돌려 02:36:52 에 마쳤습니다(1 h 17 m · 착수 견적 1 ~ 2 h 안). 14호출이 ok 이고, 2014[Zn][unj]3[FSR]1 의 막음 1.65(CO2) 한 호출이 가드에 걸렸고 직렬 재시도에서도 걸렸습니다. 그래서 이 구조는 GCMC 에서 빠졌고, 16 GB 글 §6 대로 큰 기기 몫에 돌려보냅니다. 키 파일의 고르는 규칙(보통 잔차 ×1.17)보다 실측이 큰 구조가 셋이라 아래에 실측/예측을 적습니다.
**답 필요**: 예 — HKHOME: 2014[Zn][unj]3[FSR]1(b08) 을 큰 기기 몫(다음 무거운 키 파일)에 합쳐 주십시오. 이 기기는 키 파일 밖 구조를 돌리지 않습니다(PC5 글 §7)

    Zeo++   chain.log 그대로: "2026-11-16 02:36:52 Zeo++ 끝 rc=0 · 저장 /home/kgees/mof_project/21_ZIF69_MTV/results_corepop_blocks_pc5_b08_b09_heavy.json (4603 s) · 전부 ok False · 막음 필요 구조 수 {'1.65': 1, '1.82': 1, '1.30': 1}"
            chain.log 그대로: "2026-11-16 02:36:52 막음 ok 구조 4"
            zeo.log: 호출 15 · ok 14 · 가드 kill 1 · 직렬 재시도 1(그것도 가드 kill) · 빠진 구조 1 · 병렬 1
            걸린 호출: 2014[Zn][unj]3[FSR]1 r=1.65(CO2) — 218.0 s 에 최대 6,390 MB 에서 kill · 재시도 216.1 s 에 6,942 MB 에서 다시 kill. 같은 구조의 1.82 · 1.30 은 ok(5,882 · 4,422 MB)
            호출 시간 216 ~ 338 s(재시도 포함 16호출) · ok 호출의 최대 RSS 5,882 MB
    예측식  키 파일 c001941e 의 규칙 "pred_peak × 1.17 ≤ 6.0 GB"(PC5 글 §1) 대로 고른 5종 · 구조마다 세 탐침 중 실측 최대(MB ÷ 1024)와 예측:
            2015[V][bpq]3[ASR]1   4.38 GB / 예측 4.58 = 0.96
            2015[V][bpq]3[FSR]1   4.46 / 4.58 = 0.97
            2016[Cu][nbo]3[FSR]2  5.66 / 4.82 = 1.17
            2021[Fe][acs]3[ASR]1  5.60 / 4.52 = 1.24
            2014[Zn][unj]3[FSR]1  ≥ 6.24(kill 시점 · 재시도 ≥ 6.78) / 5.01 = ≥ 1.25(재시도 ≥ 1.35)
            실측 > 예측 × 1.17 이 3종입니다(Cu nbo 는 경계 · MB ÷ 1000 으로 보면 1.20). 다섯 다 가장 큰 잔차 ×1.46 안이지만, 보통 잔차로 고른 이 몫에서 걸린 수(1종)는 PC5 글 §1 의 기대 0.3종보다 많았습니다
            Zn unj 는 kill 시점이 이미 잰 한도(6.0)를 넘었고 실제 최대는 그보다 크므로, 이 기기의 한도로는 막을 수 없는 구조입니다
    스모크  chain.log 그대로: "2026-11-16 02:37:09 스모크 rc=0 n_ok=2 (기대 2)"(값은 옮기지 않음)
    GCMC    02:37:09 착수 · 작업 4 · 워커 16 → 한 물결 · 03:15:19 끝. 완주 글은 이 글 바로 다음에 따로 올립니다
    기기    덮개 닫기(AC): 착수 글의 ⚠ 뒤 사용자가 바꿨고 01:4x 무렵 값 0("아무 것도 안 함")을 확인했습니다. 그 사이 한 번 값 3(종료)으로 저장된 것을 잡아 다시 고쳤습니다
            WSL 유지: wsl_hold.log 의 "hold loop started" 가 01:17:07 · 01:37:10 두 번입니다. 첫 인스턴스가 그 사이에 끝났고 5분 트리거가 다시 띄웠습니다. 배포판은 내려가지 않았고(05:25 WSL uptime 5 h 12 m) 사슬 기록도 끊기지 않았습니다. 첫 인스턴스가 왜 끝났는지는 확인하지 못했습니다
            호스트 커밋: Zeo++ 첫 호출 중 01:2x 에 최대 18.7/20.8 GB(90 %)를 쟀습니다 → 사용자 지시로 Edge · 카카오톡을 닫은 뒤 85 % → 01:4x 78 % · 05:25 에 14.6/20.8 GB(70 %). 그 뒤 잰 값은 없습니다
    견적    Zeo++ 실제 1.28 h(착수 견적 1 ~ 2 h · 아래쪽)
    파일    results_corepop_blocks_pc5_b08_b09_heavy.json(072d8130 · 15,059 B · 02:36)
            corepop_zeo_runs/<4종>/block{1.65,1.82,1.30}/<파일>.block 12개(전부 비어 있지 않음)
            ⚠ 2014_Zn__unj_3_FSR_1 의 막음 파일 2개(1.82 · 1.30 · ok)는 올리지 않았습니다. corepop_blocks.py(c00cd11a) 179행은 대상 구조의 corepop_zeo_runs/<파일 이름>/ 폴더가 있으면 묶음 전체를 멈추므로, 이 구조를 넘겨받는 기기의 작업트리에 그 폴더가 생기지 않게 하려는 것입니다. 이 기기에는 그대로 남아 있습니다

---

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
