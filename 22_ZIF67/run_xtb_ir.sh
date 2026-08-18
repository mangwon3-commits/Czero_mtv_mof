#!/bin/bash
# GFN2-xTB 로 링커의 IR 진동수와 세기를 낸다.
#
# --ohess = 기하 최적화 후 헤시안. 최적화하지 않고 헤시안을 뜨면 허수 진동수가
#           쏟아져 아무것도 못 읽습니다.
# --chrg  = 전하. **틀리면 전자 수가 달라져 진동수가 통째로 어긋납니다.**
#           xyz 두 번째 줄에 적어 둔 charge= 를 그대로 읽어 씁니다.
#
# 격리 환경(spectra)의 xtb 를 씁니다. czeromof 에는 RASPA 가 돌고 있어
# 건드리면 안 됩니다. nice 19 로 본 계산에 양보합니다.
SP=/home/mangwon1/miniconda3/envs/spectra/bin
Q=/home/mangwon1/mof_project/22_ZIF67
XYZ="$Q/spectra/xyz"
RUN="$Q/spectra/runs"
mkdir -p "$RUN"

command -v "$SP/xtb" > /dev/null || { echo "xtb 없음: $SP/xtb"; exit 1; }
echo "xtb: $("$SP/xtb" --version 2>&1 | grep -i 'xtb version' | head -1)"
echo

ok=0; fail=0
for f in "$XYZ"/*.xyz; do
  n=$(basename "$f" .xyz)
  c=$(sed -n '2p' "$f" | grep -o 'charge=-\?[0-9]*' | cut -d= -f2)
  [ -z "$c" ] && c=0
  d="$RUN/$n"
  mkdir -p "$d"
  cp "$f" "$d/mol.xyz"
  printf "  %-14s 전하 %-3s " "$n" "$c"
  ( cd "$d" && nice -n 19 "$SP/xtb" mol.xyz --ohess --chrg "$c" \
      > xtb.log 2>&1 )
  if grep -q 'normal termination' "$d/xtb.log" && [ -f "$d/vibspectrum" ]; then
    # 허수 진동수 개수 (음수 파수). 있으면 최소점이 아니다.
    im=$(awk '/^\$vibrational spectrum/,/^\$end/' "$d/vibspectrum" \
         | awk 'NF>=6 && $3+0 < -1 {n++} END{print n+0}')
    echo "완료  허수진동수 $im"
    ok=$((ok+1))
  else
    echo "실패 (xtb.log 확인)"
    tail -3 "$d/xtb.log" | sed 's/^/        /'
    fail=$((fail+1))
  fi
done
echo
echo "=== 완료 $ok / 실패 $fail ==="
exit 0
