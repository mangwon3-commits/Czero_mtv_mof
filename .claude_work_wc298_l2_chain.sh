#!/bin/bash
# 298 K 습윤 WC 앙상블 사슬 — laptop2. 323 K 드라이버(run_humid_wc_v3w_323.py)·simulate 가 3분 연속 0 이면 착수.
# 등록: ENS298_*_REGISTRATION_20260920.md (자료 0건). 기동: cd ~/mof_project && setsid nohup bash .claude_work_wc298_l2_chain.sh > .claude_work_wc298_l2_chain.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). 죽일 때는 PID 로(§4). 이 사슬은 git pull 을 하지 않는다(postman 몫).
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
: "${RASPA_DIR:=$HOME/RASPA/simulations}"; export RASPA_DIR
pick(){ for p in "$@"; do [ -x "$p" ] && { echo "$p"; return; }; done; echo ""; }
CZ="${CZ:-$(pick "$HOME/miniconda3/envs/czeromof/bin/python" "$HOME/anaconda3/envs/czeromof/bin/python")}"
LOG=wc298_l2_chain.log; WW="${HWC_V3W_WORKERS:-12}"
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
nsim(){ pgrep -xc simulate; }
drv(){ pgrep -fc 'run_humid_wc_v3w_32[3].py'; }
[ -n "$CZ" ] || { say "!! czeromof 파이썬 없음 — CZ=... 로 주고 재기동"; exit 2; }
say "================ 사슬 시작 (laptop2, 워커 $WW) — 323 K 배치 종료 대기 (드라이버 $(drv), simulate $(nsim)) ================"
q=0; while [ $q -lt 3 ]; do if [ "$(drv)" -gt 0 ] || [ "$(nsim)" -gt 0 ]; then q=0; sleep 60; else q=$((q+1)); sleep 60; fi; done
say "323 K 배치 종료 확인(드라이버·simulate 0, 3분). git status -uno: $(git status --porcelain -uno | tr '\n' ' ')"
# --- 1차 ---
for t in $(echo "mslm025e1,mslm025e2,mslm025e3,mslm025e4,mslm025e5" | tr ',' ' '); do [ -f "charged_v3/${t}_DDEC6.cif" ] || { say "!! 전하 CIF 없음 charged_v3/${t}_DDEC6.cif — 멈춤. 종합자에게 보고"; exit 3; }; done
say "1차 착수 — 타깃 mslm025e1,mslm025e2,mslm025e3,mslm025e4,mslm025e5, 워커 $WW, 결과 humid_working_capacity_w2_mslm025e_laptop2.json"
HWC_V3W_TARGETS="mslm025e1,mslm025e2,mslm025e3,mslm025e4,mslm025e5" HWC_V3W_WORKERS="$WW" HWC_V3W_RESULT="humid_working_capacity_w2_mslm025e_laptop2.json" "$CZ" -u run_humid_wc_v3w.py >> "$LOG" 2>&1; rc=$?
say "1차 rc=$rc"; [ -f "v3w_humid_wc/humid_working_capacity_w2_mslm025e_laptop2.json" ] && say "1차 결과 파일 생성 — 완주" || say "!! 1차 결과 파일 없음 — 비정상"
# --- 2차 ---
for t in $(echo "sa25nb75e1,sa25nb75e2,sa25nb75e3,sa25nb75e4,sa25nb75e5" | tr ',' ' '); do [ -f "charged_v3/${t}_DDEC6.cif" ] || { say "!! 전하 CIF 없음 charged_v3/${t}_DDEC6.cif — 멈춤. 종합자에게 보고"; exit 3; }; done
say "2차 착수 — 타깃 sa25nb75e1,sa25nb75e2,sa25nb75e3,sa25nb75e4,sa25nb75e5, 워커 $WW, 결과 humid_working_capacity_w2_sa25nb75e_laptop2.json"
HWC_V3W_TARGETS="sa25nb75e1,sa25nb75e2,sa25nb75e3,sa25nb75e4,sa25nb75e5" HWC_V3W_WORKERS="$WW" HWC_V3W_RESULT="humid_working_capacity_w2_sa25nb75e_laptop2.json" "$CZ" -u run_humid_wc_v3w.py >> "$LOG" 2>&1; rc=$?
say "2차 rc=$rc"; [ -f "v3w_humid_wc/humid_working_capacity_w2_sa25nb75e_laptop2.json" ] && say "2차 결과 파일 생성 — 완주" || say "!! 2차 결과 파일 없음 — 비정상"
say "사슬 종료"
