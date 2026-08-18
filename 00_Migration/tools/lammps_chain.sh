#!/bin/bash
P=/home/mangwon1/mof_project/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
LM=/home/mangwon1/miniconda3/envs/lammps_mof/bin
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin
export RASPA_DIR=/home/mangwon1/RASPA/simulations
cd "$P" || exit 1

# 종료코드는 **반드시 먼저 변수에 담는다.**
#
# 원래 이렇게 썼다:
#     echo ">>> [$(date +%H:%M)] saIm 종료코드 $?"
# 명령 치환 $(date) 가 먼저 실행되고 성공하므로, 그 뒤의 $? 는 python 이 아니라
# **date 의 종료코드**가 된다. 즉 무조건 0 이다.
#
# 2026-08-12 에 이것 때문에 두 단계가 OOM 으로 죽었는데도 로그에 "종료코드 0",
# "전체 완료"가 찍혔다. 감시견은 '전체 완료'를 보고 감시를 끝냈다(16:03).
# 실패가 성공으로 보고되면 감시 장치 전체가 무력화된다.
run_stage() {
  local label="$1"; shift
  echo ">>> [$(date +%H:%M)] $label 시작"
  "$@"
  local rc=$?
  if [ "$rc" -eq 0 ]; then
    echo ">>> [$(date +%H:%M)] $label 종료코드 0"
  else
    echo ">>> [$(date +%H:%M)] $label **실패** 종료코드 $rc"
  fi
  return "$rc"
}

fail=0
run_stage "saIm 5종" env PATH="$LM:$CZ:$PATH" stdbuf -oL "$LM/python" \
  risk_screen.py > "$W/lammps_saim.log" 2>&1 || fail=1
run_stage "아릴 12종" env PATH="$LM:$CZ:$PATH" stdbuf -oL "$LM/python" \
  risk_screen.py aryl_scan_index.json aryl > "$W/lammps_aryl.log" 2>&1 || fail=1

# '전체 완료'는 **정말로 다 됐을 때만** 찍는다. 감시견의 종료 조건이기 때문이다.
if [ "$fail" -eq 0 ]; then
  echo ">>> [$(date +%H:%M)] 전체 완료"
else
  echo ">>> [$(date +%H:%M)] 일부 단계 실패 — 완료로 표시하지 않음"
fi
exit "$fail"
