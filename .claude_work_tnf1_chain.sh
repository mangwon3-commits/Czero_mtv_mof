#!/bin/bash
# ============================================================================
# T-NF-1 (MUF-16 Co) 무인 앞단 + 생산 사슬 — 등록 TNF_REGISTRATION_20260910.md §1 (09-19 (가) 보완)
#   활성화 CIF(게스트 물 제거본) -> GFN-FF 셀 고정 이완 -> PACMAN DDEC6 -> [RASPA 0 창] Zeo++ 관문
#   -> run_tnf.py --dry-run -> 생산: 293 K · 0.165 bar · RH 0/50/82/100 (psat 2339) 씨앗 2, 8코어
#   -> 298 K RH100 한 점(psat 3169, 물 등온 앵커 ③) 씨앗 2  +  Widom Q_st(CO₂) 293 K 반복 2 (앵커 ②)
#
#   .claude_work_tnf_chain.sh(09-10, T-NF-0) 를 그대로 물려받고 재료 표와 뒤쪽 두 단계만 더했습니다.
#   · 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). · 아무것도 죽이지 않습니다(§4).
#   · 기존 러너를 고치지 않습니다 — relax_tnf.py · charge_tnf.py · run_tnf.py · run_widom_tnf.py 만 부릅니다.
#   · TNF_DRY=1 이면 외부 명령을 실행하지 않고 로그에 찍기만 합니다.
#   띄우는 법:  cd /home/mangwon1/mof_project && setsid nohup bash .claude_work_tnf1_chain.sh < /dev/null > /dev/null 2>&1 &
#   PID:        ps -eo pid,args | grep [t]nf1_chain      ($! 는 setsid 의 PID 라 곧 사라짐 — §4)
#   마른 확인:  TNF_DRY=1 bash .claude_work_tnf1_chain.sh
# ============================================================================
set -u
ROOT=/home/mangwon1/mof_project
HERE=$ROOT/21_ZIF69_MTV
cd "$HERE" || exit 1
export RASPA_DIR=$HOME/RASPA/simulations
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin/python
LM=/home/mangwon1/miniconda3/envs/lammps_mof/bin/python
LMPATH=/home/mangwon1/miniconda3/envs/lammps_mof/bin:/home/mangwon1/miniconda3/envs/czeromof/bin
export XTB_BIN=${XTB_BIN:-/home/mangwon1/miniconda3/envs/spectra/bin/xtb}
L=$HERE/tnf1_chain.log
DRY=${TNF_DRY:-0}
CORES=${TNF_CORES:-8}
DISK_MIN_GB=${TNF_DISK_MIN_GB:-5}
POLL=${TNF_POLL:-300}

say() { echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$L"; }
run() { if [ "$DRY" = 1 ]; then say "DRY  $*"; return 0; fi; say "실행 $*"; "$@" >> "$L" 2>&1; local rc=$?; say "  rc=$rc  ($1 …)"; return $rc; }
nsim() { local n; n=$(pgrep -xc simulate 2>/dev/null); echo "${n:-0}"; }

disk_guard() {   # 게스트 df / 는 호스트 C: 를 못 봅니다 — 반드시 /mnt/c (CLAUDE.md §5, 09-07 사고)
  local free; free=$(df -BG --output=avail /mnt/c 2>/dev/null | tail -1 | tr -dc '0-9')
  if [ -z "$free" ]; then say "!! df /mnt/c 를 못 읽었습니다 — 착수하지 않습니다."; [ "$DRY" = 1 ] && return 0; return 1; fi
  say "디스크 C: ${free} GB 여유 (문턱 ${DISK_MIN_GB} GB)"
  if [ "$free" -lt "$DISK_MIN_GB" ]; then say "!! C: 여유 부족 — 착수하지 않습니다."; [ "$DRY" = 1 ] && return 0; return 1; fi
  return 0
}
wait_sim_zero() {   # Zeo++ 는 RASPA 와 같이 띄우지 않습니다 (CLAUDE.md §5)
  if [ "$DRY" = 1 ]; then say "DRY  대기: pgrep -xc simulate == 0"; return 0; fi
  local n; n=$(nsim); [ "$n" -gt 0 ] && say "관문 대기: simulate ${n}건"
  while [ "$(nsim)" -gt 0 ]; do sleep "$POLL"; done
  while [ "$(pgrep -fc 'risk_screen_v3_su[b]')" -gt 0 ] || [ "$(pgrep -xc network)" -gt 0 ]; do sleep 30; done
  say "관문 창 열림 (simulate 0, 다른 관문 없음)"
}
wait_cores() {
  local need=$1
  if [ "$DRY" = 1 ]; then say "DRY  대기: simulate 수 <= $((CORES - need))"; return 0; fi
  local n; n=$(nsim); [ $((n + need)) -gt "$CORES" ] && say "코어 대기: simulate ${n}건 + 필요 ${need} > ${CORES}"
  while [ $(( $(nsim) + need )) -gt "$CORES" ]; do sleep "$POLL"; done
  say "코어 확보: simulate $(nsim)건, ${need}건 추가 가능"
}
STAGED=""
cleanup_stage() { local f; for f in $STAGED; do [ -f "$f" ] && { rm -f "$f"; say "정리: v3 서랍에서 회수 $f"; }; done; STAGED=""; }
trap cleanup_stage EXIT INT TERM

TAG=muf16
CIF=external_cif/MUF-16_Co_activated_P1.cif
T=293; PCO2=0.165; RH=0,50,82,100; PSAT=2339          # MUF16_ANCHORS §4 (가)
T2=298; RH2=100; PSAT2=3169                            # 물 등온 앵커 ③ 는 298 K — 한 점 추가

say "======================================================================"
say "T-NF-1 사슬 착수 (DRY=${DRY}, 코어 상한 ${CORES}) — $TAG  ${T} K · CO2 ${PCO2} bar · RH ${RH} (+ ${T2} K RH ${RH2})"
say "등록 TNF_REGISTRATION_20260910.md §1 (09-19 (가) 보완) · 앵커 MUF16_ANCHORS_20260918.md §2"

run "$CZ" -u -c "import sys; sys.path.insert(0,'$HERE'); import ff_gate; ok,m=ff_gate.md5_gate(); print(m); sys.exit(0 if ok else 3)"
FFRC=$?; if [ "$FFRC" != 0 ] && [ "$DRY" != 1 ]; then say "!! 힘장 파일 관문 실패(rc=$FFRC). 멈춥니다."; exit 3; fi

# (0) 구조 — 게스트 물 제거본(strip_guests_tnf.py, 조성 C64H48Co4N8O32 확인 후 기록된 파일)
[ -f "$CIF" ] || { say "  [미착수] 활성화 CIF 없음: $CIF"; exit 2; }
say "  구조   $CIF  (md5 $(md5sum "$CIF" | cut -c1-32))"
run "$CZ" -u audit_external_cif.py --no-write "$CIF"

# (1) 이완
RCIF=relax_tnf/${TAG}_relaxed.cif
if [ -f "$RCIF" ]; then say "  [이완 이미있음] $RCIF"; else
  disk_guard || { say "  !! 디스크 관문 — 중단"; exit 1; }
  run env RELAX_WORKERS=2 nice -n 19 "$CZ" -u relax_tnf.py --job "${TAG}=${CIF}"
fi
if [ ! -f "$RCIF" ] && [ "$DRY" != 1 ]; then say "  [앞단 실패] 이완본이 없습니다 — 등록 §1 '앞단 실패는 그 자체가 결과'."; exit 1; fi

# (2) 전하
QCIF=charged_v3/${TAG}_DDEC6.cif
if [ -f "$QCIF" ]; then say "  [전하 이미있음] $QCIF"; else run nice -n 10 "$CT" -u charge_tnf.py --tag "$TAG" --cif "$RCIF"; fi
if [ ! -f "$QCIF" ] && [ "$DRY" != 1 ]; then say "  [앞단 실패] 전하 CIF 가 없습니다."; exit 1; fi

# (3) Zeo++ 관문 — LCD_drop 분모는 ZIF-69 모체라 판정에 안 씀, PLD 절대 문턱(3.3 Å)만 뜻 보존
GJSON=risk_results_tnf_${TAG}.json
if [ -f "$GJSON" ]; then say "  [관문 이미있음] $GJSON"; else
  wait_sim_zero
  disk_guard || say "  !! 디스크 관문 — 관문 건너뜀"
  [ -f risk_results_v3sub.json ] && run mv risk_results_v3sub.json "risk_results_v3sub.before_tnf1_$(date +%m%d%H%M).json"
  SRC_V3=relax_v3/ZIF69_${TAG}_relaxed.cif
  if [ -f "$SRC_V3" ]; then say "  !! v3 서랍에 이미 $SRC_V3 — 건드리지 않습니다."; else
    if [ "$DRY" = 1 ]; then say "DRY  cp $RCIF $SRC_V3 (관문 stage 직후 회수)"; else cp "$RCIF" "$SRC_V3" && STAGED="$STAGED $SRC_V3"; say "  임시 배치 $SRC_V3"; fi
  fi
  if [ "$DRY" = 1 ]; then say "DRY  env PATH=$LMPATH:\$PATH RISK_SUB_TAGS=base,$TAG nice -n 10 $LM -u risk_screen_v3_sub.py"; else
    env PATH="$LMPATH:$PATH" RISK_SUB_TAGS="base,$TAG" nice -n 10 "$LM" -u risk_screen_v3_sub.py >> "$L" 2>&1 < /dev/null &
    GPID=$!; say "  관문 착수 pid=$GPID (RISK_SUB_TAGS=base,$TAG)"
    for _ in $(seq 1 240); do [ -f "structures_v3sub_stage/ZIF69_${TAG}.cif" ] && break; kill -0 "$GPID" 2>/dev/null || break; sleep 5; done
    cleanup_stage; wait "$GPID"; say "  관문 rc=$?"
  fi
  [ -f risk_results_v3sub.json ] && run cp risk_results_v3sub.json "$GJSON"
fi
run "$CZ" -u -c "
import json,os
p='$GJSON'
if os.path.exists(p):
    d=json.load(open(p,encoding='utf-8')); rows=d.get('rows',d) if isinstance(d,dict) else d
    for r in (rows if isinstance(rows,list) else rows.values()):
        if isinstance(r,dict) and (r.get('tag') or r.get('name')) in ('base','$TAG'):
            print('  [Zeo++]',r.get('tag') or r.get('name'),'PLD',r.get('PLD'),'LCD',r.get('LCD'),'AV',r.get('AV_cm3g') or r.get('AV'),'pass',r.get('pass'))
else: print('  관문 결과 없음:',p)
"

# (4) 입력 확인
run "$CZ" -u run_tnf.py --cif "$QCIF" --tag "${TAG}_T-NF-1" --temp "$T" --pco2 "$PCO2" --rh "$RH" --psat "$PSAT" --dry-run --runs-root "tnf_dryrun_${TAG}"
run "$CZ" -u run_tnf.py --cif "$QCIF" --tag "${TAG}_298rh100" --temp "$T2" --pco2 "$PCO2" --rh "$RH2" --psat "$PSAT2" --dry-run --runs-root "tnf_dryrun_${TAG}_298"
run "$CZ" -u run_widom_tnf.py --cif "$QCIF" --tag "$TAG" --temp "$T" --reps 2 --dry-run

# (5) 생산 — 293 K 네 RH 점 × 씨앗 2, 워커 4×2 = 코어 8
say "  [생산] T-NF-1/$TAG — 씨앗 2 × RH 4점, 워커 4×2."
wait_cores 8
disk_guard || { say "  !! 디스크 관문 — 생산 취소"; exit 1; }
for S in 1 2; do
  if [ "$DRY" = 1 ]; then say "DRY  nohup $CZ -u run_tnf.py --cif $QCIF --tag ${TAG}_s${S} --temp $T --pco2 $PCO2 --rh $RH --psat $PSAT --workers 4 --seed-stagger 5 --runs-root tnf_runs_${TAG}_s${S} --out tnf_results_${TAG}_s${S}.json"; else
    nohup "$CZ" -u run_tnf.py --cif "$QCIF" --tag "${TAG}_s${S}" --temp "$T" --pco2 "$PCO2" --rh "$RH" --psat "$PSAT" --workers 4 --seed-stagger 5 \
      --runs-root "tnf_runs_${TAG}_s${S}" --out "tnf_results_${TAG}_s${S}.json" >> "tnf_${TAG}_s${S}.log" 2>&1 < /dev/null &
    say "  씨앗 $S 착수 pid=$!  -> tnf_${TAG}_s${S}.log"; sleep 7
  fi
done
[ "$DRY" != 1 ] && { wait; say "  [생산 종료] $TAG 293 K 씨앗 2회 전부 끝"; }

# (6) 298 K RH100 한 점(앵커 ③) 씨앗 2  +  Widom Q_st 293 K 반복 2 (앵커 ②) — 합쳐 코어 4
wait_cores 4
for S in 1 2; do
  if [ "$DRY" = 1 ]; then say "DRY  nohup $CZ -u run_tnf.py --cif $QCIF --tag ${TAG}_298rh100_s${S} --temp $T2 --pco2 $PCO2 --rh $RH2 --psat $PSAT2 --workers 1 --runs-root tnf_runs_${TAG}_298rh100_s${S} --out tnf_results_${TAG}_298rh100_s${S}.json"; else
    nohup "$CZ" -u run_tnf.py --cif "$QCIF" --tag "${TAG}_298rh100_s${S}" --temp "$T2" --pco2 "$PCO2" --rh "$RH2" --psat "$PSAT2" --workers 1 \
      --runs-root "tnf_runs_${TAG}_298rh100_s${S}" --out "tnf_results_${TAG}_298rh100_s${S}.json" >> "tnf_${TAG}_298rh100_s${S}.log" 2>&1 < /dev/null &
    say "  298 K RH100 씨앗 $S 착수 pid=$!"; sleep 7
  fi
done
if [ "$DRY" = 1 ]; then say "DRY  $CZ -u run_widom_tnf.py --cif $QCIF --tag $TAG --temp $T --reps 2"; else
  nohup "$CZ" -u run_widom_tnf.py --cif "$QCIF" --tag "$TAG" --temp "$T" --reps 2 >> "tnf_widom_${TAG}.log" 2>&1 < /dev/null &
  say "  Widom 착수 pid=$!  -> tnf_widom_${TAG}.log"
  wait; say "  [종료] 298 K 점·Widom 전부 끝"
fi
say "======================================================================"
say "T-NF-1 사슬 종료. 판정은 등록 §1 (가) 앵커 셋 그대로 TNF_RESULTS_20260910.md 에."
say "  · 앞단: relax_tnf/${TAG}_relaxed.cif · charged_v3/${TAG}_DDEC6.cif · $GJSON"
say "  · GCMC: tnf_results_${TAG}_s{1,2}.json · tnf_results_${TAG}_298rh100_s{1,2}.json · tnf_widom_${TAG}.json"
