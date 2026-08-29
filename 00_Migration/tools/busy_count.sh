#!/bin/bash
# 계산이 몇 개 도는지 한 숫자로 출력한다. 그 외에는 아무것도 안 찍는다.
#
# **별도 파일인 이유**: 패턴을 호출 명령줄에 두면 pgrep -f 가 호출자 자신을
# 잡습니다. 2026-08-28 에 이 자기매칭으로 감시기가 30분간 자기 자신을 보고
# "바쁨" 이라 판단해 동작을 막았습니다. 파일 안에 두면 명령줄에 안 나옵니다.
n=0
for c in simulate lmp_serial lmp network xtb; do
  k=$(pgrep -c -x "$c" 2>/dev/null); n=$((n + ${k:-0}))
done
# 러너는 comm=python 인 것만 본다 (감시 셸이 안 걸리도록)
p=$(ps -eo comm=,args= | awk '$1 ~ /^python/ && $0 ~ /run_water|run_humid|run_gcmc|risk_screen|relax_series/' | wc -l)
echo $((n + p))
