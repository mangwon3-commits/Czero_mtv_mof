#!/bin/bash
# saIm050 앙상블 5실현: 이완 -> 판정 -> 전하. 여기까지가 데스크탑 몫입니다.
# 습윤 WC 15작업은 Junseok 이 받습니다 (xtb·PACMAN 이 이 기기에만 있어
# 앞 세 단계가 데스크탑 전용이고, 뒤는 전하 CIF 만 있으면 어디서든 돕니다).
# 사전 등록: 21_ZIF69_MTV/ENSEMBLE_0500_PROTOCOL.md
L=$HOME/.claude_work/ens0500.log
P=/home/mangwon1/mof_project/21_ZIF69_MTV
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin/python
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
TAGS="saIm050e1 saIm050e2 saIm050e3 saIm050e4 saIm050e5"
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
cd "$P" || exit 1

say "=== saIm050 앙상블 체인 시작 (5실현) ==="

# ---------------------------------------------------------------- 1. 이완
say "--- 이완 (새 5종만, 기존 49종은 건너뜀) ---"
nice -n 10 "$CZ" -u relax_series_v3.py >> "$L" 2>&1
n=0; for t in $TAGS; do [ -f "relax_v3/ZIF69_${t}_relaxed.cif" ] && n=$((n+1)); done
say "이완 결과 CIF $n/5"
[ "$n" -eq 5 ] || { say "!! 이완 미완 — 중단"; exit 1; }

# ---------------------------------------------------------------- 2. 판정
say "--- 판정 ---"
"$CZ" -u judge_relax_v3.py >> "$L" 2>&1 || { say "!! 판정 실패"; exit 1; }
"$CZ" - <<'PY' >> "$L" 2>&1
import json, sys
d = json.load(open('relax_v3_judged.json'))
rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
mine = [r for r in rows if r['name'].startswith('ZIF69_saIm050e')]
print('saIm050 앙상블 판정:', [(r['name'], r.get('pass')) for r in mine])
if len(mine) != 5:
    print(f'!! 판정 행이 5개가 아닙니다 ({len(mine)}개) — 이름 규약 확인')
    sys.exit(1)
bad = [r['name'] for r in mine if not r.get('pass')]
print('탈락:', bad if bad else '없음')
sys.exit(1 if bad else 0)
PY
[ $? -eq 0 ] || { say "!! 판정 탈락 — 하류로 보내지 않음"; exit 1; }

# ---------------------------------------------------------------- 3. 전하
say "--- 전하 (PACMAN, coremof_tools) ---"
"$CT" -u charge_v3.py >> "$L" 2>&1 || { say "!! 전하 실패"; exit 1; }
n=0; for t in $TAGS; do [ -f "charged_v3/${t}_DDEC6.cif" ] && n=$((n+1)); done
say "전하 CIF $n/5"
[ "$n" -eq 5 ] || { say "!! 전하 CIF 미완 — 중단"; exit 1; }

# ---------------------------------------------------------------- 4. 인계 준비
# 데스크탑 몫은 여기까지입니다. GCMC 와 물은 Junseok 이 받습니다.
say "--- 인계 준비 완료 ---"
say "전하 CIF 5개: $(for t in $TAGS; do printf '%s ' charged_v3/${t}_DDEC6.cif; done)"
say "다음: 사람이 커밋·푸시하면 Junseok 이 pull 해서 습윤 WC 15작업"
say "=== saIm050 앙상블 체인 끝 (데스크탑 몫) ==="
