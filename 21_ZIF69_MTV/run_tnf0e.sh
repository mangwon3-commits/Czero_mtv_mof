#!/usr/bin/env bash
# T-NF-0e — 포화 근처 적재 탈착. 등록 TNF0E_REGISTRATION_20260911.md
#
# ⚠️ **초판(13:45)이 씨앗 충돌을 냈습니다.** 두 씨앗을 `&` 로 **같은 초에** 띄웠고,
#    이 RASPA 빌드는 씨앗을 **폴더 생성 시각(초)** 으로 정하므로 둘이 같은 난수열을
#    받아 **모든 자리가 동일한 결과**가 나왔습니다(zif90e050 s1=s2, 씨앗 1789101948).
#    오늘 `run_kh_ext.py`·`run_helium_void.py` 에는 어긋내기를 넣어 막아 놓고
#    **이 bash 드라이버에만 안 넣었습니다.**
#
#    -> **STAGGER 초만큼 어긋내 띄웁니다.** 그리고 착수 후 씨앗을 **대조**합니다.
#
# --temp 와 --psat 를 명시합니다 — 기본값 303.0 이 조용히 다른 온도를 만듭니다.
set -u
PY=/home/skyjun/miniconda3/envs/czeromof/bin/python
STAGGER=${TNF0E_STAGGER:-7}          # 초. 같은 초 = 같은 씨앗
cd "$(dirname "$0")"

run () {  # $1 CIF  $2 적재  $3 태그접두  $4 씨앗번호  $5 지연초
  sleep "$5"
  echo "=== $(date '+%F %H:%M:%S')  적재 $2  $3_s$4 (지연 ${5}s) ==="
  $PY run_tnf.py --cif "$1" --tag "$3_s$4" --preload-water "$2" \
      --rh 90 --temp 298 --pco2 0.15 --psat 3169.0 --workers 1 \
      --runs-root "tnf0e_runs_$3_s$4" >> "tnf0e_$3_s$4.log" 2>&1
  echo "    rc=$? $3_s$4 $(date '+%H:%M:%S')"
}

seedcheck () {   # 착수 뒤 씨앗을 눈으로 대조합니다
  sleep 45
  echo "--- 씨앗 대조 $(date '+%H:%M:%S') ---"
  for d in "$@"; do
    f=$(find "$d" -name '*.data' 2>/dev/null | head -1)
    [ -n "$f" ] && echo "    $d  $(grep -m1 'Random number seed' "$f" | grep -o '[0-9]*')"
  done
}

# 1차: 50 % 재실행(s2) + 100 % 둘.  전부 어긋내 띄웁니다.
run charged_v3/zif90_DDEC6.cif 338 zif90e050 2 0   &
run charged_v3/zif90_DDEC6.cif 676 zif90e100 1 $STAGGER &
run charged_v3/zif90_DDEC6.cif 676 zif90e100 2 $((STAGGER*2)) &
seedcheck tnf0e_runs_zif90e050_s2 tnf0e_runs_zif90e100_s1 tnf0e_runs_zif90e100_s2 &
wait
echo "=== ZIF-90 팔 완료 $(date '+%F %H:%M:%S') — 씨앗 대조 후 나머지 조성 결정 ==="
