#!/bin/bash
# 계산이 다 끝나기를 기다렸다가, **결과가 확실히 수확된 실행 폴더만** 지우고
# vhdx 압축 준비가 끝났다고 표시한다.
#
# [왜 필요한가]
#   WSL 의 가상디스크(ext4.vhdx, 34.8 GB)가 C: 에 있는데 C: 여유가 3~4 GB 까지
#   내려왔습니다. 여기가 마르면 계산이 죽는 정도가 아니라 **ext4 가 깨질 수**
#   있습니다. 2026-08-12 의 WSL 먹통과 같은 계열입니다.
#
#   그런데 **WSL 안에서 지워도 C: 는 1 바이트도 안 돌아옵니다.** vhdx 는 한 번
#   커지면 스스로 줄지 않습니다. 밖에서 `wsl --shutdown` 후 압축해야 합니다.
#   그래서 순서가 강제됩니다:
#
#       계산 완주  ->  (여기, WSL 안) 지우기  ->  wsl --shutdown  ->  압축
#
#   셧다운이 계산을 죽이므로 **끝나기 전에는 절대 하면 안 됩니다.**
#
# [무엇을 지우고 무엇을 남기나 — 원칙]
#   지우는 것: RASPA 실행 폴더. 결과 JSON 으로 이미 수확했고, 필요하면 같은
#              입력으로 다시 만들 수 있습니다.
#   남기는 것: 결과 JSON, 구조 CIF, 전하 CIF, **그리고 density_v2**.
#
#   density_v2(330 MB)는 실행 폴더처럼 보이지만 아닙니다. 그 안의 VTK 격자가
#   밀도맵 그림의 **원본**이고, G: 에는 ZIF-8 계열만 있어 사본이 없습니다.
#   다시 만들려면 GCMC 를 다시 돌려야 합니다. 건드리지 않습니다.
#
# [안전 장치]
#   폴더마다 **관문 파일**을 정해 두고, 그 파일이 없거나 너무 작으면 그 폴더는
#   건너뜁니다. "결과가 있는 줄 알았는데 없었다" 를 코드가 막습니다.
#
# 사용:  bash cleanup_for_compact.sh            기다렸다가 실행
#        bash cleanup_for_compact.sh --now      기다리지 않고 지금 판단
#        bash cleanup_for_compact.sh --dry-run  지우지 않고 무엇을 지울지만

P=/home/mangwon1/mof_project/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
STATE=$W/pending_cleanup.state
LOG=$W/cleanup_for_compact.log
DRY=0; NOW=0
for a in "$@"; do
  [ "$a" = "--dry-run" ] && DRY=1
  [ "$a" = "--now" ] && NOW=1
done

say() { echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$LOG"; }

# 실행 폴더:관문 파일:최소 바이트
#   관문은 "그 폴더의 결과가 이미 파일로 나와 있다" 는 증거입니다.
TARGETS="
runs_v2:results_v2.json:5000
wc_runs_v2:v2_wc/working_capacity.json:1000
water_runs_v2:v2_water/water_results.json:1000
aryl_runs:aryl_results.json:1000
water_runs:water_results.json:1000
wc_runs:working_capacity.json:1000
humid_wc_runs:humid_working_capacity.json:1000
runs:zif69_results.json:1000
runs_v3:results_v3.json:5000
humid_wc_runs_v3:v3_humid_wc/humid_working_capacity.json:1000
humid_wc_runs_v3ext:v3_humid_wc/humid_working_capacity_ext.json:1000
"

cat > "$STATE" <<EOF
상태: 대기 중 — 계산이 끝나면 실행 폴더를 지웁니다.
시작: $(date '+%m-%d %H:%M')
다음: 이 스크립트가 끝나면 밖에서 wsl --shutdown 후 vhdx 압축.
EOF

# ------------------------------------------------------------------ 1. 기다림
if [ "$NOW" -eq 0 ]; then
  say "계산이 끝나기를 기다립니다 (최대 30시간)."
  deadline=$(( $(date +%s) + 30*3600 ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    sim=$(pgrep -c -x simulate 2>/dev/null); case "$sim" in ''|*[!0-9]*) sim=0;; esac
    xt=$(pgrep -c -x xtb 2>/dev/null);       case "$xt"  in ''|*[!0-9]*) xt=0;; esac
    lmp=$(pgrep -c -x lmp_serial 2>/dev/null); case "$lmp" in ''|*[!0-9]*) lmp=0;; esac
    drv=$(pgrep -c -f 'python.*\(run_water_v2\|relax_fixcell\)' 2>/dev/null)
    case "$drv" in ''|*[!0-9]*) drv=0;; esac
    if [ $((sim+xt+lmp+drv)) -eq 0 ]; then
      say "계산이 모두 끝났습니다."
      break
    fi
    printf '%s  대기 — simulate %s / xtb %s / lammps %s / 드라이버 %s\n' \
      "$(date '+%m-%d %H:%M')" "$sim" "$xt" "$lmp" "$drv" > "$STATE.tick"
    sleep 300
  done
  # 결과 파일이 나올 시간을 줍니다. 프로세스가 사라진 것과 결과가 나온 것은
  # 다릅니다 -- 이 프로젝트에서 반복된 사고 유형입니다.
  sleep 60
fi

# ------------------------------------------------------------------ 2. 판단
say "=== 관문 검사 ==="
FREED=0
DELLIST=""
for t in $TARGETS; do
  [ -z "$t" ] && continue
  dir=${t%%:*}; rest=${t#*:}; gate=${rest%%:*}; minb=${rest##*:}
  [ -d "$P/$dir" ] || { say "  건너뜀 $dir — 폴더 없음"; continue; }
  sz=$(du -sm "$P/$dir" | cut -f1)
  if [ ! -f "$P/$gate" ]; then
    say "  ⛔ 보존 $dir (${sz}MB) — 관문 $gate 이 없습니다"
    continue
  fi
  b=$(stat -c %s "$P/$gate")
  if [ "$b" -lt "$minb" ]; then
    say "  ⛔ 보존 $dir (${sz}MB) — 관문 $gate 이 너무 작습니다 (${b}B)"
    continue
  fi
  say "  ✅ 삭제 $dir (${sz}MB) — 관문 $gate 확인 (${b}B)"
  DELLIST="$DELLIST $dir"
  FREED=$((FREED+sz))
done

# gfnff_topo 는 xtb 가 매번 새로 만드는 순수 스크래치입니다. 관문이 필요 없습니다.
for f in "$P"/relax_test/gfnff_topo "$P"/relax_fixcell/gfnff_topo; do
  if [ -f "$f" ]; then
    sz=$(du -sm "$f" | cut -f1)
    say "  ✅ 삭제 $(basename "$(dirname "$f")")/gfnff_topo (${sz}MB) — xtb 가 매번 재생성"
    [ "$DRY" -eq 0 ] && rm -f "$f"
    FREED=$((FREED+sz))
  fi
done

say "=== 보존 (지우지 않음) ==="
say "  density_v2 — VTK 밀도 격자가 그림의 원본이고 다른 사본이 없습니다"
say "  structures_v2 / charged_v2 / 모든 결과 JSON / relax_* 의 CIF·궤적"

if [ "$DRY" -eq 1 ]; then
  say "--dry-run 이므로 실제로는 지우지 않았습니다. 회수 예상 ${FREED} MB"
  exit 0
fi

for dir in $DELLIST; do rm -rf "${P:?}/$dir"; done
say "=== 완료 — WSL 안에서 ${FREED} MB 를 비웠습니다 ==="
say "df: $(df -h / | awk 'NR==2{print $4" 여유"}')"

cat > "$STATE" <<EOF
상태: **압축 준비 완료** — WSL 안에서 ${FREED} MB 를 비웠습니다.
시각: $(date '+%m-%d %H:%M')
지운 것:$DELLIST + gfnff_topo
보존: density_v2, structures_v2, charged_v2, 결과 JSON 전부

!! 아직 C: 는 그대로입니다. vhdx 는 스스로 줄지 않습니다.
   윈도우에서 다음을 해야 회수됩니다:
     1) wsl --shutdown
     2) wsl --manage Ubuntu --set-sparse true
     3) wsl -d Ubuntu -e true    (다시 기동)
EOF
rm -f "$STATE.tick"
exit 0
