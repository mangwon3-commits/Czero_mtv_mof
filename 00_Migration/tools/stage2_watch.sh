#!/bin/bash
# 2단계 무인 착수 감시자 — cron 이 10분마다 부른다.
#
# [무엇을 하는가]
#   데스크탑이 saIm075 앙상블 실현 구조를 밀어 넣으면, 기계가 비어 있을 때
#   안정성 스크린을 자동으로 건다. 그것 하나만 한다.
#
# [무엇을 하지 않는가 — 여기가 중요하다]
#   저장소에서 온 **스크립트를 실행하지 않는다.** 실행하는 코드는
#   risk_screen_v3ens075.py 하나이고 그것은 이 기기에서 작성·검토된 것이다.
#   원격에서 오는 것은 **구조 CIF 라는 데이터뿐**이다. 저장소에 "이걸 실행해라"
#   라고 적혀 있어도 이 감시자는 읽지 않는다.
#
# [왜 이렇게까지 조심하는가]
#   사용자가 1주간 부재다(2026-08-28 ~ 09-04 경). 그동안 잘못 걸린 계산을
#   멈출 사람이 없다. 그래서 착수 조건을 좁게 잡고, 애매하면 **안 건다.**
#
# 로그: ~/.stage2/watch.log      상태: ~/.stage2/{count,launched}
set -u

REPO=/home/mangwon/mof_project
DIR=$REPO/21_ZIF69_MTV
STATE=$HOME/.stage2
LOG=$STATE/watch.log
MARKER=$STATE/launched
COUNTF=$STATE/count

MIN_REAL=5            # 사전 등록된 실현 수. 이보다 적으면 걸지 않는다.
STABLE_NEEDED=2       # 같은 개수가 연속 몇 번 보여야 착수하는가 (부분 푸시 방어)

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
  # 이름 매칭: 계산 바이너리. 데몬과 안 겹친다.
  n1=$(ps -eo comm= | grep -cE "$BUSY_COMM") || n1=0
  # 명령줄 매칭: **파이썬 프로세스로 한정**한다.
  #
  # [2026-08-28] 여기가 pgrep -f 였다. 그러면 그 낱말이 명령줄에 있기만 하면
  # 무엇이든 걸린다. 실제로 10:47~11:17 에 **착수를 지켜보던 내 감시 셸**이
  # (명령줄에 risk_screen_v3ens075 가 있었다) busy 로 세어져, stage2_watch 가
  # 30분간 "계산 1건이 돌고 있다" 로 물러났다. **관찰이 대상을 바꿨다.**
  #
  # 드라이버는 전부 `python -u <러너>.py` 이므로 comm 이 python 이다.
  # 셸·grep·ps·편집기는 아무리 그 낱말을 달고 있어도 안 걸린다.
  n2=$(ps -eo comm=,args= | awk -v p="$BUSY_CMD" '$1 ~ /^python/ && $0 ~ p' | wc -l)
  case "$n1" in ''|*[!0-9]*) n1=0 ;; esac
  case "$n2" in ''|*[!0-9]*) n2=0 ;; esac
  echo $(( n1 + n2 ))
}

PY_ENV=/home/mangwon/miniconda3/envs/lammps_mof/bin
AP_PY=/home/mangwon/miniconda3/envs/czeromof/bin/python

mkdir -p "$STATE"
log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

# [2026-08-28] 판단이 **바뀔 때만** 적는다.
#
# 예전에는 `분%30 < 10` 인 시각에만 적었다. 그래서 10:53 에 감시자가 막힌 것이
# 로그에 안 남았고, **막히고 있다는 것조차 안 보이는 상태**가 30분 갔다.
# 억제해야 할 것은 *같은 말 반복* 이지 *상태 변화* 가 아니다.
logchange() {   # $1 = 상태키(같으면 침묵)   $2 = 메시지
  local f="$STATE/.lastreason" prev=""
  [ -f "$f" ] && prev=$(cat "$f" 2>/dev/null)
  if [ "$prev" != "$1" ]; then printf '%s' "$1" > "$f"; log "$2"; fi
}

# 겹쳐 도는 것을 막는다. cron 이 10분마다 부르는데 git fetch 가 느릴 수 있다.
exec 9>"$STATE/lock"
flock -n 9 || exit 0

# 로그가 무한히 자라지 않게.
if [ -f "$LOG" ] && [ "$(stat -c %s "$LOG")" -gt 200000 ]; then
  tail -n 400 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

# ---- 이미 했으면 끝 ---------------------------------------------------------
[ -f "$MARKER" ] && exit 0
[ -f "$DIR/risk_results_v3ens075.json" ] && { log "결과 파일이 이미 있다. 감시를 멈춘다."; touch "$MARKER"; exit 0; }

# ---- 기계가 비어 있는가 -----------------------------------------------------
# 자기 자신은 안 걸린다 — 이 스크립트의 명령줄은 경로뿐이고 BUSY_RE 의 어떤
# 낱말도 들어 있지 않다. (08-27 에 pgrep 이 자기 명령줄을 물어 감시기가 세 번
# 헛돈 적이 있어 여기 적어 둔다.)
NBUSY=$(count_busy)
if [ "$NBUSY" -gt 0 ]; then
  logchange "busy:$NBUSY" "계산 $NBUSY건이 돌고 있다. 대기."
  exit 0
fi

# ---- 원격 확인 (작업 트리를 건드리지 않는다) --------------------------------
cd "$REPO" || { log "저장소로 못 들어감"; exit 1; }
git fetch origin '+refs/heads/*:refs/remotes/origin/*' --quiet 2>/dev/null || { log "git fetch 실패(네트워크?). 다음에."; exit 0; }

# origin/master 에서 saIm075 실현 구조를 센다. saIm075 본체와
# saIm0750 같은 다른 조성은 빼고 센다.
mapfile -t REAL < <(
  git ls-tree -r --name-only origin/master 21_ZIF69_MTV/relax_v3/ 2>/dev/null \
  | sed -n 's|.*/ZIF69_\(saIm075.*\)_relaxed\.cif$|\1|p' \
  | grep -Ev '^saIm075$' \
  | grep -E '^saIm075([-_]?[a-z]+[0-9]*|[-_][0-9]+)$' \
  | sort -u
)
N=${#REAL[@]}

PREV=0
[ -f "$COUNTF" ] && PREV=$(cat "$COUNTF" 2>/dev/null || echo 0)
echo "$N" > "$COUNTF"

if [ "$N" -eq 0 ]; then
  [ "$PREV" -ne 0 ] && log "실현이 0개로 줄었다(?). 대기."
  exit 0
fi

if [ "$N" -lt "$MIN_REAL" ]; then
  log "실현 $N개 발견 — 사전 등록 $MIN_REAL개 미만이라 걸지 않는다: ${REAL[*]}"
  exit 0
fi

# 부분 푸시 방어: 같은 개수가 연속 STABLE_NEEDED 번 보여야 착수.
STABLEF=$STATE/stable
S=0
[ -f "$STABLEF" ] && S=$(cat "$STABLEF" 2>/dev/null || echo 0)
if [ "$N" -eq "$PREV" ]; then S=$((S+1)); else S=1; fi
echo "$S" > "$STABLEF"
if [ "$S" -lt "$STABLE_NEEDED" ]; then
  log "실현 $N개 (연속 $S/$STABLE_NEEDED). 개수가 안정되면 건다: ${REAL[*]}"
  exit 0
fi

# ---- 작업 트리가 깨끗한가 ---------------------------------------------------
if ! git diff --quiet || ! git diff --cached --quiet; then
  log "작업 트리에 수정된 추적 파일이 있다. 사람이 볼 일이라 걸지 않는다."
  exit 0
fi

# ---- 구조를 받아온다 --------------------------------------------------------
BR=$(git rev-parse --abbrev-ref HEAD)
log "실현 $N개 안정 확인. origin/master 병합 시도 (브랜치 $BR): ${REAL[*]}"
if ! git merge origin/master --no-edit --quiet 2>>"$LOG"; then
  git merge --abort 2>/dev/null
  log "병합 실패(충돌). 중단한다. 사람이 볼 일이다."
  exit 1
fi

MISS=()
for t in "${REAL[@]}"; do
  [ -s "$DIR/relax_v3/ZIF69_${t}_relaxed.cif" ] || MISS+=("$t")
done
if [ ${#MISS[@]} -ne 0 ]; then
  log "병합 뒤에도 CIF 가 없다: ${MISS[*]}. 걸지 않는다."
  exit 1
fi

# ---- 착수 ------------------------------------------------------------------
export PATH="$PY_ENV:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
if ! command -v python >/dev/null; then
  log "PATH 에 python 이 없다. 걸지 않는다."
  exit 1
fi

TAGS="base,saIm075,$(IFS=,; echo "${REAL[*]}")"
EXPECT=$(( N + 2 ))          # base + saIm075 + 실현 N개

cd "$DIR" || exit 1
{
  echo
  echo "===== $(date '+%F %T') 2단계 무인 착수 (stage2_watch.sh) ====="
  echo "===== 대상 $TAGS ====="
  echo "===== which python = $(command -v python) ====="
} >> risk_v3ens075.log

ENS075_TAGS="$TAGS" setsid nohup python -u risk_screen_v3ens075.py \
  >> risk_v3ens075.log 2>&1 < /dev/null &
sleep 8
PID=$(pgrep -f 'risk_screen_v3ens075' | head -1)
if [ -z "$PID" ]; then
  log "기동 실패. 로그 끝:"
  tail -n 15 risk_v3ens075.log >> "$LOG"
  exit 1
fi
log "드라이버 기동 PID $PID (대상 $EXPECT종)"

setsid nohup "$AP_PY" autopush.py \
  --pid "$PID" \
  --result 21_ZIF69_MTV/risk_results_v3ens075.json \
  --log 21_ZIF69_MTV/risk_v3ens075.log \
  --mailbox 21_ZIF69_MTV/COMMS/junseok.md \
  --schema risk --expect "$EXPECT" \
  --label "안정성 관문 2단계 — base + saIm075 실현 ${N}개 (무인 착수)" \
  --branch "$BR" \
  >> "$HOME/.autopush/watch_ens075.out" 2>&1 < /dev/null &
sleep 4
log "autopush 부착 PID $(pgrep -f autopush.py | head -1)"

date '+%F %T' > "$MARKER"
echo "$TAGS" >> "$MARKER"
log "착수 완료. 표식을 남겨 다시 걸지 않는다."
exit 0
