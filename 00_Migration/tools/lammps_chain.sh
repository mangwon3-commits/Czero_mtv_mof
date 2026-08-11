#!/bin/bash
P=/home/mangwon1/mof_project/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
LM=/home/mangwon1/miniconda3/envs/lammps_mof/bin
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin
export RASPA_DIR=/home/mangwon1/RASPA/simulations
cd "$P" || exit 1
echo ">>> [$(date +%H:%M)] saIm 5종 시작"
PATH="$LM:$CZ:$PATH" stdbuf -oL "$LM/python" risk_screen.py > "$W/lammps_saim.log" 2>&1
echo ">>> [$(date +%H:%M)] saIm 종료코드 $?"
echo ">>> [$(date +%H:%M)] 아릴 12종 시작"
PATH="$LM:$CZ:$PATH" stdbuf -oL "$LM/python" risk_screen.py aryl_scan_index.json aryl \
  > "$W/lammps_aryl.log" 2>&1
echo ">>> [$(date +%H:%M)] 아릴 종료코드 $?"
echo ">>> [$(date +%H:%M)] 전체 완료"
