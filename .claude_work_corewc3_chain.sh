#!/bin/bash
# §AW-2 완주 뒤, laptop2 몫 분담분이 **파일로 와 있으면** 유휴 없이 이어서 돈다.
#   기다리는 파일: 21_ZIF69_MTV/core_wc_pick3_laptop.json  (없으면 24 h 기다리다 조용히 끝난다)
# 왜: 09-22 에 완주 뒤 13 h, laptop2 는 세션이 끊겨 109종이 멈춰 있다. 시각에 걸린 인계는
#     "그때 깨어 있는 무언가" 가 필요하다(CLAUDE.md §9). 사람 대신 이것이 깬다.
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_corewc3_chain.sh > .claude_work_corewc3_chain.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(§6). 죽일 때는 PID 로(§4).
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ="$HOME/miniconda3/envs/czeromof/bin/python"
LOG=corewc3_chain.log
PREV_CHAIN=2432337                      # §AW-2 를 띄우는 앞 사슬. 이것이 사라져야 §AW-2 가 끝난 것.
PICK=core_wc_pick3_laptop.json
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
drv(){ ps -eo args | grep -c '[r]un_core_wc\.py'; }
say "사슬3 시작 — 앞 사슬(PID $PREV_CHAIN) 종료 대기"
while kill -0 "$PREV_CHAIN" 2>/dev/null; do sleep 60; done
say "앞 사슬 종료 확인. 계산 정지 확인 중"
q=0; while [ $q -lt 3 ]; do
  if [ "$(drv)" -gt 0 ] || [ "$(pgrep -xc simulate)" -gt 0 ]; then q=0; else q=$((q+1)); fi
  sleep 60
done
say "정지 확인(3분 연속 0). $PICK 을 기다립니다(최대 24 h)"
n=0
while [ ! -f "$PICK" ]; do
  n=$((n+1)); [ $n -ge 1440 ] && { say "24 h 동안 $PICK 이 안 와 종료합니다(할 일 없음)"; exit 0; }
  sleep 60
done
say "$PICK 도착 — 착수. 항목 $("$CZ" -c "import json;print(len(json.load(open('$PICK'))))" 2>/dev/null)"
COREWC_ASSIGN=laptop COREWC_WORKERS=8 \
  COREWC_PICK="$PWD/$PICK" \
  COREWC_OUT="$PWD/core_wc_results_ext2_laptop.json" \
  "$CZ" -u run_core_wc.py >> "$LOG" 2>&1
say "rc=$? · 사슬3 종료"
