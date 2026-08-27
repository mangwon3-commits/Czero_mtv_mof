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

# 계산으로 치는 것. 하나라도 살아 있으면 걸지 않는다.
#
# [2026-08-28 데스크탑이 잡은 결함] 예전에는 이 한 줄이었다:
#     BUSY_RE='simulate|lmp_serial|/network|risk_screen|run_water|run_humid'
# `/network` 가 상시 데몬 `networkd-dispatcher` 에 걸린다. 그러면 busy 가 항상
# 참이 되어 **감시자가 영원히 아무것도 안 한다.** Junseok 에서 그 데몬이 지금
# 돌지는 않지만 `networkd-dispatcher.service` 가 **enabled** 로 설치돼 있어
# 언제든 뜬다. 이름 매칭과 명령줄 매칭을 섞으면 어느 쪽 함정인지 안 보인다
# (CLAUDE.md §4 의 pgrep 자기 매칭과 같은 계열).
#
#   BUSY_COMM  프로세스 **이름** 정확일치 -> 계산 바이너리. 데몬과 안 겹친다.
#              (`networkd-dispatcher` 의 comm 은 `networkd-dispat` 라 안 걸린다)
#   BUSY_CMD   **명령줄** 매칭 -> 우리 드라이버만.
BUSY_COMM='^(simulate|lmp_serial|lmp|network|xtb|git|git-remote-http|git-remote-https)$'
#
# [2026-08-28] git 을 여기 넣은 이유, 그리고 autopush 를 **안** 넣은 이유.
#
#   보호하려는 것: 푸시가 도는 중에 감시자가 git merge 를 걸어 같은 저장소를
#   둘이 동시에 만지는 것. 08-27 에 34개 파일이 로컬에만 남은 적이 있다.
#
#   처음에는 autopush 를 BUSY_CMD 에 넣었는데 데스크탑이 되짚었다 --
#   **autopush 는 계산 내내 붙어 있는 감독자**다. 고아로 남으면 busy 가
#   영구히 참이 되어 감시자가 영영 아무것도 안 한다. 방금 고친
#   `/network` -> networkd-dispatcher 와 **같은 형태**다.
#
#     상주 감독자를 매칭  ->  가드가 영구히 켜짐  ->  복구 불능
#     일시적 일꾼을 매칭  ->  일하는 동안만 켜짐  ->  그 창만 정확히 보호
#
#   git 프로세스는 전송 중에만 뜬다 (실측: 전송 중 1개, 끝난 뒤 0개).
#   이 스크립트 자신의 git 은 안 세인다 -- busy 검사가 첫 git 호출보다
#   앞줄에 있다 (stage2 84 < 93, water 76 < 120).
BUSY_CMD='run_water|run_humid|run_gcmc|risk_screen|relax_series'

# 이 스크립트 자신은 어느 쪽에도 안 걸린다 - 명령줄이 경로뿐이고
# BUSY_CMD 의 어떤 낱말도 들어 있지 않다.
count_busy() {
  local n1 n2
  n1=$(ps -eo comm= | grep -cE "$BUSY_COMM") || n1=0
  n2=$(pgrep -c -f "$BUSY_CMD") || n2=0
  case "$n1" in ''|*[!0-9]*) n1=0 ;; esac
  case "$n2" in ''|*[!0-9]*) n2=0 ;; esac
  echo $(( n1 + n2 ))
}
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
NBUSY=$(count_busy)
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
