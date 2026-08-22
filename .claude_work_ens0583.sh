#!/bin/bash
# saIm0583 앙상블 5종: 이완 -> 판정 -> 전하 -> 건조 GCMC. 각 단계 실패 시 중단.
# 사전 등록: 21_ZIF69_MTV/ENSEMBLE_0583_PROTOCOL.md
L=$HOME/.claude_work/ens0583.log
P=/home/mangwon1/mof_project/21_ZIF69_MTV
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin/python
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
TAGS="saIm0583e1 saIm0583e2 saIm0583e3 saIm0583e4 saIm0583e5"
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
cd "$P" || exit 1
say "=== ens0583 체인 시작 ==="
say "--- 이완 (새 5종만, 기존 37종은 건너뜀) ---"
nice -n 10 "$CZ" -u relax_series_v3.py >> "$L" 2>&1
n=0; for t in $TAGS; do [ -f "relax_v3/ZIF69_${t}_relaxed.cif" ] && n=$((n+1)); done
say "이완 결과 CIF $n/5"
[ "$n" -eq 5 ] || { say "!! 이완 미완 — 중단"; exit 1; }
say "--- 판정 ---"
"$CZ" -u judge_relax_v3.py >> "$L" 2>&1 || { say "!! 판정 실패"; exit 1; }
"$CZ" - <<'PY' >> "$L" 2>&1
import json,sys
d=json.load(open('relax_v3_judged.json'))
rows=d['rows'] if isinstance(d,dict) and 'rows' in d else d
bad=[r['name'] for r in rows if 'saIm0583e' in r['name'] and not r.get('pass')]
print('앙상블 판정 탈락:', bad if bad else '없음')
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || { say "!! 판정 탈락 있음 — GCMC 로 보내지 않음"; exit 1; }
say "--- 전하 (PACMAN, coremof_tools) ---"
"$CT" -u charge_v3.py >> "$L" 2>&1 || { say "!! 전하 실패"; exit 1; }
say "--- 건조 GCMC (5종, 결과는 results_v3ens0583.json 으로 분리) ---"
V3_WORKERS=6 nice -n 10 "$CZ" -u run_gcmc_v3.py --only $TAGS \
  --out results_v3ens0583.json >> "$L" 2>&1 || { say "!! GCMC 실패"; exit 1; }
say "=== ens0583 체인 끝 — results_v3ens0583.json ==="
