#!/bin/bash
# 백그라운드에서 도는 것들의 현황을 한 번에 보여 준다. /backgroundstate 가 이것을 부른다.
#
# [왜 스크립트로 두는가]
#   "지금 뭐가 돌고 있나" 를 매번 즉흥으로 물었고, 그때마다 **틀린 방법으로
#   세었습니다.** 이 프로젝트에서 실제로 겪은 오답들:
#
#     - 실행 디렉터리 개수로 셌더니 "시작 0 / 완주 0". run_water.py 와
#       run_working_capacity.py 는 결과를 뽑은 뒤 폴더를 지웁니다.
#       **끝난 것일수록 안 보입니다.**
#     - 출력 파일 갱신 시각으로 판단했더니 "6시간째 멈춤" 으로 보였습니다.
#       RASPA 의 PrintEvery 가 15000 이라 처음과 끝에만 씁니다. 멀쩡했습니다.
#     - `pgrep -f` 로 셌더니 tmux 서버와 래퍼 sh 까지 잡혀 3배로 나왔습니다.
#     - 프로세스가 살아 있다는 것과 **일을 하고 있다**는 것은 다릅니다.
#
#   그래서 이 스크립트는 **CPU 시간이 실제로 늘어나는지**를 4초 재서 증거로
#   삼고, 완주 여부는 RASPA 출력의 "Simulation finished" 로 셉니다.
#
# 사용:  bash bgstate.sh          전체
#        bash bgstate.sh --brief  1절만

P=/home/mangwon1/mof_project/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
HZ=$(getconf CLK_TCK 2>/dev/null || echo 100)
NOW=$(date +%s)

hdr() { printf '\n\033[1m%s\033[0m\n' "$*"; }
plain() { printf '\n%s\n' "$*"; }
command -v tput >/dev/null 2>&1 || hdr() { plain "$@"; }

# ---------------------------------------------------------------- 1. 도는 것
hdr "=== 1. 지금 도는 것 ==="

# 관심 대상만 고릅니다. pgrep -f 로 넓게 잡으면 래퍼 셸까지 딸려 옵니다.
PIDS=$(ps -eo pid=,comm=,args= | awk '
  $2=="simulate" || $2=="lmp_serial" || $2=="xtb" || $2=="network" {print $1; next}
  $2=="python" || $2=="python3" {
    if ($0 ~ /run_water|run_wc|run_density|run_gcmc|relax_|risk_|regen_|queue_/) print $1
  }')

if [ -z "$PIDS" ]; then
  echo "  (없음) — 백그라운드 계산이 하나도 돌고 있지 않습니다."
else
  declare -A T0 PCT KIDS GRP GSUM GKIDS
  for p in $PIDS; do
    T0[$p]=$(awk '{print $14+$15}' /proc/$p/stat 2>/dev/null || echo 0)
  done
  sleep 4

  # 1차: 재고 무리를 짓습니다. 같은 스크립트에서 갈라진 것들이 한 무리입니다.
  for p in $PIDS; do
    [ -d /proc/$p ] || continue
    t1=$(awk '{print $14+$15}' /proc/$p/stat 2>/dev/null || echo 0)
    PCT[$p]=$(( ( (t1 - ${T0[$p]:-0}) * 100 ) / (4 * HZ) ))
    KIDS[$p]=$(pgrep -P "$p" 2>/dev/null | wc -l)
    g=$(ps -o args= -p $p | awk '{for(i=1;i<=NF;i++) if($i ~ /\.py$/){n=split($i,a,"/"); print a[n]; exit}}')
    [ -z "$g" ] && g=$(ps -o comm= -p $p | tr -d ' ')
    # xtb 는 한 단계가 14초라 이 4초 사이에 끝나 버릴 수 있습니다. 그러면 ps 가
    # 빈 문자열을 돌려주고 연관배열 첨자가 비어 "bad array subscript" 가 납니다.
    # 사라진 프로세스는 무리 이름을 '(종료됨)' 으로 두고 넘어갑니다.
    [ -z "$g" ] && g='(종료됨)'
    GRP[$p]=$g
    GSUM[$g]=$(( ${GSUM[$g]:-0} + ${PCT[$p]} ))
    GKIDS[$g]=$(( ${GKIDS[$g]:-0} + ${KIDS[$p]} ))
  done

  printf "  %-7s %-5s %-11s %8s %7s  %s\n" PID nice 경과 "CPU점유" RSS 무엇
  for p in $PIDS; do
    [ -d /proc/$p ] || continue
    pct="${PCT[$p]}%"
    ni=$(ps -o ni= -p $p | tr -d ' ')
    et=$(ps -o etime= -p $p | tr -d ' ')
    rss=$(awk -v r="$(ps -o rss= -p $p | tr -d ' ')" 'BEGIN{printf "%.0fM", r/1024}')
    cm=$(ps -o comm= -p $p | tr -d ' ')
    cwd=$(readlink /proc/$p/cwd 2>/dev/null)
    case "$cm" in
      simulate)  lbl="RASPA  $(basename "$(dirname "$cwd")")/$(basename "$cwd")" ;;
      xtb)       lbl="xtb    $(basename "$cwd")" ;;
      network)   lbl="Zeo++  $(basename "$cwd")" ;;
      lmp_serial) lbl="LAMMPS $(basename "$cwd")" ;;
      *)         lbl=$(ps -o args= -p $p | awk '{for(i=1;i<=NF;i++) if($i ~ /\.py$/){print "python " $i; exit}} END{}')
                 [ -z "$lbl" ] && lbl="python (드라이버)" ;;
    esac
    # [2026-08-16 오탐 수정] CPU 0% 를 프로세스 하나만 보고 판정하면 틀립니다.
    #   수분 v2 는 워커가 4인데 남은 작업이 2뿐이라, 놀던 워커 둘을 "멈춘 것일
    #   수 있음" 으로 찍었습니다. 멈춘 게 아니라 **일감이 없었습니다.**
    #
    #   풀 방식에서 워커 하나가 노는 것은 정상입니다. 비정상은 **무리 전체가
    #   노는 것**입니다. 그래서 개체가 아니라 무리로 판정합니다.
    g=${GRP[$p]}
    if [ "${pct%\%}" -lt 3 ] 2>/dev/null; then
      if [ "${KIDS[$p]}" -gt 0 ]; then
        lbl="$lbl  (대기 — 자식 ${KIDS[$p]}개가 계산 중)"
      elif [ "${GSUM[$g]:-0}" -ge 30 ] || [ "${GKIDS[$g]:-0}" -gt 0 ]; then
        lbl="$lbl  (놀고 있음 — 같은 배치의 다른 워커가 계산 중)"
      else
        lbl="$lbl  <-- 배치 전체가 0%, 자식도 없음. **멈췄을 수 있음**"
      fi
    fi
    printf "  %-7s %-5s %-11s %8s %7s  %s\n" "$p" "$ni" "$et" "$pct" "$rss" "$lbl"
  done
fi

[ "$1" = "--brief" ] && exit 0

# ------------------------------------------------------- 2. RASPA 배치 진행도
hdr "=== 2. 배치 진행도 ==="

batch() {  # $1 = 폴더, $2 = 표시 이름(폭 14 로 맞춰 넘길 것), $3 = 결과 파일(선택)
  local d="$P/$1" done=0 run=0 wait=0 names=""
  if [ ! -d "$d" ]; then
    # "폴더 없음" 을 뭉뚱그리면 **끝나서 정리한 것**과 **아직 시작도 안 한 것**이
    # 같아 보입니다. 결과 파일로 가릅니다 -- 그게 실제로 다른 상태입니다.
    if [ -n "${3:-}" ] && [ -f "$P/$3" ]; then
      printf "  %s ✅ 완료 후 정리됨 (결과 %s 보존)\n" "$2" "$3"
    else
      printf "  %s ⬜ 아직 시작 전\n" "$2"
    fi
    return
  fi
  for r in "$d"/*/; do
    [ -d "$r" ] || continue
    local f
    f=$(ls "$r"/Output/System_0/*.data 2>/dev/null | head -1)
    if [ -z "$f" ]; then wait=$((wait+1)); continue; fi
    if grep -q "Simulation finished" "$f" 2>/dev/null; then
      done=$((done+1))
    else
      run=$((run+1))
      local st el pid
      # 폴더 생성 시각으로 경과를 재면, **재시작한 작업**이 원래 시작 시각부터
      # 잰 값으로 나옵니다(08-16 정전 복구 때 22시간으로 찍혔는데 실제로는
      # 1분이었습니다). 그 폴더를 실제로 쓰고 있는 프로세스가 있으면 그쪽 경과를
      # 씁니다 -- 그것이 지금 이 계산이 얼마나 돌았는지입니다.
      pid=$(for q in $(pgrep -x simulate 2>/dev/null); do
              [ "$(readlink /proc/$q/cwd 2>/dev/null)" = "${r%/}" ] && echo "$q" && break
            done)
      if [ -n "$pid" ]; then
        names="$names $(basename "$r")($(ps -o etime= -p "$pid" | tr -d ' '))"
      else
        st=$(stat -c %W "$r"); [ "$st" = "0" ] && st=$(stat -c %Y "$r/simulation.input" 2>/dev/null)
        el=$(awk -v a="$NOW" -v b="$st" 'BEGIN{printf "%.1f", (a-b)/3600}')
        names="$names $(basename "$r")(${el}h·프로세스없음)"
      fi
    fi
  done
  local tot=$((done+run+wait))
  # printf 의 %-16s 는 **바이트**를 셉니다. 한글은 UTF-8 로 3바이트인데 화면에서는
  # 2칸이라 열이 어긋납니다. 그래서 이름은 호출부에서 이미 맞춰 넘깁니다.
  printf "  %s 완주 %2d / %2d" "$2" "$done" "$tot"
  [ "$run" -gt 0 ] && printf "   진행중:%s" "$names"
  [ "$wait" -gt 0 ] && printf "   대기 %d" "$wait"
  printf "\n"
}

#            표시폭 14 칸에 맞춰 손으로 채웁니다 (한글 1자 = 2칸)
batch water_runs_v2  "수분 v2       " v2_water/water_results.json
batch wc_runs_v2     "작업용량 v2   " v2_wc/working_capacity.json
batch runs_v2        "GCMC v2       " results_v2.json
batch runs_v3        "GCMC v3       " results_v3.json
batch humid_wc_v2    "습윤 WC v2    " humid_working_capacity_v2.json
batch aryl_runs      "아릴 GCMC     " aryl_results.json

# ---------------------------------------------------------- 3. 결과 파일
hdr "=== 3. 결과 파일 (이게 있어야 끝난 것) ==="
res() {
  local f="$P/$1"
  if [ -f "$f" ]; then
    local n
    n=$(python3 -c "
import json,sys
d=json.load(open('$f'))
r=d.get('rows',d) if isinstance(d,dict) else d
print(len(r))" 2>/dev/null || echo '?')
    printf "  ✅ %-34s %s   항목 %s\n" "$1" "$(date -d @$(stat -c %Y "$f") '+%m-%d %H:%M')" "$n"
  else
    printf "  ⬜ %-34s 아직\n" "$1"
  fi
}
res results_v2.json
res v2_wc/working_capacity.json
res v2_water/water_results.json
res density_v2/density_results.json
res humid_working_capacity_v2.json
res risk_results_v2.json

# ---------------------------------------------------------- 4. 자원과 디스크
hdr "=== 4. 자원 ==="
# [2026-08-22] 코어 수와 디스크 이름을 재서 씁니다.
#
#   여기 "물리 8코어" 가 데스크탑 값으로 **박혀** 있었습니다. 새 기기(물리
#   4코어 컨테이너)가 이 스크립트를 돌리자 8코어라고 거짓 보고했습니다.
#   워커 수를 물리 코어로 정하는 것이 이 프로젝트의 규약이므로, 그 판단의
#   입력이 거짓이면 배정이 통째로 틀립니다 -- 재지 않고 적어 둔 숫자가
#   측정값 행세를 하는, 이 프로젝트가 반복해서 데인 바로 그 유형입니다.
#   같은 이유로 "WSL 디스크" 도 WSL 이 아닌 기기에서 거짓말이었습니다.
PHYS=$(lscpu -p=Core,Socket 2>/dev/null | grep -v '^#' | sort -u | wc -l)
[ "${PHYS:-0}" -gt 0 ] 2>/dev/null || PHYS=$(nproc 2>/dev/null || echo '?')
if grep -qi microsoft /proc/version 2>/dev/null; then DLABEL="WSL 디스크"; else DLABEL="루트 디스크"; fi
printf "  부하 %s (물리 %s코어)   메모리 가용 %s GB / 스왑 사용 %s MB\n" \
  "$(cut -d' ' -f1-3 /proc/loadavg)" \
  "$PHYS" \
  "$(free -g | awk 'NR==2{print $7}')" \
  "$(free -m | awk 'NR==3{print $3}')"
printf "  %s  %s\n" "$DLABEL" "$(df -h / | awk 'NR==2{print $4" 여유 ("$5" 사용)"}')"
if [ -d /mnt/c ]; then
  cfree=$(df -BG /mnt/c 2>/dev/null | awk 'NR==2{gsub("G","",$4); print $4}')
  printf "  C: 드라이브 %s" "$(df -h /mnt/c | awk 'NR==2{print $4" 여유 ("$5" 사용)"}')"
  # vhdx 가 C: 에 있으므로 여기가 마르면 WSL 이 통째로 멈춥니다. 08-12 와 같은 계열.
  if [ -n "$cfree" ] && [ "$cfree" -lt 10 ]; then
    printf "   ⚠️  10 GB 미만 — vhdx 가 여기 있습니다. 압축 필요"
  fi
  printf "\n"
fi

# ---------------------------------------------------------- 5. 로그 꼬리
hdr "=== 5. 백그라운드 로그 마지막 줄 ==="
for f in "$W"/*.log; do
  [ -f "$f" ] || continue
  # 하루 넘게 안 건드린 로그는 지난 일입니다. 화면을 어지럽히지 않게 뺍니다.
  age=$(( (NOW - $(stat -c %Y "$f")) / 3600 ))
  [ "$age" -gt 30 ] && continue
  printf "  %-24s %2dh 전  %s\n" "$(basename "$f")" "$age" \
    "$(tail -1 "$f" | cut -c1-88)"
done
[ -f "$P/relax_fixcell/opt.log" ] && \
  printf "  %-24s %8s  %s\n" "relax_fixcell/opt.log" "" "$(tail -1 "$P/relax_fixcell/opt.log")"

# ---------------------------------------------------------- 6. 예약된 후속
if [ -f "$W/pending_cleanup.state" ]; then
  hdr "=== 6. 예약된 후속 작업 ==="
  cat "$W/pending_cleanup.state" | sed 's/^/  /'
fi

exit 0
