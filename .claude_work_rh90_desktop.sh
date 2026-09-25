#!/bin/bash
# 데스크탑 RH90 3종 (랩탑 2파도 몫 이관, CLAUDE.md §9) — WATER_FIX §4. 돌고 있는 이 파일을 편집하지 마십시오.
set -u
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
export RASPA_DIR=$HOME/RASPA/simulations
L=rh90_desktop.log
echo "===== $(date '+%F %T') RH90 데스크탑 착수: saIm0625 saIm0667 saIm075 =====" | tee -a "$L"
nice -n 10 /home/mangwon1/miniconda3/envs/czeromof/bin/python -u run_water_v3w.py --only saIm0625 saIm0667 saIm075 >> "$L" 2>&1
rc=$?; echo "===== $(date '+%F %T') RH90 데스크탑 종료 rc=$rc =====" >> "$L"
