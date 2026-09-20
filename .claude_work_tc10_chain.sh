#!/bin/bash
# T-C10 — saIm0583 앙상블 보강 e6~e10. 등록 21_ZIF69_MTV/TC10_REGISTRATION_20260920.md (자료 0건).
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tc10_chain.sh > .claude_work_tc10.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). 죽일 때는 PID 로(§4).
#
# 앞단(②이완 ③판정 ④전하)은 (가) Q_st(n) 8슬롯 옆에서 nice 19 로 돕니다(§5 "부수 작업").
# ⑤관문(Zeo++ 9.5 GB)·⑥본계산은 **simulate 0** 을 기다립니다 — §5 Zeo++/RASPA 동시 금지.
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
: "${RASPA_DIR:=$HOME/RASPA/simulations}"; export RASPA_DIR
pick(){ for p in "$@"; do [ -x "$p" ] && { echo "$p"; return; }; done; echo ""; }
CZ="${CZ:-$(pick "$HOME/miniconda3/envs/czeromof/bin/python" "$HOME/anaconda3/envs/czeromof/bin/python")}"
CT="${CT:-$(pick "$HOME/miniconda3/envs/coremof_tools/bin/python" "$HOME/anaconda3/envs/coremof_tools/bin/python")}"
XTB="${XTB_BIN:-$HOME/miniconda3/envs/spectra/bin/xtb}"
RW="${RELAX_WORKERS:-2}"; WW="${HWC_V3W_WORKERS:-8}"
TAGS="saIm0583e6,saIm0583e7,saIm0583e8,saIm0583e9,saIm0583e10"
RESULT="humid_working_capacity_w2_saIm0583e_ext_desk.json"
L=tc10_chain.log
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$L"; }
die(){ say "!! $*"; exit 1; }
nsim(){ pgrep -xc simulate; }

say "================ T-C10 사슬 시작  CZ=$CZ  RELAX_WORKERS=$RW  WC 워커=$WW ================"
[ -n "$CZ" ] || die "czeromof 파이썬 없음"
[ -n "$CT" ] || die "coremof_tools 파이썬 없음"
[ -x "$XTB" ] || die "xtb 없음: $XTB"
export XTB_BIN="$XTB"; export PATH="$(dirname "$CZ"):$PATH"

# --- ① 빌드는 이미 끝났습니다(17:4x, 5/5 채택) ---
n=$(ls structures_v2/ZIF69_saIm0583e[6-9].cif structures_v2/ZIF69_saIm0583e10.cif 2>/dev/null | wc -l)
say "① 빌드 CIF $n/5 (이미 만들어져 있어야 합니다)"
[ "$n" -ge 5 ] || die "빌드 5/5 아님 — build_ensemble_0583_ext.py 를 먼저 도십시오"

# --- ② 이완 (nice 19, RASPA 옆에서) ---
say "② 이완 RELAX_WORKERS=$RW (nice 19 — (가) 8슬롯 옆)"
RELAX_WORKERS="$RW" nice -n 19 "$CZ" -u relax_series_v3.py >> "$L" 2>&1; rc=$?
n=$(ls relax_v3/ZIF69_saIm0583e[6-9]_relaxed.cif relax_v3/ZIF69_saIm0583e10_relaxed.cif 2>/dev/null | wc -l)
say "이완 rc=$rc, 새 CIF $n/5"
[ "$n" -ge 5 ] || die "이완 5/5 아님"

# --- ③ 판정 ---
say "③ 판정 judge_relax_v3"
nice -n 19 "$CZ" -u judge_relax_v3.py >> "$L" 2>&1
nice -n 19 "$CZ" - >> "$L" 2>&1 <<'PY' || die "판정 5/5 pass 아님 — 사람이 볼 것"
import json, sys
rows = json.load(open('relax_v3_judged.json'))
rows = rows['rows'] if isinstance(rows, dict) else rows
want = {f'ZIF69_saIm0583e{i}' for i in (6, 7, 8, 9, 10)}
mine = [r for r in rows if r.get('name') in want]
print([(r['name'], r.get('pass')) for r in mine])
sys.exit(0 if len(mine) >= 5 and all(r.get('pass') for r in mine) else 1)
PY

# --- ④ 전하 (PACMAN DDEC6) ---
say "④ 전하 PACMAN"
nice -n 19 "$CT" -u charge_v3.py >> "$L" 2>&1
n=$(ls charged_v3/saIm0583e[6-9]_DDEC6.cif charged_v3/saIm0583e10_DDEC6.cif 2>/dev/null | wc -l)
say "전하 CIF $n/5"
[ "$n" -ge 5 ] || die "전하 5/5 아님"

# --- ⑤ 관문 — simulate·network 0 을 3분 연속 (Zeo++ 9.5 GB, §5) ---
say "⑤ 관문 대기 — simulate $(nsim) 이 0 이 될 때까지 (Q_st(n) 완주 전망 09-21 16:30 이후)"
q=0; while [ $q -lt 3 ]; do
  if [ "$(nsim)" -gt 0 ] || [ "$(pgrep -xc network)" -gt 0 ]; then q=0; else q=$((q+1)); fi
  sleep 60
done
say "simulate·network 0 (3분 연속) 확인 — 관문 착수"
[ -f risk_results_v3sub.json ] && cp -a risk_results_v3sub.json "risk_results_v3sub.before_tc10_$(date +%m%d%H%M).json"
[ -f risk_v3sub_index.json ] && cp -a risk_v3sub_index.json "risk_v3sub_index.before_tc10_$(date +%m%d%H%M).json"
RISK_SUB_TAGS="base,saIm0583,saIm0583e6,saIm0583e7,saIm0583e8,saIm0583e9,saIm0583e10" \
  nice -n 10 "$CZ" -u risk_screen_v3_sub.py >> "$L" 2>&1; rc=$?
say "관문 rc=$rc — 통과 여부는 종합자가 읽습니다(등록 §4)"
[ "$rc" -eq 0 ] || die "관문 rc=$rc — WC 를 안 띄우고 멈춤"
cp -a risk_results_v3sub.json risk_results_tc10.json 2>/dev/null

# --- ⑥ 습윤 WC 15작업 ---
say "⑥ 습윤 WC — 타깃 $TAGS, 워커 $WW, 결과 $RESULT"
HWC_V3W_TARGETS="$TAGS" HWC_V3W_WORKERS="$WW" HWC_V3W_RESULT="$RESULT" \
  "$CZ" -u run_humid_wc_v3w.py >> "$L" 2>&1; rc=$?
say "WC rc=$rc"
[ -f "v3w_humid_wc/$RESULT" ] && say "결과 파일 생성 — 완주" || say "!! 결과 파일 없음 — 비정상"
say "T-C10 사슬 종료. 판정은 등록 §3·§4 그대로."
