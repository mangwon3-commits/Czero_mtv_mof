#!/bin/bash
# 절벽 구조 2종(saIm0917 22/24, saIm0958 23/24) 체인:
#   [대기] 이완 -> 판정 -> 전하 -> 건조 GCMC -> 물 RH0/RH90
# 각 단계 실패 시 중단합니다. 사전 등록: 21_ZIF69_MTV/ASSIGN_48H_20260824.md
#
# [왜 이완을 다시 띄우지 않고 기다리나]
#   이완은 09:41 에 이미 따로 띄웠습니다(PID 11745). relax_series_v3.py 의
#   "있으면 건너뜀" 판정은 **결과 CIF 가 다 만들어진 뒤에야** 참이 되므로,
#   지금 두 번째 인스턴스를 띄우면 같은 두 구조를 양쪽이 동시에 계산합니다.
#   건너뛰기가 그것을 막아 주지 않습니다. 그래서 띄우지 않고 기다립니다.
L=$HOME/.claude_work/cliff.log
P=/home/mangwon1/mof_project/21_ZIF69_MTV
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin/python
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
TAGS="saIm0917 saIm0958"
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
cd "$P" || exit 1

say "=== 절벽 체인 시작 (saIm0917 saIm0958) ==="

# ---------------------------------------------------------------- 0. 이완 대기
say "--- 이완 완료 대기 (이미 도는 것을 기다림, 최대 8시간) ---"
for i in $(seq 1 480); do
  pgrep -f 'relax_series_v3' > /dev/null || break
  sleep 60
done
if pgrep -f 'relax_series_v3' > /dev/null; then
  say "!! 8시간 안에 이완이 끝나지 않았습니다. 중단합니다."
  exit 1
fi
# 프로세스가 사라진 것과 결과가 나온 것은 다릅니다 — 이 저장소가 반복해서
# 데인 유형이라 파일로 확인합니다.
sleep 30
n=0; for t in $TAGS; do [ -f "relax_v3/ZIF69_${t}_relaxed.cif" ] && n=$((n+1)); done
say "이완 결과 CIF $n/2"
[ "$n" -eq 2 ] || { say "!! 이완 미완 — 중단"; exit 1; }

# ---------------------------------------------------------------- 1. 판정
say "--- 판정 ---"
"$CZ" -u judge_relax_v3.py >> "$L" 2>&1 || { say "!! 판정 실패"; exit 1; }
"$CZ" - <<'PY' >> "$L" 2>&1
import json, sys
d = json.load(open('relax_v3_judged.json'))
rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
want = {'ZIF69_saIm0917', 'ZIF69_saIm0958', 'saIm0917', 'saIm0958'}
mine = [r for r in rows if r['name'] in want]
print('절벽 2종 판정:', [(r['name'], r.get('pass')) for r in mine])
if len(mine) != 2:
    print('!! 판정 행이 2개가 아닙니다 — 이름 규약 확인 필요')
    sys.exit(1)
bad = [r['name'] for r in mine if not r.get('pass')]
print('탈락:', bad if bad else '없음')
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || { say "!! 판정 탈락 — 하류로 보내지 않음"; exit 1; }

# ---------------------------------------------------------------- 2. 전하
say "--- 전하 (PACMAN, coremof_tools) ---"
"$CT" -u charge_v3.py >> "$L" 2>&1 || { say "!! 전하 실패"; exit 1; }
n=0; for t in $TAGS; do [ -f "charged_v3/${t}_DDEC6.cif" ] && n=$((n+1)); done
say "전하 CIF $n/2"
[ "$n" -eq 2 ] || { say "!! 전하 CIF 미완 — 중단"; exit 1; }

# ---------------------------------------------------------------- 3. 건조 GCMC
# Zeo++ network 가 v3 구조 한 건에 9.5 GB 입니다(5 절). RASPA 와 겹치면
# 08-12 의 OOM 재현이라, 이 체인은 순차이고 다른 계산이 없을 때만 돕니다.
# RISK_WORKERS 를 손으로 주지 않습니다 — 스크립트가 /proc/meminfo 로 정합니다.
say "--- 건조 GCMC (결과는 results_v3cliff.json 으로 분리) ---"
V3_WORKERS=6 nice -n 10 "$CZ" -u run_gcmc_v3.py --only $TAGS \
  --out results_v3cliff.json >> "$L" 2>&1 || { say "!! GCMC 실패"; exit 1; }
[ -f results_v3cliff.json ] || { say "!! results_v3cliff.json 없음"; exit 1; }
say "건조 GCMC 완료"

# ---------------------------------------------------------------- 4. 물
say "--- 물 RH0/RH90 (4작업, 예상 ~12h) ---"
WATER_BATCH_TAG=desktopcliff WATER_V3_WORKERS=8 nice -n 5 \
  "$CZ" -u run_water_v3cliff.py >> "$L" 2>&1
rc=$?
say "물 러너 종료코드 $rc"

# ---------------------------------------------------------------- 5. 마무리
if [ -f v3_water_grid_cliff/water_results_desktopcliff.json ]; then
  n=$("$CZ" -c "import json;print(len(json.load(open('v3_water_grid_cliff/water_results_desktopcliff.json'))))" 2>/dev/null)
  say "절벽 물 결과 $n행 (기대 4)"
  say "유지율:"
  "$CZ" - <<'PY' >> "$L" 2>&1
import json
rows = json.load(open('v3_water_grid_cliff/water_results_desktopcliff.json'))
by = {}
for r in rows:
    by.setdefault(r['name'], {})[r['RH']] = r
for n in sorted(by):
    d = by[n]
    if 0.0 in d and 0.9 in d:
        pct = d[0.9]['CO2_molkg'] / d[0.0]['CO2_molkg'] * 100
        print(f"  {n}  RH0 {d[0.0]['CO2_molkg']:.4f}  RH90 {d[0.9]['CO2_molkg']:.4f}  유지율 {pct:.1f}%")
print()
print('  비교: 87.5% = 74.2 pp (고원 안) / 100% = 60.6 pp (절벽)')
print('  사전 등록 관문: >=80 유효 / 50~80 조건부 / <50 종료')
PY
fi
say "=== 절벽 체인 끝 ==="
