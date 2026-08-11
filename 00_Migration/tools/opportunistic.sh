#!/bin/bash
# 노는 코어를 메운다 — 파이프라인이 순차라서 생기는 유휴를 없애는 상시 스케줄러.
# MIGRATION.md 3-11 의 원칙 구현.
#
# [대상 — 겹쳐도 안전한 것만]
#   파이프라인이 나중에 같은 것을 또 돌리므로, 자격 요건 두 개를 갖춘 것만 띄운다.
#     run_density_map.py  O  이어받기 + already_running() 단일 인스턴스 검사
#     run_aryl_gcmc.py    O  이어받기 + occupied_by_other() 디렉터리 점유 검사
#     risk_screen.py      X  **둘 다 없다.** lmp/ 에서 겹치면 이완이 깨진다.
#
# [2026-08-07 21:00 개정]
#   밀도맵이 끝나서 다음 대상인 아릴 GCMC 로 옮긴다. 남은 27작업은 전부 독립이고
#   run_aryl_gcmc.py 는 자격 요건 둘을 다 갖췄다.
#
# [연속 확인이 필요한 이유]
#   한 번만 보면 작업이 끝나고 다음이 시작되는 찰나의 빈틈에 반응해 곧 채워질
#   코어에 뛰어든다. 유령 감지에서 실제로 오탐을 냈던 것과 같은 실수다.
set -u
P=/home/mangwon1/mof_project/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin
export RASPA_DIR=/home/mangwon1/RASPA/simulations
CORES=8
MIN_IDLE=2
CONFIRM=3

say() { echo ">>> [$(date +%m-%d\ %H:%M)] 기회주의: $*"; }

# `pgrep -c` 는 일치가 없으면 "0" 을 찍으면서 **종료코드 1** 을 낸다. 그래서
# `$(pgrep -c x || echo 0)` 로 쓰면 "0\n0" 이 되어 산술 확장이 깨진다. 실제로 깨졌다.
count() {
  local n
  n=$(pgrep -c "$1" 2>/dev/null)
  case "$n" in ''|*[!0-9]*) echo 0;; *) echo "$n";; esac
}
busy() { echo $(( $(count simulate) + $(count lmp_serial) )); }

streak=0
say "감시 시작 — 대상 아릴 GCMC (여유 $MIN_IDLE 이상이 ${CONFIRM}회 연속이면 기동)"

while true; do
  if [ -f "$P/aryl_results.json" ]; then
    say "아릴 결과 존재 — 스케줄러 종료"
    exit 0
  fi
  if pgrep -f "python run_aryl_gcmc.py" > /dev/null 2>&1; then
    say "파이프라인이 이미 아릴을 돌리는 중 — 스케줄러 종료"
    exit 0
  fi

  b=$(busy); idle=$((CORES - b))
  if [ "$idle" -ge "$MIN_IDLE" ]; then streak=$((streak+1)); else streak=0; fi

  if [ "$streak" -ge "$CONFIRM" ]; then
    say "유휴 코어 ${idle}개가 ${CONFIRM}회 연속 확인됨 -> 아릴 GCMC 시작 (워커 ${idle})"
    cd "$P" || exit 1
    ARYL_WORKERS=$idle PATH="$CZ:$PATH" stdbuf -oL "$CZ/python" run_aryl_gcmc.py \
      > "$W/aryl_gcmc.log" 2>&1
    rc=$?
    if [ -f "$P/aryl_results.json" ]; then
      say "아릴 GCMC 완료 (aryl_results.json)"
    else
      say "아릴 GCMC 가 결과 없이 종료 (rc=$rc, aryl_gcmc.log 확인)"
    fi
    exit 0
  fi
  sleep 300
done
