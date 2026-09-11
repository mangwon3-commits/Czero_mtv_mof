#!/usr/bin/env bash
# T-NF-0e — 포화 근처 적재 탈착. 등록 TNF0E_REGISTRATION_20260911.md
# 순서는 **싸고 정보 많은 것부터** (등록문 §5). ZIF-90 이 먼저입니다.
# --temp 와 --psat 를 **명시**합니다 — 기본값 303.0 이 조용히 다른 온도를 만듭니다.
set -u
PY=/home/skyjun/miniconda3/envs/czeromof/bin/python
cd "$(dirname "$0")"
run () {  # $1 조성  $2 CIF  $3 적재  $4 태그접미  $5 씨앗번호
  echo "=== $(date '+%F %H:%M:%S')  $1  적재 $3  씨앗 $5 ==="
  $PY run_tnf.py --cif "$2" --tag "$4_s$5" --preload-water "$3" \
      --rh 90 --temp 298 --pco2 0.15 --psat 3169.0 --workers 1 \
      --runs-root "tnf0e_runs_$4_s$5" >> "tnf0e_$4_s$5.log" 2>&1
  echo "    rc=$? $(date '+%H:%M:%S')"
}
for s in 1 2; do
  run zif90 charged_v3/zif90_DDEC6.cif 338 zif90e050 $s &
done
wait
for s in 1 2; do
  run zif90 charged_v3/zif90_DDEC6.cif 676 zif90e100 $s &
done
wait
echo "=== ZIF-90 4건 완료 $(date '+%F %H:%M:%S') — 속도 보고 후 나머지 결정 ==="
