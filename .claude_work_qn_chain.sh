#!/bin/bash
# §AS — (다) T-NF-1 RH82 씨앗 3·4·5 → (가) Q_st(n) 72건. 등록 21_ZIF69_MTV/QSTN_REGISTRATION_20260920.md (자료 0건).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_qn_chain.sh > .claude_work_qn.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). 죽일 때는 PID 로(§4).
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
LOG=qn_chain.log; DRY="${DRY:-0}"; MAXC=8
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
nsim(){ pgrep -xc simulate; }
tb2w_running(){ [ "$(pgrep -fc 'run_tb2w_32[3].py')" -gt 0 ]; }
wait_slots(){ local n=$1; while [ $(( MAXC - $(nsim) )) -lt "$n" ]; do sleep 60; done; }
wait_spawn(){ local before=$1 t=0; while [ "$(nsim)" -le "$before" ] && [ $t -lt 90 ]; do sleep 5; t=$((t+5)); done; [ "$(nsim)" -gt "$before" ] || say "  !! 90 s 안에 simulate 가 늘지 않음(before=$before)"; }
disk_ok(){ local f; f=$(df -BG /mnt/c | awk 'NR==2{gsub("G","",$4); print $4}'); [ "${f:-0}" -ge 5 ] || { say "!! C: 여유 ${f} GB < 5 — 중단"; exit 9; }; }
say "================ §AS 사슬 시작 (DRY=$DRY) — T-B2w-323 종료 대기 ================"
# ⓪ T-B2w-323(§AR) 드라이버와 simulate 가 3분 연속 0 일 때까지 기다린다(다른 드라이버가 돌면 그것도 기다림)
q=0; while [ $q -lt 3 ]; do if tb2w_running || [ "$(nsim)" -gt 0 ] || [ "$(pgrep -xc network)" -gt 0 ]; then q=0; sleep 60; else q=$((q+1)); sleep 60; fi; done
say "T-B2w-323 종료 확인(simulate·network 0, 3분). 착수."
COMPS="base saIm050 saIm0583 sa50nb50 mslm050 saIm025"
for c in $COMPS; do [ -f "charged_v3/${c}_DDEC6.cif" ] || { say "!! CIF 없음 charged_v3/${c}_DDEC6.cif"; exit 3; }; done
MUF=charged_v3/muf16_DDEC6.cif; [ "$(md5sum "$MUF" | cut -c1-8)" = "8d3fba10" ] || { say "!! muf16 md5 다름"; exit 3; }
disk_ok
say "[입력 확인] dry-run base 283 K 1.00 bar / saIm0583 313 K 0.05 bar"
$CZ -u run_tnf.py --cif charged_v3/base_DDEC6.cif --tag qn_dry_base --temp 283 --pco2 1.00 --rh 0 --dry-run --runs-root qn_dryrun_base >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
$CZ -u run_tnf.py --cif charged_v3/saIm0583_DDEC6.cif --tag qn_dry_0583 --temp 313 --pco2 0.05 --rh 0 --dry-run --runs-root qn_dryrun_0583 >> "$LOG" 2>&1 || { say "!! dry-run 실패"; exit 5; }
grep -h "UnitCells\|ExternalTemperature\|ExternalPressure\|NumberOfCycles\|Forcefield" qn_dryrun_*/*/simulation.input 2>/dev/null | sort | uniq -c | sed 's/^/    /' | tee -a "$LOG"
if [ "$DRY" = 1 ]; then say "DRY 종료"; exit 0; fi
PIDS=()
# (다) T-NF-1 RH82 293 K 씨앗 3·4·5 — 짧은 3건 먼저(42 분/건)
for S in 3 4 5; do wait_slots 1; disk_ok; b=$(nsim)
  nohup "$CZ" -u run_tnf.py --cif "$MUF" --tag "muf16_rh82_s${S}" --temp 293 --pco2 0.165 --rh 82 --psat 2339 --workers 1 \
    --runs-root "tnf_runs_muf16_rh82_s${S}" --out "tnf_results_muf16_rh82_s${S}.json" >> "tnf_muf16_rh82_s${S}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  (다) RH82 씨앗 $S 착수 pid=$!"; wait_spawn "$b"; sleep 7
done
# (가) 72건 — LPT: 1.00 bar·283 K(분자 최다) 부터
for P in 1.00 0.50 0.15 0.05; do for T in 283 298 313; do for c in $COMPS; do
  wait_slots 1; disk_ok; b=$(nsim)
  nohup "$CZ" -u run_tnf.py --cif "charged_v3/${c}_DDEC6.cif" --tag "qn_${c}_${T}K_${P}bar" --temp "$T" --pco2 "$P" --rh 0 --workers 1 \
    --runs-root "qn_runs_${c}_${T}_${P}" --out "tnf_results_qn_${c}_${T}K_${P}bar.json" >> "qn_${c}_${T}_${P}.log" 2>&1 < /dev/null &
  PIDS+=($!); say "  (가) $c $T K $P bar 착수 pid=$!"; wait_spawn "$b"; sleep 7
done; done; done
say "모든 드라이버 착수 (${#PIDS[@]}개). 완주 대기."
for p in "${PIDS[@]}"; do while kill -0 "$p" 2>/dev/null; do sleep 60; done; done
sleep 5; n=$(ls tnf_results_qn_*.json 2>/dev/null | wc -l); m=$(ls tnf_results_muf16_rh82_s*.json 2>/dev/null | wc -l)
say "§AS 사슬 종료 — (가) 결과 JSON ${n}/72 · (다) ${m}/3. 판정은 등록 §3·§4 그대로."
