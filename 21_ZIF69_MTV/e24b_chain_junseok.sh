#!/bin/bash
# E-24b 사슬(Junseok 14차): ① Zeo++ 접근성(czeromof) → ② 관문 ⑤ run_e24_gate5.py(lammps_mof — risk_screen 이 network·lmp_serial 을 절대경로로 찾음). 차례로 · RASPA 없음.
D=/home/mangwon/mof_project/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin; LM=/home/mangwon/miniconda3/envs/lammps_mof/bin
cd "$D" || exit 1
echo "사슬 착수 $(date +%T) · simulate $(pgrep -xc simulate) · network $(pgrep -xc network)"
[ "$(pgrep -xc simulate)" = 0 ] || { echo "!! simulate 도는 중 — 중단"; exit 1; }
$CZ/python -u magi5_e24b_zeo_junseok.py >> e24b_zeo_junseok.log 2>&1; rc=$?
echo "① rc $rc $(date +%T)"
[ $rc = 0 ] || { echo "!! ① 실패 — 관문 ⑤ 안 띄움"; exit 1; }
[ "$(pgrep -xc simulate)" = 0 ] && [ "$(pgrep -xc network)" = 0 ] || { echo "!! RASPA/Zeo++ 도는 중 — 관문 ⑤ 안 띄움"; exit 1; }
[ -e results_e24_gate5_junseok.json ] || [ -e e24_stage ] || [ -e lmp_e24 ] && { echo "!! 관문 ⑤ 이전 산출 있음 — 안 띄움"; exit 1; }
$LM/python -u run_e24_gate5.py >> e24_gate5_junseok.log 2>&1; rc=$?
echo "⑤ rc $rc $(date +%T)"
