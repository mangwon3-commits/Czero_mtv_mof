#!/bin/bash
# 원격 제어 세션 감시견 — 프로세스를 보고, 대화를 이어받고, 좀비를 치운다.
#
# [왜 새로 쓰는가 — remote_control.sh 의 결함 셋]
#
#   ① tmux 세션을 보고 판단했다.
#      기존 스크립트는 `claude ...; echo ...; sleep 86400` 으로 띄운다.
#      claude 가 죽어도 뒤의 sleep 이 tmux 세션을 24시간 붙잡으므로
#      `tmux has-session` 은 계속 "있음" 을 답한다. 즉 원격 제어가 끊긴 채로
#      점검은 매번 정상으로 보고한다. 2026-08-24 랩탑에서 실제로 발견됐다 —
#      `claude-remote` 세션이 08-18 부터 6일간 껍데기만 남아 있었다.
#      **그래서 여기서는 tmux 가 아니라 프로세스를 본다.**
#
#   ② 재기동하면 대화가 비어 있었다.
#      맨몸으로 `claude --remote-control <이름>` 을 띄우면 새 대화가 시작된다.
#      전원을 껐다 켤 때마다 맥락이 사라지고, 피어 목록에는 offline 행만
#      쌓인다. `--continue` 를 붙이면 그 작업 디렉터리의 직전 대화를 이어받는다.
#      **프로세스는 새로 뜨지만 대화는 이어진다** — 프로세스를 되살리는 것은
#      원리상 불가능하므로 여기까지가 할 수 있는 최선이다.
#
#   ③ 죽은 자리를 치우지 않았다.
#      좀비 tmux 세션이 남아 있으면 같은 이름으로 새로 못 띄운다.
#      여기서는 프로세스가 없는데 세션만 있으면 그 세션을 먼저 죽인다.
#
# [사용]
#   bash rc_guard.sh --check          # 진단만. 아무것도 띄우지도 죽이지도 않음
#   bash rc_guard.sh                  # 필요하면 되살림
#
#   환경변수로 기기별 값을 덮는다 (기본값은 이 랩탑 기준):
#     RC_NAME     원격 제어 이름          (기본 laptop-mof)
#     RC_TMUX     tmux 세션 이름          (기본 claude-rc)
#     RC_CLAUDE   claude 실행 파일 경로   (기본 ~/.local/bin/claude)
#     RC_WORK     작업 디렉터리           (기본 ~/mof_project)
#
#   데스크탑에서 쓰려면:
#     RC_NAME=HKHOME-desktop RC_TMUX=claude-remote \
#     RC_CLAUDE=/home/mangwon1/.local/bin/claude \
#     RC_WORK=/home/mangwon1/mof_project bash rc_guard.sh
#
# [무엇을 하지 않는가]
#   계산 프로세스를 절대 건드리지 않는다. simulate·lmp_serial·network 를
#   보지도 죽이지도 않는다. 이 스크립트가 아는 것은 claude 원격 제어뿐이다.
set -u

RC_NAME=${RC_NAME:-laptop-mof}
RC_TMUX=${RC_TMUX:-claude-rc}
RC_CLAUDE=${RC_CLAUDE:-$HOME/.local/bin/claude}
RC_WORK=${RC_WORK:-$HOME/mof_project}
RC_LOG=${RC_LOG:-$HOME/.claude_work/rc_guard.log}

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

mkdir -p "$(dirname "$RC_LOG")"
say() { printf '[%s] %s\n' "$(date '+%m-%d %H:%M:%S')" "$*"; }
log() { say "$@" >> "$RC_LOG"; }

# 겹쳐 불려도 하나만 돈다. 예약 작업과 crontab 이 둘 다 부를 수 있다.
# (ensure_guards.sh 가 08-10 에 같은 이유로 감시견을 두 개 띄운 전례)
if [ $CHECK -eq 0 ]; then
  exec 9>"${RC_LOG}.lock"
  flock -n 9 || exit 0
fi

# ── 1. 프로세스가 살아 있는가 (tmux 가 아니라 이것이 판정 기준) ──────────
# pgrep -f 는 자기 명령줄에도 걸리므로 $$ 를 뺀다.
alive_pids=$(pgrep -f -- "--remote-control ${RC_NAME}" 2>/dev/null | grep -v "^$$\$")
n_alive=$(printf '%s' "$alive_pids" | grep -c . || true)

has_tmux=0
tmux has-session -t "$RC_TMUX" 2>/dev/null && has_tmux=1

if [ $CHECK -eq 1 ]; then
  say "원격 제어 이름 : $RC_NAME"
  say "tmux 세션      : $RC_TMUX ($([ $has_tmux -eq 1 ] && echo 있음 || echo 없음))"
  say "claude 프로세스: ${n_alive}개 ${alive_pids:+($(printf '%s' "$alive_pids" | tr '\n' ' '))}"
  if [ "$n_alive" -ge 1 ]; then
    say "판정: 정상 — 되살릴 필요 없음"
  elif [ $has_tmux -eq 1 ]; then
    say "판정: **좀비** — tmux 세션은 있는데 claude 가 없음. 세션을 치우고 재기동해야 함"
  else
    say "판정: 죽음 — 재기동 필요"
  fi
  say "(--check 이므로 아무것도 바꾸지 않았습니다)"
  exit 0
fi

[ "$n_alive" -ge 1 ] && exit 0          # 정상. 조용히 물러난다.

# ── 2. 좀비 tmux 세션 치우기 ────────────────────────────────────────────
if [ $has_tmux -eq 1 ]; then
  log "좀비 감지: tmux '$RC_TMUX' 는 있는데 claude 없음 → 세션 종료"
  tmux kill-session -t "$RC_TMUX" 2>/dev/null
fi

[ -x "$RC_CLAUDE" ] || { log "claude 없음: $RC_CLAUDE"; exit 1; }

# ── 3. 재기동. 먼저 대화를 이어받아 보고, 안 되면 새로 시작 ─────────────
#   --continue 는 그 작업 디렉터리의 직전 대화를 잇는다. 이력이 없거나
#   손상됐으면 즉시 죽을 수 있으므로, 살아났는지 확인하고 안 되면 맨몸으로
#   다시 띄운다. 그러지 않으면 15분마다 같은 실패를 반복한다.
start() {   # $1 = 추가 플래그(비어도 됨)
  tmux new-session -d -s "$RC_TMUX" -c "$RC_WORK" \
    "$RC_CLAUDE ${1:+$1 }--remote-control $RC_NAME"
}

start "--continue"
sleep 8
alive_pids=$(pgrep -f -- "--remote-control ${RC_NAME}" 2>/dev/null)
if [ -n "$alive_pids" ]; then
  log "재기동 완료 (--continue, 대화 이어받음) pid $(printf '%s' "$alive_pids" | tr '\n' ' ')"
  exit 0
fi

log "--continue 실패 → 새 대화로 재시도"
tmux kill-session -t "$RC_TMUX" 2>/dev/null
start ""
sleep 8
alive_pids=$(pgrep -f -- "--remote-control ${RC_NAME}" 2>/dev/null)
if [ -n "$alive_pids" ]; then
  log "재기동 완료 (새 대화) pid $(printf '%s' "$alive_pids" | tr '\n' ' ')"
  exit 0
fi

log "!! 재기동 실패 — 손으로 확인 필요: tmux new -s $RC_TMUX \"$RC_CLAUDE --remote-control $RC_NAME\""
exit 1
