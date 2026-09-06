#!/bin/bash
# 물 밀도 격자 v3w (T-4·T-6) — 사용자 지시 09-06 23:1x "띄워 당장 실행". WATER_FIX §3 ③. 대상 3종을 프로세스 셋으로, 2초 어긋내기(씨앗 규칙).
set -u
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
export RASPA_DIR=$HOME/RASPA/simulations
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
echo "===== $(date '+%F %T') 밀도 격자 v3w 착수: base nbIm025 saIm050 =====" | tee -a density_v3w.log
for t in base nbIm025 saIm050; do
  DW_SUB=$t nice -n 10 "$CZ" -u run_density_water_v3w.py $t >> density_v3w_$t.log 2>&1 &
  sleep 2
done
wait
echo "===== $(date '+%F %T') 밀도 격자 v3w 셋 종료 =====" >> density_v3w.log
