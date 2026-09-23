#!/bin/bash
# §AW 꼬리 완주 -> §AW-2 자동 착수. 09-22 08시에 아무도 안 깨어 있어 13시간 놀았던 일을 막는다.
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_corewc2_chain.sh > .claude_work_corewc2_chain.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). 죽일 때는 PID 로(§4).
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ="$HOME/miniconda3/envs/czeromof/bin/python"
LOG=corewc2_chain.log
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
drv(){ ps -eo args | grep -c '[r]un_core_wc\.py'; }
say "사슬 시작 — §AW 꼬리 종료 대기 (드라이버 $(drv), simulate $(pgrep -xc simulate))"
q=0
while [ $q -lt 3 ]; do
  if [ "$(drv)" -gt 0 ] || [ "$(pgrep -xc simulate)" -gt 0 ]; then q=0; else q=$((q+1)); fi
  sleep 60
done
say "§AW 꼬리 종료 확인(3분 연속 0)"
[ -f core_wc_pick2.json ] || { say "!! core_wc_pick2.json 없음 — 멈춤"; exit 3; }
say "§AW-2 착수 — COREWC_PICK=core_wc_pick2.json · OUT=core_wc_results_ext_laptop.json · 워커 8"
COREWC_ASSIGN=laptop COREWC_WORKERS=8 \
  COREWC_PICK="$PWD/core_wc_pick2.json" \
  COREWC_OUT="$PWD/core_wc_results_ext_laptop.json" \
  "$CZ" -u run_core_wc.py >> "$LOG" 2>&1
say "§AW-2 rc=$?"
say "사슬 종료"
