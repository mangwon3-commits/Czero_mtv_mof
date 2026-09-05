#!/usr/bin/env bash
# B 표집 — 대조의 **생산** 구간. 초기화가 끝난 뒤에 시작해야 구간이 안 섞입니다.
#   등록 규약은 A·D 와 동일: 500사이클 눈금, 5구간, 모든 구간의 simulate 개수 동일,
#   (max-min)/mean <=10% 정상 / ~25% 구간보고 / >25% 외삽 안 함.
D=/home/skyjun/mof_project/21_ZIF69_MTV/tb1_runs_ffctl/hvap
F="$D/CrashRestart/binary_restart.dat"
DATA="$D/Output/System_0/output_Box_1.1.1_298.150000_100000.data"
OUT=/home/skyjun/mof_project/21_ZIF69_MTV/tb1_ckpt_sample_B.log
echo "B 감시 시작 $(date '+%F %T') — 생산 시작을 기다립니다" >> "$OUT"
# 생산 시작 = .data 에 'Current cycle: 0 out of 15000' (앞에 [Init] 없음)
while ! grep -aq '^Current cycle: 0 out of 15000' "$DATA" 2>/dev/null; do sleep 60; done
echo "생산 시작 감지 $(date '+%F %T')" >> "$OUT"
prev=$(stat -c %Y "$F")
echo "기준 mtime $(date -d @$prev '+%T')" >> "$OUT"
n=0
while [ $n -lt 6 ]; do
  sleep 30
  cur=$(stat -c %Y "$F" 2>/dev/null) || { echo "파일 없음 — 중단" >> "$OUT"; exit 1; }
  if [ "$cur" != "$prev" ]; then
    n=$((n+1)); la=$(cut -d' ' -f1-3 /proc/loadavg); ns=$(pgrep -xc simulate)
    if [ $n -gt 1 ]; then d=$((cur-prev)); else d=0; fi
    echo "$n $(date -d @$cur '+%T') delta=${d}s load=[$la] simulate=$ns" >> "$OUT"
    prev=$cur
  fi
done
echo "B 표집 종료 $(date '+%F %T')" >> "$OUT"
