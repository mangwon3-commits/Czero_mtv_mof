#!/bin/bash
# E-24c 사슬(Junseok): ① Zeo++ 접근성(czeromof) → ② 관문 ⑤ 등록판 상한 12(lammps_mof) → ③ 서술 상한 60(lammps_mof). 차례로 · RASPA 없음.
D=/home/mangwon/mof_project/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin; LM=/home/mangwon/miniconda3/envs/lammps_mof/bin
cd "$D" || exit 1
idle() { [ "$(pgrep -xc simulate)" = 0 ] && [ "$(pgrep -xc network)" = 0 ] && [ "$(pgrep -c lmp_serial)" = 0 ]; }
echo "사슬 착수 $(date +%T)"
idle || { echo "!! RASPA/Zeo++/LAMMPS 도는 중 — 중단"; exit 1; }
$CZ/python -u magi5_e24c_zeo_junseok.py >> e24c_zeo_junseok.log 2>&1; rc=$?; echo "① rc $rc $(date +%T)"
[ $rc = 0 ] || { echo "!! ① 실패 — 멈춤"; exit 1; }
idle || { echo "!! ① 뒤 도는 것 있음 — 멈춤"; exit 1; }
$LM/python -u run_e24c_relax.py --cap 12 --gate5 >> e24c_gate5_junseok.log 2>&1; rc=$?; echo "② rc $rc $(date +%T)"
[ $rc = 0 ] || { echo "!! ② 실패 — 멈춤"; exit 1; }
idle || { echo "!! ② 뒤 도는 것 있음 — 멈춤"; exit 1; }
$LM/python -u run_e24c_relax.py --cap 60 >> e24c_relax60_junseok.log 2>&1; rc=$?; echo "③ rc $rc $(date +%T)"
