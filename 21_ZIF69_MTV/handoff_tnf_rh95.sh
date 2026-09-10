#!/bin/bash
# T-NF-0 RH95 무인 인계 (종합자 승인 09-10 §6 보완) — 12건 완주 뒤 s1·s2 각 1건
# ⚠️ 돌고 있는 이 스크립트를 편집하지 마십시오 (CLAUDE.md §6).
cd /home/skyjun/mof_project/21_ZIF69_MTV
PY=/home/skyjun/miniconda3/envs/czeromof/bin/python
wait_pid () {   # PID 재사용 함정 대비 — 번호와 명령줄을 같이 봅니다
  while kill -0 "$1" 2>/dev/null; do
    ps -p "$1" -o args= 2>/dev/null | grep -q "run_tnf.py" || break
    sleep 120
  done
}
wait_pid 987211
wait_pid 987268
for s in s1 s2; do
  nice -n 5 $PY -u run_tnf.py --cif charged_v3/zif90_DDEC6.cif --tag zif90_rh95_$s \
    --temp 298 --pco2 0 --rh 95 --workers 1 --seed-stagger 5 \
    --runs-root tnf_runs_zif90_rh95_$s --out tnf_results_zif90_rh95_$s.json \
    >> tnf_zif90_rh95_$s.log 2>&1 &
  sleep 7
done
wait
