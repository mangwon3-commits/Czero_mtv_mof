#!/bin/bash
# h~p (9회) 완주하면 등록 판정을 돌린다. q~s(e4) 는 별도로 붙는다.
D=/home/mangwon/mof_project/21_ZIF69_MTV
export PATH=/home/mangwon/miniconda3/envs/czeromof/bin:$PATH
cd "$D" || exit 1
for i in $(seq 1 600); do
  n=0; for T in h i j k l m n o p; do [ -f "v3_water_repro_$T/water_results.json" ] && n=$((n+1)); done
  q=0; for T in q r s; do [ -f "v3_water_repro_$T/water_results.json" ] && q=$((q+1)); done
  live=$(pgrep -c -x simulate); live=${live:-0}
  if [ "$n" -ge 9 ] && [ "$live" -eq 0 ]; then
    echo "=== h~p 9/9 완주 · e4 $q/3 · $(date "+%F %T") ==="
    exec python repro_verdict.py
  fi
  sleep 30
done
echo "!! 5시간 초과 — 완주 $n/9, e4 $q/3, simulate $live개"
exec python repro_verdict.py
