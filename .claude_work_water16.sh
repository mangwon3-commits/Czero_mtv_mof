#!/bin/bash
# 격자 나머지 3종 16작업 — 앙상블 체인이 끝난 뒤에 시작한다.
#
# [왜 기다리나]
#   지금 붙이면 앙상블과 코어가 겹칩니다(앙상블 실측 3.4/8코어). 더 중요한 것은
#   앙상블의 GCMC 단계가 Zeo++ 를 먼저 도는데, CLAUDE.md 5절이 "RASPA 가 돌 때
#   Zeo++ 를 같이 띄우지 말라"고 못 박은 조합이라는 점입니다 -- 08-12 에 그 조합이
#   OOM 으로 dbus 까지 죽여 WSL 을 통째로 먹통으로 만들었습니다.
#   그래서 겹치지 않게 순서대로 돌립니다. 노는 시간은 없습니다.
L=$HOME/.claude_work/water16.log
E=$HOME/.claude_work/ens0583.log
P=/home/mangwon1/mof_project/21_ZIF69_MTV
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
cd "$P" || exit 1

say "=== 대기 시작: 앙상블 체인 종료를 기다립니다 ==="
# 최대 24시간. 끝 표시는 성공("체인 끝")과 실패("!!") 양쪽을 다 봅니다 --
# 성공만 기다리면 앙상블이 죽었을 때 영원히 안 뜹니다.
for i in $(seq 1 2880); do
  if grep -q "ens0583 체인 끝\|!!" "$E" 2>/dev/null; then
    say "앙상블 체인 종료 감지"
    break
  fi
  sleep 30
done
if ! grep -q "ens0583 체인 끝\|!!" "$E" 2>/dev/null; then
  say "!! 24시간 안에 앙상블이 끝나지 않았습니다. 물 16작업을 시작하지 않습니다."
  exit 1
fi

# 앙상블 잔여 프로세스가 완전히 빠질 때까지 한 번 더 확인합니다.
for i in $(seq 1 60); do
  n=$(pgrep -x xtb | wc -l); m=$(pgrep -x simulate | wc -l); z=$(pgrep -x network | wc -l)
  [ "$n" -eq 0 ] && [ "$m" -eq 0 ] && [ "$z" -eq 0 ] && break
  say "잔여 프로세스 xtb=$n simulate=$m network=$z — 대기"
  sleep 60
done

FREE=$(awk '/MemAvailable/{printf "%d", $2/1024/1024}' /proc/meminfo)
PHYS=$(lscpu -p=Core,Socket | grep -v '^#' | sort -u | wc -l)
say "1파도(워커 8): saIm0583 4작업 전부 + saIm0625 4작업 — 승자 조성이 먼저 끝납니다"
say "--- 물 16작업 시작 (물리 ${PHYS}코어, 가용 ${FREE} GB) ---"
WATER_V3_WORKERS="$PHYS" nice -n 5 "$CZ" -u run_water_v3grid.py >> "$L" 2>&1
rc=$?
say "러너 종료코드 $rc"
if [ -f v3_water_grid/water_results.json ]; then
  n=$("$CZ" -c "import json;print(len(json.load(open('v3_water_grid/water_results.json'))))" 2>/dev/null)
  say "결과 행수 $n (기대 16)"
  # 어느 기기가 낸 값인지 되돌릴 수 있게 기기 이름을 붙여 사본을 남깁니다.
  cp v3_water_grid/water_results.json "v3_water_grid/water_results_desktop16.json"
  say "사본 저장: v3_water_grid/water_results_desktop16.json"
fi
say "=== 물 16작업 끝 ==="
