#!/bin/bash
# 윈도우 쪽 예약 작업이 5분마다 부른다. 없는 것만 되살린다.
#
# [왜 안쪽이 아니라 바깥에서 부르는가 — 2026-08-10 의 교훈]
#   WSL VM 이 08-10 17:25 에 스스로 꺼졌다. 그때 안에서는 wsl_keepalive.sh 가
#   돌고 있었고 .wslconfig 에도 vmIdleTimeout=-1 이 들어 있었다. 둘 다 못 막았다.
#   VM 이 꺼지면 안에 있던 감시견도 같이 죽으므로, 안쪽 장치만으로는 원리상
#   복구가 불가능하다. 되살릴 주체는 반드시 VM 바깥에 있어야 한다.
#
#   crontab @reboot 은 keepalive 만 띄웠고 감시견은 안 띄웠다. 그래서 08-10
#   17:25 에 VM 이 다시 떴을 때 keepalive 만 살아나고 LAMMPS 는 39시간 동안
#   죽은 채였다. 여기서 감시견까지 챙기는 이유다.
set -u
W=/home/mangwon1/.claude_work
cd "$W" || exit 0

# 1) 유휴 종료 방지 데몬 (여벌). 경로가 절대/상대 둘 다로 뜰 수 있으므로
#    스크립트 이름만 본다 — 'bash wsl_keepalive.sh' 로 찾으면 crontab 이 띄운
#    절대경로짜리를 놓쳐 중복으로 켜진다 (실제로 2개까지 늘었다).
if ! pgrep -f 'wsl_keepalive\.sh' >/dev/null 2>&1; then
  setsid nohup bash wsl_keepalive.sh >/dev/null 2>&1 < /dev/null &
fi

# 2) LAMMPS 감시견. 체인이 이미 끝났거나 감시견이 스스로 포기했으면 건드리지 않는다.
if [ -f "$W/.watchdog_gave_up" ]; then
  exit 0
fi
if grep -q "전체 완료" "$W/lammps_chain.log" 2>/dev/null; then
  exit 0
fi
if ! pgrep -f 'lammps_watchdog\.sh' >/dev/null 2>&1; then
  echo "[$(date '+%m-%d %H:%M')] 바깥감시: 감시견이 없어 다시 띄움" >> "$W/watchdog.log"
  setsid nohup bash lammps_watchdog.sh >> watchdog.log 2>&1 < /dev/null &
fi
exit 0
