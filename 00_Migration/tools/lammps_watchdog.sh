#!/bin/bash
# LAMMPS 체인 감시견. 1시간마다 상태를 보고, 죽었거나 매달려 있으면 재실행한다.
#
# [왜 '죽음'만 보면 안 되는가 — 실측]
#   2026-08-09 10:54 에 띄운 체인이 24시간 뒤에도 프로세스는 살아 있는데
#   lmp_serial 0개, 로그 갱신 없음 상태였다. ProcessPoolExecutor 의 워커가
#   사라지면 부모가 영원히 기다리는 형태로 **살아 있는 채 매달린다.**
#   그래서 판정은 프로세스 생존이 아니라 **진전(파일 갱신)** 으로 한다.
#
# [판정 규칙]
#   완료  = lammps_chain.log 에 '전체 완료'
#   진전  = lmp/, lmp_aryl/, lammps_chain.log 중 최근 60분 안에 갱신된 것이 있다
#   고장  = 완료도 진전도 아니다 (죽었든 매달렸든 동일 취급)
#
# [재실행]
#   깨끗이 죽이고(lmp_serial 까지), 작업 디렉터리를 지우고, 처음부터.
#   risk_screen 은 이어받기가 없으므로 부분 산출물을 남기면 오히려 위험하다.
#   3회 넘게 실패하면 포기하고 로그에 남긴다 — 무한 재시도는 더 나쁘다.
set -u
W=/home/mangwon1/.claude_work
P=/home/mangwon1/mof_project/21_ZIF69_MTV
MAX_RETRY=3
STALL_SEC=3600
# 확인 간격은 정지 판정과 **분리한다.**
#
# 원래 1시간마다 확인했다. 그런데 08-12 12:45~13:25 에 감시견 자신이 5분마다
# 죽고 되살아나는 상황이 벌어지자, 새로 뜬 감시견은 시작 직후 한 번 보고
# (그때는 아직 진전이 최근이라 통과) 잠들었다가 1시간을 못 채우고 죽었다.
# **그래서 감시견이 9번 떴는데 고장을 한 번도 못 잡았다.** 그동안 LAMMPS 는
# 12:47 에 죽어 76분간 방치됐다.
# 확인을 5분마다 하면 수명이 짧아도 판정은 제대로 된다. 판정 기준(1시간 무진전)은
# 그대로다.
CHECK_SEC=300

say() { echo "[$(date +%m-%d\ %H:%M)] 감시견: $*"; }

# 로그와 작업 디렉터리를 통틀어 가장 최근에 손댄 시각(epoch). 하나라도 최근이면
# 진전이 있는 것이다.
newest_mtime() {
  {
    for f in "$W/lammps_chain.log" "$W/lammps_saim.log" "$W/lammps_aryl.log"; do
      [ -f "$f" ] && stat -c %Y "$f"
    done
    find "$P/lmp" "$P/lmp_aryl" -type f -printf '%T@\n' 2>/dev/null | cut -d. -f1
    echo 0
  } | sort -n | tail -1
}

relaunch() {
  pkill -f "bash lammps_chain.sh" 2>/dev/null
  pkill -f risk_screen.py 2>/dev/null
  pkill lmp_serial 2>/dev/null
  sleep 5
  pkill -9 -f risk_screen.py 2>/dev/null
  pkill -9 lmp_serial 2>/dev/null
  rm -rf "$P/lmp" "$P/lmp_aryl"
  cd "$W" || exit 1
  setsid nohup bash lammps_chain.sh >> lammps_chain.log 2>&1 < /dev/null &
  sleep 10
  say "재실행함 (risk $(pgrep -cf risk_screen.py 2>/dev/null || echo 0) / lmp $(pgrep -c lmp_serial 2>/dev/null || echo 0))"
}

retries=0
say "감시 시작 (간격 1시간, 정지 판정 ${STALL_SEC}초, 최대 재시도 ${MAX_RETRY}회)"

while true; do
  if grep -q "전체 완료" "$W/lammps_chain.log" 2>/dev/null; then
    say "체인 완료 — 감시 종료"
    exit 0
  fi

  now=$(date +%s)
  last=$(newest_mtime)
  age=$(( now - last ))

  if [ "$age" -lt "$STALL_SEC" ]; then
    : # 진전 있음 — 조용히 지나간다
  else
    retries=$((retries+1))
    if [ "$retries" -gt "$MAX_RETRY" ]; then
      say "재시도 ${MAX_RETRY}회 초과 — 포기합니다. lammps_saim.log / lammps_aryl.log 를 직접 봐야 합니다"
      # 바깥(윈도우)의 5분 감시가 이 감시견을 되살려 재시도 횟수를 0으로 되돌리면
      # 사실상 무한 재시도가 된다. 포기했다는 사실을 파일로 남겨 그것을 막는다.
      touch "$W/.watchdog_gave_up"
      exit 1
    fi
    say "고장 감지 (${age}초 무진전, risk $(pgrep -cf risk_screen.py 2>/dev/null || echo 0) / lmp $(pgrep -c lmp_serial 2>/dev/null || echo 0)) — 재실행 ${retries}회차"
    relaunch
  fi
  sleep "$CHECK_SEC"
done
