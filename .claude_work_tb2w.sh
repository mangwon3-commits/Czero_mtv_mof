#!/bin/bash
# nbIm050 체인(.claude_work_nb050.sh, bash PID 92226)이 끝나면 T-B2w(수정 힘장 물 K_H 39 Widom)를 바로 잇는다 — CLAUDE.md §9 '끊기지 않게'.
set -u
cd /home/mangwon1/mof_project || exit 1
while kill -0 92226 2>/dev/null; do sleep 300; done   # 92226 = ps 로 확인한 체인 bash PID (setsid 뒤의 $! 는 setsid 자신이라 곧 사라짐 — 11:12 오발동 원인)
cd 21_ZIF69_MTV
export RASPA_DIR=$HOME/RASPA/simulations
L=tb2w.log
echo "===== $(date '+%F %T') nbIm050 체인 종료 감지 → T-B2w 착수 =====" | tee -a "$L"
git -C .. pull -q --no-rebase 2>>"$L" || true
[ "$(pgrep -x network | wc -l)" -eq 0 ] || { echo "Zeo++ 가동 중 — 대기 실패" >> "$L"; exit 2; }
TB2_WORKERS=6 nice -n 10 /home/mangwon1/miniconda3/envs/czeromof/bin/python -u run_tb2w.py >> "$L" 2>&1
echo "===== $(date '+%F %T') T-B2w 종료 rc=$? =====" >> "$L"
