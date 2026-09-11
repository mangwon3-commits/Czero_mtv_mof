#!/usr/bin/env bash
# T-NF-0e 2단계 — 우리 3조성 12건. 등록 TNF0E_REGISTRATION_20260911.md
#
# ⚠️ 오늘 이 판에서 두 번 데었습니다. 둘 다 코드에 박아 둡니다:
#   ① **씨앗 충돌** — 같은 초 착수는 같은 난수열. STAGGER 로 어긋내고 씨앗을 되읽어 대조합니다.
#   ② **코어 초과** — 초판이 12건을 한꺼번에 띄워 8코어를 넘겼습니다(CLAUDE.md §5).
#      **한 파 6건**으로 끊고, 앞 파가 끝나야 뒤 파를 띄웁니다.
# ⚠️ --temp / --psat 명시 (run_tnf.py 기본값 303.0 함정).
#
# 적재는 등록문 §2 표(헬륨 공극 x 액체 물 밀도).
# 파 구성: 조성별로 50%·100% 를 같은 파에 둡니다 — 주 판정 (A)가 그 둘의 비이므로
#          한 파가 실패해도 **판정 단위가 통째로** 남거나 통째로 빠집니다.
set -u
PY=/home/skyjun/miniconda3/envs/czeromof/bin/python
STAGGER=${TNF0E_STAGGER:-7}
cd "$(dirname "$0")"

run () {  # $1 조성 $2 적재 $3 태그 $4 씨앗 $5 지연
  sleep "$5"
  echo "=== $(date '+%F %H:%M:%S')  $3_s$4  적재 $2 ==="
  $PY run_tnf.py --cif "charged_v3/$1_DDEC6.cif" --tag "$3_s$4" --preload-water "$2" \
      --rh 90 --temp 298 --pco2 0.15 --psat 3169.0 --workers 1 \
      --runs-root "tnf0e_runs_$3_s$4" >> "tnf0e_$3_s$4.log" 2>&1
  echo "    rc=$? $3_s$4 $(date '+%H:%M:%S')"
}
seedcheck () { sleep 90; echo "--- 씨앗 대조 $(date '+%H:%M:%S') ---"
  for d in "$@"; do f=$(find "$d" -name '*.data' 2>/dev/null|head -1)
    [ -n "$f" ] && echo "    $d  $(grep -m1 'Random number seed' "$f"|grep -o '[0-9]*')"; done
  echo "--- (전부 달라야 합니다) ---"; }

wave () {   # 인자: "조성 적재 태그" 셋 -> 6건
  local i=0 dirs=()
  for spec in "$@"; do
    set -- $spec
    for s in 1 2; do
      run "$1" "$2" "$3" "$s" $((i*STAGGER)) &
      dirs+=("tnf0e_runs_$3_s$s"); i=$((i+1))
    done
  done
  seedcheck "${dirs[@]}" &
  wait
}

echo "### 1파: mbIm050 + saIm050 $(date '+%F %H:%M:%S')"
wave "mbIm050 652 mb50e050" "mbIm050 1305 mb50e100" "saIm050 695 sa50e050"
echo "### 1파 끝 $(date '+%F %H:%M:%S')"

echo "### 2파: saIm050(100%) + nbIm050 $(date '+%F %H:%M:%S')"
wave "saIm050 1391 sa50e100" "nbIm050 743 nb50e050" "nbIm050 1486 nb50e100"
echo "### 2단계 12건 완료 $(date '+%F %H:%M:%S')"
