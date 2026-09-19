#!/bin/bash
# T-NF-1q §10-보완 — 공통 적재 범위 확장 10건 (등록 TNF_REGISTRATION_20260910.md §10-보완, 자료 0건, 09-19 22:3x).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tnf1q2_chain.sh > .claude_work_tnf1q2.out 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
LOG=tnf1q2_chain.log; DRY="${DRY:-0}"; MAXC=8
CIF=charged_v3/muf16_DDEC6.cif; TAG=muf16
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
nsim(){ pgrep -xc simulate; }
wait_slots(){ local n=$1; while [ $(( MAXC - $(nsim) )) -lt "$n" ]; do sleep 60; done; }
wait_spawn(){ local before=$1 t=0; while [ "$(nsim)" -le "$before" ] && [ $t -lt 90 ]; do sleep 5; t=$((t+5)); done; [ "$(nsim)" -gt "$before" ] || say "  !! 90 s 안에 simulate 가 늘지 않음(before=$before)"; }
disk_ok(){ local f; f=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4); print $4}'); [ "${f:-0}" -ge 5 ] || { say "!! C: 여유 ${f} GB < 5 — 중단"; exit 9; }; }
say "================ T-NF-1q 보완 사슬 시작 (DRY=$DRY) ================"
M0=$(md5sum "$CIF" | cut -c1-32); [ "${M0:0:8}" = "8d3fba10" ] || { say "!! CIF md5 다름"; exit 3; }
[ "$(pgrep -xc network)" = 0 ] || { say "!! Zeo++ 실행 중"; exit 4; }
disk_ok
JOBS="273:0.01 273:0.02 293:0.02 308:3.00 308:2.00"
say "[입력 확인] dry-run 273 K 0.01 bar / 308 K 3 bar"
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_q2_dry273" --temp 273 --pco2 0.01 --rh 0 --psat 611 --dry-run --runs-root "tnf1q2_dryrun_273" >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_q2_dry308" --temp 308 --pco2 3.0 --rh 0 --psat 5623 --dry-run --runs-root "tnf1q2_dryrun_308" >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
grep -h "UnitCells\|ExternalTemperature\|ExternalPressure" tnf1q2_dryrun_*/*/simulation.input 2>/dev/null | sort | uniq -c | sed 's/^/    /' | tee -a "$LOG"
if [ "$DRY" = 1 ]; then say "DRY 종료"; exit 0; fi
PIDS=()
for J in $JOBS; do T=${J%%:*}; P=${J##*:}; case $T in 273) PS=611;; 293) PS=2339;; *) PS=5623;; esac
  for S in 1 2; do wait_slots 1; disk_ok; b=$(nsim)
    nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_co2_${T}K_${P}bar_s${S}" --temp "$T" --pco2 "$P" --rh 0 --psat "$PS" --workers 1 \
      --runs-root "tnf1q2_runs_${TAG}_${T}_${P}_s${S}" --out "tnf_results_${TAG}_co2_${T}K_${P}bar_s${S}.json" >> "tnf1q2_${TAG}_${T}_${P}_s${S}.log" 2>&1 < /dev/null &
    PIDS+=($!); say "  ${T} K ${P} bar 씨앗 $S 착수 pid=$!"; wait_spawn "$b"; sleep 2
  done; done
say "모든 드라이버 착수 (${#PIDS[@]}개). 완주 대기."
for p in "${PIDS[@]}"; do while kill -0 "$p" 2>/dev/null; do sleep 60; done; done
sleep 5
n=0; for J in $JOBS; do T=${J%%:*}; P=${J##*:}; for S in 1 2; do [ -f "tnf_results_${TAG}_co2_${T}K_${P}bar_s${S}.json" ] && n=$((n+1)); done; done
say "T-NF-1q 보완 사슬 종료 — 결과 JSON ${n}/10. 판정 2 는 등록 §10 격자·문턱 그대로 확장 범위에서."
