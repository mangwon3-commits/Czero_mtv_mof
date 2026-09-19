#!/bin/bash
# T-NF-1w — MUF-16 물 항 진단 사슬 (등록 TNF_REGISTRATION_20260910.md §9, 자료 0건, 09-19 19:5x 데스크탑).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tnf1w_chain.sh > .claude_work_tnf1w.out 2>&1 < /dev/null &
# DRY=1 이면 입력 확인만(simulate 를 띄우지 않음). 8코어 상한(CLAUDE.md §5) — 슬롯이 날 때만 다음을 띄운다.
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
LOG=tnf1w_chain.log; DRY="${DRY:-0}"; MAXC=8
CIF=charged_v3/muf16_DDEC6.cif; TAG=muf16
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
slots(){ echo $(( MAXC - $(pgrep -xc simulate) )); }
wait_slots(){ local n=$1; while [ "$(slots)" -lt "$n" ]; do sleep 60; done; }
disk_ok(){ local f; f=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4); print $4}'); [ "${f:-0}" -ge 5 ] || { say "!! C: 여유 ${f} GB < 5 — 중단"; exit 9; }; }
md5_now(){ md5sum "$CIF" | cut -c1-32; }
say "================ T-NF-1w 사슬 시작 (DRY=$DRY) ================"
[ -f "$CIF" ] || { say "!! CIF 없음 $CIF"; exit 2; }
M0=$(md5_now); say "CIF $CIF md5 $M0 (T-NF-1 과 같은 8d3fba10 이어야 함)"
[ "${M0:0:8}" = "8d3fba10" ] || { say "!! CIF md5 가 T-NF-1 과 다름 — 중단"; exit 3; }
[ "$(pgrep -xc network)" = 0 ] || { say "!! Zeo++ 실행 중 — RASPA 와 동시 금지(§5)"; exit 4; }
disk_ok
# ---- 입력 확인(dry-run) — 세 가지 run_tnf 모드 전부
say "[입력 확인] run_tnf.py --dry-run × 3 (순수 물 / 사전 적재 / CO2 단일)"
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_w298_dry" --temp 298 --pco2 0 --rh 20,40,60,80,100 --psat 3169 --dry-run --runs-root "tnf1w_dryrun_w" >> "$LOG" 2>&1 || { say "!! dry-run(순수 물) 실패"; exit 5; }
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_pre_dry" --temp 298 --pco2 0 --rh 100 --psat 3169 --preload-water 110 --dry-run --runs-root "tnf1w_dryrun_p" >> "$LOG" 2>&1 || { say "!! dry-run(사전 적재) 실패"; exit 5; }
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_co2_dry" --temp 293 --pco2 1.0 --rh 0 --psat 2339 --dry-run --runs-root "tnf1w_dryrun_c" >> "$LOG" 2>&1 || { say "!! dry-run(CO2 단일) 실패"; exit 5; }
say "  dry-run 3/3 rc=0"
$CZ -c "import run_kh_muf16, run_he_muf16; print('  래퍼 import ok')" >> "$LOG" 2>&1 || { say "!! 래퍼 import 실패"; exit 6; }
grep -h "UnitCells\|ExternalTemperature\|ExternalPressure\|CreateNumberOfMolecules\|MolFraction" tnf1w_dryrun_*/*/simulation.input 2>/dev/null | sort | uniq -c | sed 's/^/    /' | tee -a "$LOG"
if [ "$DRY" = 1 ]; then say "DRY 종료 — simulate 0건 띄움"; exit 0; fi
PIDS=()
# ---- 1단계: 사전 적재 RH100 ×2(가장 긴 것 먼저, LPT) + 순수 물 등온 ×2 (3+3) = 8
say "[1단계] 사전 적재 110 H2O × 2 + 순수 물 등온 RH20~100 × 2씨앗(워커 3+3)"
for S in 1 2; do wait_slots 1; disk_ok
  nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_w298_pre110_s${S}" --temp 298 --pco2 0 --rh 100 --psat 3169 --preload-water 110 --workers 1 \
    --runs-root "tnf1w_runs_${TAG}_pre_s${S}" --out "tnf_results_${TAG}_water298_pre110_s${S}.json" >> "tnf1w_${TAG}_pre_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  사전 적재 씨앗 $S 착수 pid=$!"; sleep 7; done
for S in 1 2; do wait_slots 3; disk_ok
  nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_w298_s${S}" --temp 298 --pco2 0 --rh 20,40,60,80,100 --psat 3169 --workers 3 --seed-stagger 5 \
    --runs-root "tnf1w_runs_${TAG}_w298_s${S}" --out "tnf_results_${TAG}_water298_s${S}.json" >> "tnf1w_${TAG}_w298_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  순수 물 등온 씨앗 $S 착수 pid=$!"; sleep 7; done
# ---- 2단계: 건조 CO2 293 K 등온 0.05/0.10/0.50/1.00 bar × 2씨앗 = 8건(단일 작업씩, 슬롯 나는 대로)
say "[2단계] 건조 CO2 293 K 0.05/0.10/0.50/1.00 bar × 2씨앗 (슬롯 나는 대로)"
for P in 1.00 0.50 0.10 0.05; do for S in 1 2; do wait_slots 1; disk_ok
  nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_co2_293K_${P}bar_s${S}" --temp 293 --pco2 "$P" --rh 0 --psat 2339 --workers 1 \
    --runs-root "tnf1w_runs_${TAG}_co2_${P}_s${S}" --out "tnf_results_${TAG}_co2_293K_${P}bar_s${S}.json" >> "tnf1w_${TAG}_co2_${P}_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  CO2 ${P} bar 씨앗 $S 착수 pid=$!"; sleep 4; done; done
# ---- 3단계: Widom 물 K_H ×3 + He 공극률 ×2 = 5
say "[3단계] Widom 물 K_H 298 K × 3 + He 공극률 × 2"
wait_slots 3; disk_ok
KHX_WORKERS=3 KHX_NREP=3 nohup nice -n 5 "$CZ" -u run_kh_muf16.py >> "tnf1w_${TAG}_khw.log" 2>&1 < /dev/null & PIDS+=($!); say "  물 K_H 착수 pid=$!"; sleep 10
wait_slots 2; disk_ok
HEV_WORKERS=2 HEV_NREP=2 nohup nice -n 5 "$CZ" -u run_he_muf16.py >> "tnf1w_${TAG}_hev.log" 2>&1 < /dev/null & PIDS+=($!); say "  He 공극률 착수 pid=$!"
# ---- 완주 대기
say "모든 드라이버 착수 (${#PIDS[@]}개). 완주 대기."
for p in "${PIDS[@]}"; do while kill -0 "$p" 2>/dev/null; do sleep 60; done; done
sleep 5
say "결과 파일:"; ls -la --time-style=+%H:%M tnf_results_${TAG}_water298_*.json tnf_results_${TAG}_co2_293K_*.json tnf_widom_water_${TAG}.json tnf_widom_he_${TAG}.json 2>&1 | sed 's/^/    /' | tee -a "$LOG"
n=$(ls tnf_results_${TAG}_water298_*_s?.json tnf_results_${TAG}_co2_293K_*_s?.json tnf_widom_water_${TAG}.json tnf_widom_he_${TAG}.json 2>/dev/null | grep -vc _meta)
say "T-NF-1w 사슬 종료 — 결과 JSON ${n}/14 (물 등온 2 · 사전 적재 2 · CO2 8 · Widom 2). 판정은 등록 §9 그대로 TNF_RESULTS_20260910.md 에."
