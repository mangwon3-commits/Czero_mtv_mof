#!/bin/bash
# T-NF-1q — MUF-16 건조 CO2 등온 273 K·308 K (등록 TNF_REGISTRATION_20260910.md §10, 자료 0건, 09-19 21:1x 데스크탑).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tnf1q_chain.sh > .claude_work_tnf1q.out 2>&1 < /dev/null &
# DRY=1 이면 입력 확인만. 8코어 상한(CLAUDE.md §5). T-NF-1w 의 슬롯 경합(9/8) 교훈: 착수 뒤 simulate 가 실제로 늘 때까지(최대 90 s) 기다린 뒤 다음 슬롯을 센다.
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
LOG=tnf1q_chain.log; DRY="${DRY:-0}"; MAXC=8
CIF=charged_v3/muf16_DDEC6.cif; TAG=muf16
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
nsim(){ pgrep -xc simulate; }
wait_slots(){ local n=$1; while [ $(( MAXC - $(nsim) )) -lt "$n" ]; do sleep 60; done; }
wait_spawn(){ local before=$1 t=0; while [ "$(nsim)" -le "$before" ] && [ $t -lt 90 ]; do sleep 5; t=$((t+5)); done; [ "$(nsim)" -gt "$before" ] || say "  !! 90 s 안에 simulate 가 늘지 않음(before=$before) — 드라이버 로그 확인"; }
disk_ok(){ local f; f=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4); print $4}'); [ "${f:-0}" -ge 5 ] || { say "!! C: 여유 ${f} GB < 5 — 중단"; exit 9; }; }
say "================ T-NF-1q 사슬 시작 (DRY=$DRY) ================"
[ -f "$CIF" ] || { say "!! CIF 없음 $CIF"; exit 2; }
M0=$(md5sum "$CIF" | cut -c1-32); say "CIF md5 $M0"; [ "${M0:0:8}" = "8d3fba10" ] || { say "!! CIF md5 가 T-NF-1 과 다름 — 중단"; exit 3; }
[ "$(pgrep -xc network)" = 0 ] || { say "!! Zeo++ 실행 중 — 동시 금지(§5)"; exit 4; }
disk_ok
say "[입력 확인] run_tnf.py --dry-run × 2 (273 K 1 bar / 308 K 0.05 bar)"
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_q273_dry" --temp 273 --pco2 1.0 --rh 0 --psat 611 --dry-run --runs-root "tnf1q_dryrun_273" >> "$LOG" 2>&1 || { say "!! dry-run(273) 실패"; exit 5; }
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_q308_dry" --temp 308 --pco2 0.05 --rh 0 --psat 5623 --dry-run --runs-root "tnf1q_dryrun_308" >> "$LOG" 2>&1 || { say "!! dry-run(308) 실패"; exit 5; }
grep -h "UnitCells\|ExternalTemperature\|ExternalPressure\|MoleculeName" tnf1q_dryrun_*/*/simulation.input 2>/dev/null | sort | uniq -c | sed 's/^/    /' | tee -a "$LOG"
if [ "$DRY" = 1 ]; then say "DRY 종료 — simulate 0건 띄움"; exit 0; fi
PIDS=()
# LPT: 273 K 고압(분자 많음) 먼저, 그다음 308 K. 씨앗 2 는 7 s 시차.
for T in 273 308; do case $T in 273) PS=611;; *) PS=5623;; esac
  for P in 1.00 0.50 0.165 0.10 0.05; do for S in 1 2; do
    wait_slots 1; disk_ok; b=$(nsim)
    nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_co2_${T}K_${P}bar_s${S}" --temp "$T" --pco2 "$P" --rh 0 --psat "$PS" --workers 1 \
      --runs-root "tnf1q_runs_${TAG}_${T}_${P}_s${S}" --out "tnf_results_${TAG}_co2_${T}K_${P}bar_s${S}.json" >> "tnf1q_${TAG}_${T}_${P}_s${S}.log" 2>&1 < /dev/null &
    PIDS+=($!); say "  ${T} K ${P} bar 씨앗 $S 착수 pid=$!"; wait_spawn "$b"; sleep 2
  done; done; done
say "모든 드라이버 착수 (${#PIDS[@]}개). 완주 대기."
for p in "${PIDS[@]}"; do while kill -0 "$p" 2>/dev/null; do sleep 60; done; done
sleep 5
n=$(ls tnf_results_${TAG}_co2_273K_*bar_s?.json tnf_results_${TAG}_co2_308K_*bar_s?.json 2>/dev/null | grep -vc _meta)
say "T-NF-1q 사슬 종료 — 결과 JSON ${n}/20. 판정은 등록 §10 그대로 TNF_RESULTS_20260910.md 에."
