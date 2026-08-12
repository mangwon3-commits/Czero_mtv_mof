#!/bin/bash
# 원격 제어 세션을 tmux 안에 띄운다.
#
# [왜 tmux 인가]
#   `claude --remote-control` 은 대화형 세션이라 TTY 가 필요하다. 데스크탑 앱이
#   띄우는 claude-code 프로세스에는 이 플래그가 안 붙는다(확인함) — 그래서
#   settings.json 의 remoteControlAtStartup=true 는 CLI 에만 적용되고 앱 세션은
#   못 켠다. 별도 CLI 세션을 tmux 로 붙잡아 두는 것이 유일한 방법이다.
#
# [왜 되살리기가 필요한가]
#   08-12 13:31 윈도우 업데이트 재부팅으로 원격 제어가 끊겼다. 그 전에는 WSL
#   터미널에서 손으로 띄운 것이라 재부팅과 함께 사라졌다. ensure_guards.sh 가
#   이 스크립트를 부르므로 이제는 VM 이 다시 떠도 알아서 돌아온다.
set -u
S=claude-remote
CLAUDE=/home/mangwon1/.local/bin/claude
WORK=/home/mangwon1/mof_project

[ -x "$CLAUDE" ] || { echo "claude 없음: $CLAUDE"; exit 1; }

if tmux has-session -t "$S" 2>/dev/null; then
  exit 0
fi

tmux new-session -d -s "$S" -c "$WORK" \
  "$CLAUDE --remote-control HKHOME-desktop; echo '[원격 제어 종료됨]'; sleep 86400"
echo "[$(date '+%m-%d %H:%M')] 원격제어: tmux 세션 '$S' 시작" \
  >> /home/mangwon1/.claude_work/remote_control.log
exit 0
