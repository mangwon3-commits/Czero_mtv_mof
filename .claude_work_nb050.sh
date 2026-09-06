#!/bin/bash
# nbIm050e1~e5 체인 — ASSIGN_NB050_20260906.md §4. 돌고 있는 이 파일을 편집하지 마십시오 (CLAUDE.md §6).
set -u
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
export RASPA_DIR=$HOME/RASPA/simulations
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin/python
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin/python
LM=/home/mangwon1/miniconda3/envs/lammps_mof/bin
L=nb050_chain.log
TAGS="nbIm050e1 nbIm050e2 nbIm050e3 nbIm050e4 nbIm050e5"
say(){ echo "===== $(date '+%F %T') $* =====" | tee -a "$L"; }
say "① 빌드"; "$CZ" -u build_ensemble_nb050.py >> "$L" 2>&1 || { say "빌드 실패 rc=$?"; exit 1; }
n=$(ls structures_v2/ZIF69_nbIm050e[1-5].cif 2>/dev/null | wc -l); say "빌드 CIF $n/5"; [ "$n" -eq 5 ] || exit 1
say "② 이완 (3워커 xtb)"; export PATH=/home/mangwon1/miniconda3/envs/czeromof/bin:$PATH
nice -n 10 "$CZ" -u relax_series_v3.py >> "$L" 2>&1; rc=$?
n=$(ls relax_v3/ZIF69_nbIm050e[1-5]_relaxed.cif 2>/dev/null | wc -l); say "이완 rc=$rc, CIF $n/5"; [ "$n" -eq 5 ] || exit 1
say "③ 판정"; "$CZ" -u judge_relax_v3.py >> "$L" 2>&1
"$CZ" - >> "$L" 2>&1 <<'PY' || { say "판정 5/5 pass 아님"; exit 1; }
import json,sys
rows=json.load(open('relax_v3_judged.json'))['rows']; mine=[r for r in rows if r['name'].startswith('ZIF69_nbIm050e')]
print([(r['name'],r['pass']) for r in mine]); sys.exit(0 if len(mine)==5 and all(r['pass'] for r in mine) else 1)
PY
say "④ 전하 (PACMAN)"; "$CT" -u charge_v3.py >> "$L" 2>&1
n=$(ls charged_v3/nbIm050e[1-5]_DDEC6.cif 2>/dev/null | wc -l); say "전하 CIF $n/5"; [ "$n" -eq 5 ] || exit 1
"$CZ" -c "import json;c=json.load(open('charged_v3.json'))['charged'];import sys;sys.exit(0 if all(f'nbIm050e{i}' in c for i in range(1,6)) else 1)" || { say "charged_v3.json 목록 누락"; exit 1; }
say "⑤ 관문 (Zeo++, RASPA 0 확인)"; [ "$(pgrep -x simulate | wc -l)" -eq 0 ] || { say "RASPA 가동 중 — 관문 중단"; exit 2; }
PATH="$LM:$PATH" ENS_NB050_TAGS="nbIm050,nbIm050e1,nbIm050e2,nbIm050e3,nbIm050e4,nbIm050e5" nice -n 10 "$LM/python" -u risk_screen_v3ens_nb050.py >> risk_v3ens_nb050.log 2>&1; say "관문 rc=$?"
say "⑥ Widom/GCMC 5종 (V3_WORKERS=6)"; [ "$(pgrep -x network | wc -l)" -eq 0 ] || { say "Zeo++ 가동 중 — 중단"; exit 2; }
V3_WORKERS=6 nice -n 10 "$CZ" -u run_gcmc_v3.py --only $TAGS --out results_v3ens_nb050.json >> ens_nb050_gcmc.log 2>&1; say "GCMC rc=$?"
say "체인 종료"
