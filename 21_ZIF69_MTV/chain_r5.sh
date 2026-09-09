#!/bin/bash
# 5라운드째 잇기 — 라운드 2~4 드라이버(PID 1801 의 python)가 끝나면 조각 9 를 잇는다.
# 사용자 재승인 09-09 12:0x (상한 4 -> 5, §E-2 / ASSIGN §Q).
#
# 목적(§Q): sa50nb50 의 가속이 멈추는가 + 단조 감쇠 계열의 점 하나.
#
# PID 감시는 `kill -0` 만 쓰지 않는다 — 번호가 재사용되면 조건이 계속 참이라 영영 안 걸린다.
# /proc/<pid>/cmdline 에 그 스크립트 이름이 남아 있는 동안만 기다린다. `pkill -f` 금지.

set -u
cd /home/leehk/mof_project/21_ZIF69_MTV || exit 1

PY=/home/leehk/miniconda3/envs/czeromof/bin/python
WATCH=1801                       # chain_r234.sh
LOG=extend_round5.log

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

say "5라운드째 잇기 시작 — PID $WATCH(chain_r234.sh) 감시."

while :; do
    if [ ! -r /proc/$WATCH/cmdline ]; then
        say "PID $WATCH 종료됨(/proc 없음)."; break
    fi
    if ! tr '\0' ' ' < /proc/$WATCH/cmdline 2>/dev/null | grep -q chain_r234; then
        say "PID $WATCH 가 더는 그 스크립트가 아님(번호 재사용). 대기 종료."; break
    fi
    sleep 300
done

FREE=$(df -BG --output=avail /mnt/c 2>/dev/null | tail -1 | tr -dc '0-9')
if [ -n "$FREE" ] && [ "$FREE" -lt 5 ]; then
    say "!! /mnt/c 여유 ${FREE}G < 5G — 새 계산을 걸지 않는다."
    exit 3
fi
say "디스크 여유 ${FREE:-?}G — 통과."

# 조각8 이 7종 다 완주했는지 (빈손으로 다음을 걸지 않는다)
N=0
for n in base saIm0875 saIm0917 saIm0958 saIm100 mslm050 sa50nb50; do
    f=$(ls water_runs_v3w/water_runs_chunked/rh90_$n/chunk8/Output/System_0/*.data 2>/dev/null | head -1)
    if [ -n "$f" ] && grep -q "Simulation finished" "$f"; then N=$((N+1)); fi
done
say "조각8 완주 $N/7."
if [ "$N" -lt 7 ]; then
    say "!! 7종이 다 완주하지 않았다. 라운드 사이 관문이 미완주 조성을 건너뛸 것이다 — 그대로 진행한다."
fi

say "5라운드째 착수: $PY extend_chain_v3w.py --rounds 1 --no-local-stop"
"$PY" extend_chain_v3w.py --rounds 1 --no-local-stop >> "$LOG" 2>&1
say "5라운드째 종료 rc=$?"
