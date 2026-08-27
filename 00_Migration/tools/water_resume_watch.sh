#!/bin/bash
# mslm050 물 2작업 이어받기 감시자 — cron 이 10분마다 부른다.
#
# [왜 필요한가]
#   사용자가 1주간 부재다. RH90 은 8~9시간짜리라 새벽에 죽으면 아무도 못
#   되살리고, 그러면 유지율의 분자가 통째로 빈다.
#
# [왜 안전한가]
#   run_water 는 (조성, RH) 작업 단위로 이어받는다 — 이미 끝난 작업은 결과
#   파일을 보고 건너뛰고, 중간에 죽은 작업은 RASPA 의 CrashRestart 에서
#   이어 간다. 그래서 **그냥 다시 띄우는 것이 옳은 복구**이고 중복 계산이
#   되지 않는다. (run_water_v3mslm050.py 독스트링)
#
# [무엇을 하지 않는가]
#   결과 해석도, 새 배정도 하지 않는다. **이미 착수된 그 작업만** 되살린다.
#   무한 재기동을 막기 위해 시도 횟수를 센다.
set -u

REPO=/home/mangwon/mof_project
DIR=$REPO/21_ZIF69_MTV
STATE=$HOME/.stage2
LOG=$STATE/watch.log
TRIES=$STATE/water_tries

RESULT=$DIR/v3_water_mslm050/water_results.json
RUNNER=run_water_v3mslm050.py
WANT_ROWS=2
MAX_TRIES=5

BUSY_RE='simulate|lmp_serial|/network|risk_screen|run_water|run_humid'
PY=/home/mangwon/miniconda3/envs/czeromof/bin/python

mkdir -p "$STATE"
log() { echo "[$(date '+%F %T')] [water] $*" >> "$LOG"; }

exec 8>"$STATE/water.lock"
flock -n 8 || exit 0

# ---- 이미 다 끝났나 ---------------------------------------------------------
if [ -s "$RESULT" ]; then
  n=$("$PY" -c "import json,sys;print(len(json.load(open(sys.argv[1]))))" "$RESULT" 2>/dev/null) || n=-1
  if [ "$n" = "$WANT_ROWS" ]; then
    exit 0                      # 조용히. 매 10분 로그를 쌓지 않는다.
  fi
fi

# ---- 뭐라도 돌고 있으면 손대지 않는다 ---------------------------------------
NBUSY=$(pgrep -c -f "$BUSY_RE" 2>/dev/null) || NBUSY=0
case "$NBUSY" in ''|*[!0-9]*) NBUSY=0 ;; esac
[ "$NBUSY" -gt 0 ] && exit 0

# ---- 여기까지 왔으면: 결과가 미완인데 아무것도 안 돈다 ----------------------
T=0
[ -f "$TRIES" ] && T=$(cat "$TRIES" 2>/dev/null || echo 0)
case "$T" in ''|*[!0-9]*) T=0 ;; esac
if [ "$T" -ge "$MAX_TRIES" ]; then
  [ $(( $(date +%M) % 60 )) -lt 10 ] && log "재기동 $T회로 상한 도달. 더 걸지 않는다. 사람이 볼 일이다."
  exit 0
fi
T=$((T+1)); echo "$T" > "$TRIES"

# RASPA 환경. 08-27 에 PATH 를 안 옮겨 12종 중 7종이 조용히 실패했다.
export PATH="/home/mangwon/miniconda3/envs/czeromof/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
if ! command -v python >/dev/null || ! command -v simulate >/dev/null; then
  log "PATH 에 python 또는 simulate 가 없다. 걸지 않는다."
  exit 1
fi

cd "$DIR" || exit 1
log "미완 결과 + 유휴 상태 감지. $RUNNER 이어받기 재기동 (시도 $T/$MAX_TRIES)"
{
  echo
  echo "===== $(date '+%F %T') 이어받기 재기동 (water_resume_watch.sh, 시도 $T) ====="
} >> water_mslm050.log

setsid nohup python -u "$RUNNER" >> water_mslm050.log 2>&1 < /dev/null &
sleep 10
PID=$(pgrep -f "$RUNNER" | head -1)
if [ -z "$PID" ]; then
  log "기동 실패. 로그 끝:"
  tail -n 12 water_mslm050.log >> "$LOG"
  exit 1
fi
log "드라이버 재기동 PID $PID"

setsid nohup "$PY" autopush.py \
  --pid "$PID" \
  --result 21_ZIF69_MTV/v3_water_mslm050/water_results.json \
  --log 21_ZIF69_MTV/water_mslm050.log \
  --mailbox 21_ZIF69_MTV/COMMS/junseok.md \
  --schema water --expect "$WANT_ROWS" \
  --label "mslm050 수분 경쟁 — RH90 · RH0 (이어받기 재기동 $T)" \
  --branch "$(git -C "$REPO" rev-parse --abbrev-ref HEAD)" \
  >> "$HOME/.autopush/watch_water.out" 2>&1 < /dev/null &
sleep 4
log "autopush 부착 PID $(pgrep -f autopush.py | head -1)"
exit 0
