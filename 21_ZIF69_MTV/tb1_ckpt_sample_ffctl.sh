#!/usr/bin/env bash
# T-B1 체크포인트 표집 — 규약은 COMMS/laptop.md 2026-09-05 13:1x 항에 등록됨.
#   눈금: WriteBinaryRestartFileEvery 500 이 덮어쓰는 binary_restart.dat 의 mtime
#   표본: 연속 6개 시각 -> 구간 5개, 생산 구간에만 있는 것
# 아무것도 지우지 않고, 돌고 있는 계산에 손대지 않습니다.
F=/home/skyjun/mof_project/21_ZIF69_MTV/tb1_runs_ffctl/hvap/CrashRestart/binary_restart.dat
OUT=/home/skyjun/mof_project/21_ZIF69_MTV/tb1_ckpt_sample_ffctl.log
prev=$(stat -c %Y "$F")
echo "표집 시작 $(date '+%F %T')  기준 mtime $(date -d @$prev '+%T')" >> "$OUT"
n=0
while [ $n -lt 6 ]; do
  sleep 30
  cur=$(stat -c %Y "$F" 2>/dev/null) || { echo "파일 없음 — 중단" >> "$OUT"; exit 1; }
  if [ "$cur" != "$prev" ]; then
    n=$((n+1))
    la=$(cut -d' ' -f1-3 /proc/loadavg)
    ns=$(pgrep -xc simulate)
    if [ $n -gt 1 ]; then d=$((cur-prev)); else d=0; fi
    echo "$n $(date -d @$cur '+%T') delta=${d}s load=[$la] simulate=$ns" >> "$OUT"
    prev=$cur
  fi
done
echo "표집 종료 $(date '+%F %T')" >> "$OUT"
