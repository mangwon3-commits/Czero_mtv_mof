#!/bin/bash
# 물 밀도 격자 v3w 확장 덱 (T4_PRIME §7) — saIm100 sa50nb50 nbIm075, 프로세스 셋, 2초 어긋내기. 돌고 있는 이 파일을 편집하지 마십시오.
set -u
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
export RASPA_DIR=$HOME/RASPA/simulations
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
echo "===== $(date '+%F %T') 밀도 격자 v3w 확장 착수: saIm100 sa50nb50 nbIm075 =====" | tee -a density_v3w.log
for t in saIm100 sa50nb50 nbIm075; do
  DW_EXTRA="saIm100,sa50nb50,nbIm075" DW_SUB=$t nice -n 10 "$CZ" -u run_density_water_v3w.py $t >> density_v3w_$t.log 2>&1 &
  sleep 2
done
wait
echo "===== $(date '+%F %T') 밀도 격자 v3w 확장 셋 종료 =====" >> density_v3w.log
