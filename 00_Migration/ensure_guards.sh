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

# 윈도우 예약 작업(5분)과 crontab(10분)이 둘 다 이걸 부른다. 겹치면 같은 감시견을
# 두 번 띄운다 — watchdog.log 에 "다시 띄움"이 매번 두 줄씩 찍힌 것이 그것이다.
# 겹친 호출은 그냥 물러난다. 어차피 5분 뒤에 또 온다.
exec 9>"$W/.ensure_guards.lock"
flock -n 9 || exit 0

# 1) 유휴 종료 방지 데몬 (여벌). 경로가 절대/상대 둘 다로 뜰 수 있으므로
#    스크립트 이름만 본다 — 'bash wsl_keepalive.sh' 로 찾으면 crontab 이 띄운
#    절대경로짜리를 놓쳐 중복으로 켜진다 (실제로 2개까지 늘었다).
if ! pgrep -f 'wsl_keepalive\.sh' >/dev/null 2>&1; then
  setsid nohup bash wsl_keepalive.sh >/dev/null 2>&1 < /dev/null &
fi

# 2) 원격 제어 세션. 08-12 13:31 업데이트 재부팅으로 끊겼는데, 손으로 띄운
#    것이라 되살아나지 못했다. settings.json 의 remoteControlAtStartup=true 가
#    데스크탑 앱 세션에는 적용되지 않으므로(앱이 --remote-control 을 안 붙인다)
#    여기서 챙긴다. 세션이 이미 있으면 스크립트가 알아서 물러난다.
# 2026-08-15: remote_control.sh 대신 wireless.sh 를 부릅니다.
#   옛 스크립트는 tmux has-session 만 보는데, tmux 안의 명령이
#   "claude ...; echo 종료됨; sleep 86400" 이라 **claude 가 죽어도 세션은
#   24시간 남습니다.** 그러면 has-session 이 참을 돌려주어 되살리기를
#   통째로 건너뜁니다 -- 화면엔 [원격 제어 종료됨] 만 떠 있는데.
#   wireless.sh 는 세션이 아니라 **실행파일 경로로 프로세스**를 보므로
#   그 좀비 상태를 잡아 정리하고 다시 띄웁니다.
bash /home/mangwon1/mof_project/wireless.sh >/dev/null 2>&1

# 3) LAMMPS 감시견. 체인이 이미 끝났거나 감시견이 스스로 포기했으면 건드리지 않는다.
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
