#!/bin/bash
# 원격(무선) 접속을 확실히 살려 둔다. /wireless 슬래시 명령이 이것을 부른다.
#
# [기존 remote_control.sh 의 함정 — 이 스크립트가 존재하는 이유]
#   그 스크립트는 이렇게 판정합니다.
#
#       if tmux has-session -t claude-remote; then exit 0; fi
#
#   그런데 tmux 안에서 도는 명령이
#
#       claude --remote-control ...; echo '[원격 제어 종료됨]'; sleep 86400
#
#   입니다. **claude 가 죽어도 sleep 86400 이 세션을 24시간 붙잡습니다.**
#   그러면 has-session 은 참을 돌려주고, 되살리기 로직이 통째로 건너뜁니다.
#   화면에는 '[원격 제어 종료됨]' 만 떠 있는데 스크립트는 "정상"이라고 보고합니다.
#
#   이 프로젝트에서 반복된 사고 유형이 정확히 이것입니다 — **실패가 결과처럼
#   보이는 것.** 그래서 여기서는 세션이 아니라 **프로세스**를 봅니다.
#
# 사용:
#   bash wireless.sh          점검하고 필요하면 되살림
#   bash wireless.sh --force  살아 있어도 죽이고 새로 띄움
set -u
S=claude-remote
DEVICE=HKHOME-desktop
CLAUDE=/home/mangwon1/.local/bin/claude
WORK=/home/mangwon1/mof_project
LOG=/home/mangwon1/.claude_work/remote_control.log
GUARD=/home/mangwon1/.claude_work/ensure_guards.sh

log() { echo "[$(date '+%m-%d %H:%M')] wireless: $*" >> "$LOG"; }

# [검사를 두 번 고쳤습니다 — 2026-08-15]
#
#   1판: tmux has-session 만 봄
#        -> sleep 86400 이 세션을 붙잡아, claude 가 죽어도 "정상" 이라고 함
#
#   2판: pgrep -f -- "--remote-control"
#        -> **이것도 틀립니다.** 그 문자열이 세 프로세스의 cmdline 에 다 있습니다.
#
#             714  tmux: server   tmux new-session ... claude --remote-control ...
#             715  sh             sh -c "claude --remote-control ...; sleep 86400"
#             716  claude         /home/.../claude --remote-control HKHOME-desktop
#
#           claude(716)가 죽어도 714·715 는 남아 여전히 참이 됩니다.
#           심지어 이 검사를 돌리는 grep 자기 자신까지 잡혔습니다.
#
#   3판(현재): **실행파일 경로로 시작하는 줄**만 셉니다. 716 하나만 잡힙니다.
#              comm 이 claude 인지도 함께 봅니다.
remote_pid() {
    local p
    for p in $(pgrep -f "^${CLAUDE} --remote-control" 2>/dev/null); do
        if [ "$(ps -o comm= -p "$p" 2>/dev/null)" = "claude" ]; then
            echo "$p"
            return 0
        fi
    done
    return 1
}
alive() { remote_pid > /dev/null; }
has_session() { tmux has-session -t "$S" 2>/dev/null; }

start() {
  tmux new-session -d -s "$S" -c "$WORK" \
    "$CLAUDE --remote-control $DEVICE; echo '[원격 제어 종료됨]'; sleep 86400"
  sleep 4
}

[ -x "$CLAUDE" ] || { echo "  !! claude 실행파일 없음: $CLAUDE"; exit 1; }

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

echo "=== 진단 ==="
S_OK=0; P_OK=0
has_session && S_OK=1
alive && P_OK=1
printf "  tmux 세션 '%s'   %s\n" "$S" "$([ $S_OK -eq 1 ] && echo 있음 || echo 없음)"
printf "  원격 제어 프로세스   %s\n" "$([ $P_OK -eq 1 ] && echo 살아있음 || echo 죽음)"

echo
echo "=== 조치 ==="
if [ "$FORCE" -eq 1 ]; then
  echo "  --force: 죽이고 새로 띄웁니다"
  # pkill -f -- "--remote-control" 로 쓰면 **tmux 서버까지 죽입니다**(위 주석 참고).
  # 세션만 끊고, 남은 claude 프로세스가 있으면 pid 로 정확히 지목해 끕니다.
  p=$(remote_pid) && kill "$p" 2>/dev/null
  tmux kill-session -t "$S" 2>/dev/null
  sleep 2
  start
  log "강제 재시작"
elif [ "$S_OK" -eq 1 ] && [ "$P_OK" -eq 1 ]; then
  echo "  이미 살아 있습니다. 그대로 둡니다."
elif [ "$S_OK" -eq 1 ] && [ "$P_OK" -eq 0 ]; then
  # **이것이 기존 스크립트가 놓치던 경우입니다.**
  echo "  좀비 세션 발견 — 껍데기는 남았는데 원격 제어가 죽어 있습니다."
  echo "  (sleep 86400 이 tmux 를 붙잡고 있어 has-session 만으로는 안 잡힙니다)"
  tmux kill-session -t "$S" 2>/dev/null
  sleep 1
  start
  log "좀비 세션 정리 후 재시작"
else
  echo "  세션이 없습니다. 새로 띄웁니다."
  start
  log "새로 시작"
fi

echo
echo "=== 확인 ==="
S_OK=0; P_OK=0
has_session && S_OK=1
alive && P_OK=1

# [2026-09-04 — 세 번째 판. 프로세스가 살아도 링크는 죽어 있을 수 있습니다]
#
#   09-04 16:53 에 이 스크립트가 "✅ 살아 있음 (pid 484, 1-14:22 경과)" 라고
#   보고했는데, 정작 화면에는 이렇게 떠 있었습니다.
#
#       ● Remote Control disconnected — OAuth token unavailable —
#         run /login to restore Remote Control
#                                        ... 상태줄: /rc failed
#
#   원인은 자격증명이었습니다. 프로세스는 09-03 02:29 에 떴고
#   ~/.claude/.credentials.json 은 09-04 11:20 에 **갱신**됐습니다. 오래 도는
#   프로세스가 메모리에 든 낡은 토큰을 계속 들고 있었던 것입니다. 재시작만으로
#   복구됩니다 -- /login 이 필요 없습니다.
#
#   1판은 세션을 봤고(틀림), 2판은 프로세스를 봤습니다(부족함). **살아 있음의
#   층이 하나 더 있습니다 -- 연결.** 이 프로젝트가 반복해서 데인 유형이
#   점검 스크립트 안에서 세 번째로 재현된 것입니다.
#
#   그래서 화면을 읽어 끊김 배너를 직접 찾습니다.
link_broken() {
  tmux capture-pane -p -S -200 -t "$S" 2>/dev/null \
    | grep -qE "Remote Control disconnected|OAuth token unavailable|/rc failed"
}

if [ "$S_OK" -eq 1 ] && [ "$P_OK" -eq 1 ] && link_broken; then
  echo "  ⚠️  프로세스는 살아 있지만 **링크가 끊겨 있습니다.**"
  tmux capture-pane -p -S -200 -t "$S" 2>/dev/null \
    | grep -E "Remote Control disconnected|OAuth token unavailable|/rc failed" \
    | tail -3 | sed 's/^/       /'
  if [ "$FORCE" -eq 1 ]; then
    echo "     --force 로 이미 새로 띄웠는데도 배너가 남아 있습니다."
    echo "     자격증명이 정말 만료됐을 수 있습니다 -> tmux attach 후 /login"
  else
    echo "     대개 낡은 토큰을 든 장수 프로세스입니다. 재시작으로 고쳐집니다:"
    echo "       bash $0 --force"
  fi
  log "링크 끊김 감지 (프로세스는 생존)"
  exit 1
fi

if [ "$S_OK" -eq 1 ] && [ "$P_OK" -eq 1 ]; then
  pid=$(remote_pid)
  echo "  ✅ 원격 제어 살아 있음 (pid $pid, $(ps -o etime= -p "$pid" | tr -d ' ') 경과)"
  echo "     링크 배너 검사도 통과 — 화면에 끊김 표시 없음"
  # 느슨한 검사와 몇 개나 차이 나는지 보여 줍니다. 이 격차가 1판·2판이 틀렸던 폭입니다.
  loose=$(pgrep -cf -- "--remote-control" 2>/dev/null)
  echo "     (느슨한 검사로는 ${loose}개가 잡힙니다 — tmux 서버와 래퍼 셸까지."
  echo "      그래서 실행파일 경로로 정확히 한 개만 셉니다)"
else
  echo "  ❌ 되살리기 실패 — tmux 세션=$S_OK 프로세스=$P_OK"
  echo "  화면:"
  tmux capture-pane -p -t "$S" 2>/dev/null | tail -8 | sed 's/^/      /'
  exit 1
fi

echo
echo "=== 재부팅 후에도 살아나나 ==="
if [ -f "$GUARD" ] && grep -q "remote_control.sh" "$GUARD"; then
  echo "  ✅ ensure_guards.sh 가 되살리기를 겁니다"
  echo "     (윈도우 작업 스케줄러의 wsl_hold 가 주기적으로 이 가드를 부릅니다)"
  echo "  ⚠️  단 그 경로는 remote_control.sh 를 부르므로 **좀비 세션은 못 고칩니다.**"
  echo "     껐다 켠 뒤 접속이 안 되면 이 명령(/wireless)을 한 번 실행하세요."
else
  echo "  ⚠️  ensure_guards.sh 에 되살리기가 안 걸려 있습니다 — 재부팅하면 끊깁니다"
fi

echo
echo "=== 접속 방법 ==="
cat <<EOF
  아이패드/폰에서  https://claude.ai/code  ->  기기 "$DEVICE" 선택
  작업 디렉터리    $WORK
  화면 엿보기      tmux capture-pane -p -t $S | tail -20
  직접 붙기        tmux attach -t $S   (빠져나올 때 Ctrl-b d)
EOF
exit 0
