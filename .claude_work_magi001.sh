#!/bin/bash
# MAGI-001 결정 (21_ZIF69_MTV/MAGI/MAGI-001_desktop-idle-10runs.md §5, MULTILIGAND §8-5-5)
#   ① saIm050e1~e5 관문(risk, Zeo++ 9.5 GB/건, RASPA 0 상태에서)  ->  ② 10건 GCMC/Widom
# 돌고 있는 이 파일을 편집하지 마십시오 (CLAUDE.md §6).
set -u
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
LM=/home/mangwon1/miniconda3/envs/lammps_mof/bin
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
TAGS="sa50nb50e1 sa50nb50e2 sa50nb50e3 sa50nb50e4 sa50nb50e5 saIm050e1 saIm050e2 saIm050e3 saIm050e4 saIm050e5"
L1=risk_v3ens0500.log
L2=ens_mix10_gcmc.log

echo "===== $(date '+%F %T') MAGI-001 착수 — ① 관문 base+saIm050+e1~e5 (7종) =====" | tee -a "$L1"
echo "===== which python = $LM/python =====" >> "$L1"
PATH="$LM:$PATH" ENS0500_TAGS="saIm050,saIm050e1,saIm050e2,saIm050e3,saIm050e4,saIm050e5" \
  nice -n 10 "$LM/python" -u risk_screen_v3ens0500.py >> "$L1" 2>&1
RC1=$?
echo "===== $(date '+%F %T') ① 종료 rc=$RC1 =====" >> "$L1"

echo "===== $(date '+%F %T') MAGI-001 ② GCMC/Widom 10건 (V3_WORKERS=6, nice 10) — 관문 rc=$RC1 =====" | tee -a "$L2"
V3_WORKERS=6 nice -n 10 "$CZ" -u run_gcmc_v3.py --only $TAGS --out results_v3ens_mix10.json >> "$L2" 2>&1
RC2=$?
echo "===== $(date '+%F %T') ② 종료 rc=$RC2 =====" >> "$L2"
