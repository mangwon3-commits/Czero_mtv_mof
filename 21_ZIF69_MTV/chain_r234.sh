#!/bin/bash
# 무인 잇기 — 라운드 1(PID 415)이 끝나면 라운드 2~4 를 잇는다. PLAN_30H_20260908.md §2.
#
# 왜 `kill -0 415` 만 쓰지 않는가
# --------------------------------
# 30시간이면 415 가 끝난 뒤 그 번호가 **재사용될 수 있다.** 재사용되면 `kill -0` 이 계속
# 참이라 잇기가 영영 안 걸린다 — 조용히 아무 일도 안 일어난다(§0 유형).
# 그래서 **번호가 아니라 그 번호가 무엇인지**를 본다: /proc/415/cmdline 에 도구 이름이
# 남아 있는 동안만 기다린다.
#
# `pkill -f` 는 쓰지 않는다 (CLAUDE.md §4 — 패턴이 제 명령줄을 잡는다).

set -u
cd /home/leehk/mof_project/21_ZIF69_MTV || exit 1

PY=/home/leehk/miniconda3/envs/czeromof/bin/python
WATCH=415
LOG=extend_round234.log

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

say "잇기 시작 — PID $WATCH 감시. 끝나면 --rounds 3 --no-local-stop."

# --- 라운드 1 드라이버가 끝날 때까지 ---
while :; do
    if [ ! -r /proc/$WATCH/cmdline ]; then
        say "PID $WATCH 종료됨(/proc 없음)."
        break
    fi
    if ! tr '\0' ' ' < /proc/$WATCH/cmdline 2>/dev/null | grep -q extend_chain_v3w; then
        say "PID $WATCH 가 더는 도구가 아님(번호 재사용). 대기 종료."
        break
    fi
    sleep 300
done

# --- 디스크 관문 (PLAN_30H §3 — 5 GB 아래면 새 계산 금지) ---
FREE=$(df -BG --output=avail /mnt/c 2>/dev/null | tail -1 | tr -dc '0-9')
if [ -n "$FREE" ] && [ "$FREE" -lt 5 ]; then
    say "!! /mnt/c 여유 ${FREE}G < 5G — 새 계산을 걸지 않는다. 사람이 봐야 한다."
    exit 3
fi
say "디스크 여유 ${FREE:-?}G — 통과."

# --- 라운드 1 이 실제로 조각을 남겼는지 (빈손으로 다음을 걸지 않는다) ---
N5=$(ls -d water_runs_v3w/water_runs_chunked/rh90_*/chunk5 2>/dev/null | wc -l)
say "조각5 폴더 $N5 개."

say "라운드 2~4 착수: $PY extend_chain_v3w.py --rounds 3 --no-local-stop"
"$PY" extend_chain_v3w.py --rounds 3 --no-local-stop >> "$LOG" 2>&1
say "라운드 2~4 종료 rc=$?"
