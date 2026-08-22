#!/bin/bash
# 승자 조성 saIm0583 수분 4작업 — 앙상블 체인이 끝난 뒤 시작.
# 나머지 12작업(0625/0667/0875)은 랩탑이 맡습니다.
#
# [왜 기다리나] 앙상블의 GCMC 단계가 Zeo++ 를 먼저 도는데 v3 구조에서 건당
# 9.5 GB 입니다. CLAUDE.md 5절이 "RASPA 가 돌 때 Zeo++ 를 같이 띄우지 말라"고
# 못 박은 조합이고, 08-12 에 OOM 이 dbus 까지 죽여 WSL 을 먹통으로 만들었습니다.
L=$HOME/.claude_work/water4.log
E=$HOME/.claude_work/ens0583.log
P=/home/mangwon1/mof_project/21_ZIF69_MTV
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
export WATER_BATCH_TAG=desktop4
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
cd "$P" || exit 1

say "=== 대기: 앙상블 체인 종료 ==="
# 성공("체인 끝")과 실패("!!") 양쪽을 봅니다 — 성공만 기다리면 앙상블이
# 죽었을 때 영원히 안 뜹니다.
for i in $(seq 1 2880); do
  grep -q "ens0583 체인 끝\|!!" "$E" 2>/dev/null && { say "앙상블 종료 감지"; break; }
  sleep 30
done
grep -q "ens0583 체인 끝\|!!" "$E" 2>/dev/null || {
  say "!! 24시간 안에 앙상블이 안 끝났습니다. 물 4작업을 시작하지 않습니다."; exit 1; }

for i in $(seq 1 60); do
  n=$(pgrep -x xtb | wc -l); m=$(pgrep -x simulate | wc -l); z=$(pgrep -x network | wc -l)
  [ "$n" -eq 0 ] && [ "$m" -eq 0 ] && [ "$z" -eq 0 ] && break
  say "잔여 xtb=$n simulate=$m network=$z — 대기"
  sleep 60
done

FREE=$(awk '/MemAvailable/{printf "%d", $2/1024/1024}' /proc/meminfo)
PHYS=$(lscpu -p=Core,Socket | grep -v '^#' | sort -u | wc -l)
say "--- 물 4작업 시작 (물리 ${PHYS}코어, 가용 ${FREE} GB) ---"
say "4작업이 한 파도. 승자 관문은 RH90 이 끝나야 닫힙니다(20~23시간 예상)"
WATER_V3_WORKERS="$PHYS" nice -n 5 "$CZ" -u run_water_v3grid_0583.py >> "$L" 2>&1
say "러너 종료코드 $?"
if [ -f v3_water_grid/water_results.json ]; then
  n=$("$CZ" -c "import json;print(len(json.load(open('v3_water_grid/water_results.json'))))" 2>/dev/null)
  say "결과 행수 $n (기대 4)"
  say "기기 태그 사본은 러너가 water_results_desktop4.json 으로 만듭니다"
fi
say "=== 물 4작업 끝 ==="
