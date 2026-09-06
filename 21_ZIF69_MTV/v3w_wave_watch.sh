#!/bin/bash
# 1파도 -> 2파도 전환 감시. 11작업 / 8워커라 **8건이 끝나야** 워커가 빕니다.
#   진행 중 simulate 수:  8 (1파도)  ->  3 (2파도)  ->  0 (완주)
# 워커가 5개 뜨는 그 시점에 laptop2 몫을 가져오기 위한 것입니다 (CLAUDE.md §9).
# **돌고 있는 이 파일을 편집하지 마십시오** (CLAUDE.md §6).
set -u
cd /home/skyjun/mof_project/21_ZIF69_MTV || exit 1
echo "감시 시작 $(date '+%F %T')  — simulate 8 -> 3 전환을 기다립니다"
while true; do
  n=$(pgrep -x simulate | wc -l)      # §4: grep 은 자기 셸 줄까지 셉니다
  d=$(ls water_runs_v3w 2>/dev/null | wc -l)
  if [ "$n" -le 3 ]; then
    echo "=== $(date '+%F %T')  전환 감지: simulate $n 개, 실행 폴더 $d 개 ==="
    ls water_runs_v3w 2>/dev/null | tr '\n' ' '; echo
    echo "완주 판정은 결과 JSON 으로: $([ -f v3w_water/water_results.json ] && echo 있음 || echo 아직)"
    [ "$n" -eq 0 ] && echo "!! simulate 0 — 완주이거나 죽은 것. 로그 확인 필요"
    exit 0
  fi
  sleep 600
done
