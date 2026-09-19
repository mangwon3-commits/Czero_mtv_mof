#!/bin/bash
# T-NF-1w-2 — MUF-16 물 항 온도 의존 273 K (등록 TNF_REGISTRATION_20260910.md §9-보완, 자료 0건, 09-19 23:1x).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tnf1w2_chain.sh > .claude_work_tnf1w2.out 2>&1 < /dev/null &
# 슬롯 확인은 "새 실행 폴더에 simulate 가 붙었는지"(cwd) 로 — 전체 개수 비교의 거짓 경보(22:46) 교훈.
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
LOG=tnf1w2_chain.log; DRY="${DRY:-0}"; MAXC=8
CIF=charged_v3/muf16_DDEC6.cif; TAG=muf16; T=273; PSAT=611
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
nsim(){ pgrep -xc simulate; }
wait_slots(){ local n=$1; while [ $(( MAXC - $(nsim) )) -lt "$n" ]; do sleep 60; done; }
wait_dir(){ local d=$1 t=0; while [ $t -lt 120 ]; do for p in $(pgrep -x simulate); do case "$(readlink /proc/$p/cwd 2>/dev/null)" in *"/$d/"*|*"/$d") return 0;; esac; done; sleep 5; t=$((t+5)); done; say "  !! 120 s 안에 $d 에 simulate 가 안 붙음 — 드라이버 로그 확인"; }
disk_ok(){ local f; f=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4); print $4}'); [ "${f:-0}" -ge 5 ] || { say "!! C: 여유 ${f} GB < 5 — 중단"; exit 9; }; }
say "================ T-NF-1w-2 사슬 시작 (DRY=$DRY) ================"
M0=$(md5sum "$CIF" | cut -c1-32); [ "${M0:0:8}" = "8d3fba10" ] || { say "!! CIF md5 다름"; exit 3; }
[ "$(pgrep -xc network)" = 0 ] || { say "!! Zeo++ 실행 중"; exit 4; }
disk_ok
say "[입력 확인] dry-run 273 K 순수 물 / 사전 적재"
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_w273_dry" --temp $T --pco2 0 --rh 50,100 --psat $PSAT --dry-run --runs-root "tnf1w2_dryrun_w" >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
$CZ -u run_tnf.py --cif "$CIF" --tag "${TAG}_p273_dry" --temp $T --pco2 0 --rh 100 --psat $PSAT --preload-water 110 --dry-run --runs-root "tnf1w2_dryrun_p" >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
KHX_TEMP=273 $CZ -c "import run_kh_muf16 as m; print('  kh 래퍼', m.K.T.TEMP, m.OUT.split('/')[-1], m.K.RUNS_ROOT.split('/')[-1])" >> "$LOG" 2>&1 || { say "!! 래퍼 import 실패"; exit 6; }
grep -h "UnitCells\|ExternalTemperature\|ExternalPressure\|CreateNumberOfMolecules" tnf1w2_dryrun_*/*/simulation.input 2>/dev/null | sort | uniq -c | sed 's/^/    /' | tee -a "$LOG"; tail -n 1 "$LOG" >/dev/null
if [ "$DRY" = 1 ]; then say "DRY 종료"; exit 0; fi
PIDS=()
say "[1단계] 사전 적재 110 × 2 (LPT — 머물면 이것이 가장 김)"
for S in 1 2; do wait_slots 1; disk_ok; d="tnf1w2_runs_${TAG}_pre_s${S}"
  nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_w273_pre110_s${S}" --temp $T --pco2 0 --rh 100 --psat $PSAT --preload-water 110 --workers 1 \
    --runs-root "$d" --out "tnf_results_${TAG}_water273_pre110_s${S}.json" >> "tnf1w2_${TAG}_pre_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  사전 적재 씨앗 $S 착수 pid=$!"; wait_dir "$d"; sleep 2; done
say "[2단계] 순수 물 빈 출발 RH50/100 × 2 (워커 2+2)"
for S in 1 2; do wait_slots 2; disk_ok; d="tnf1w2_runs_${TAG}_w_s${S}"
  nohup "$CZ" -u run_tnf.py --cif "$CIF" --tag "${TAG}_w273_s${S}" --temp $T --pco2 0 --rh 50,100 --psat $PSAT --workers 2 --seed-stagger 5 \
    --runs-root "$d" --out "tnf_results_${TAG}_water273_s${S}.json" >> "tnf1w2_${TAG}_w_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  빈 출발 씨앗 $S 착수 pid=$!"; wait_dir "$d"; sleep 2; done
say "[3단계] 물 Widom 273 K × 3"
wait_slots 3; disk_ok
KHX_TEMP=273 KHX_WORKERS=3 KHX_NREP=3 nohup nice -n 5 "$CZ" -u run_kh_muf16.py >> "tnf1w2_${TAG}_khw.log" 2>&1 < /dev/null & PIDS+=($!); say "  Widom 273 K 착수 pid=$!"; wait_dir "tnf1w_khw_runs_273K"
say "모든 드라이버 착수 (${#PIDS[@]}개). 완주 대기."
for p in "${PIDS[@]}"; do while kill -0 "$p" 2>/dev/null; do sleep 60; done; done
sleep 5
n=$(ls tnf_results_${TAG}_water273_s?.json tnf_results_${TAG}_water273_pre110_s?.json tnf_widom_water_${TAG}_273K.json 2>/dev/null | wc -l)
say "T-NF-1w-2 사슬 종료 — 결과 JSON ${n}/5. 판정 A~C 는 등록 §9-보완 그대로 TNF_RESULTS_20260910.md 에."
