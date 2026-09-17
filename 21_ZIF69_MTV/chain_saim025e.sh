#!/bin/bash
# §AK saIm025e 사슬 — 앞단(빌드·이완·판정·전하·관문) + 습윤 TSA WC 15작업
# 등록: 21_ZIF69_MTV/SAIM025E_HUMID_WC_REGISTRATION_20260917.md (자료 0건)
#
# **돌고 있는 이 파일을 편집하지 마십시오** (CLAUDE.md §6 — bash 는 바이트
# 오프셋으로 읽어 엉뚱한 줄을 실행합니다).
#
# 기동:  setsid nohup bash chain_saim025e.sh > ../.claude_work_saim025e_l2.out 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")" || exit 1

# --- 기기별 경로 (laptop2 가 다르면 환경변수로 덮어쓰고 기동) -------------
: "${RASPA_DIR:=$HOME/RASPA/simulations}"; export RASPA_DIR
pick(){ for p in "$@"; do [ -x "$p" ] && { echo "$p"; return; }; done; echo ""; }
CZ="${CZ:-$(pick "$HOME/miniconda3/envs/czeromof/bin/python" "$HOME/anaconda3/envs/czeromof/bin/python")}"
CT="${CT:-$(pick "$HOME/miniconda3/envs/coremof_tools/bin/python" "$HOME/anaconda3/envs/coremof_tools/bin/python")}"
RW="${RELAX_WORKERS:-2}"
WW="${HWC_V3W_WORKERS:-12}"
RESULT="${HWC_V3W_RESULT:-humid_working_capacity_w2_saIm025e_laptop2.json}"
TAGS="saIm025e1,saIm025e2,saIm025e3,saIm025e4,saIm025e5"

L=saim025e_chain.log
say(){ echo "===== $(date '+%F %T') $* =====" | tee -a "$L"; }
die(){ say "!! $*"; exit 1; }

say "사슬 시작 — CZ=$CZ  CT=$CT  RELAX_WORKERS=$RW  WC 워커=$WW"
[ -n "$CZ" ] || die "czeromof 파이썬을 못 찾음 — CZ=... 로 주고 다시 기동"
[ -n "$CT" ] || die "coremof_tools 파이썬을 못 찾음 — CT=... 로 주고 다시 기동"

# --- ⓪ 선행 조건: RASPA 가 돌고 있으면 관문(Zeo++ 9.5 GB)이 위험 ---------
if [ "$(pgrep -x simulate | wc -l)" -gt 0 ]; then
  die "simulate 가 이미 돌고 있음 — CLAUDE.md §5(Zeo++ 와 RASPA 동시 금지). 사람이 볼 것"
fi

# --- ① 빌드 (시드 1~, 검사 통과분 5개) -----------------------------------
say "① 빌드 saIm025e1~e5"
"$CZ" -u build_ensemble_025.py >> "$L" 2>&1 || die "빌드 실패 rc=$?"
n=$(ls structures_v2/ZIF69_saIm025e*.cif 2>/dev/null | wc -l); say "빌드 CIF $n/5"
[ "$n" -ge 5 ] || die "빌드 5/5 아님"

# --- ② 이완 (xtb GFN-FF) --------------------------------------------------
say "② 이완 RELAX_WORKERS=$RW"
export PATH="$(dirname "$CZ"):$PATH"
RELAX_WORKERS="$RW" nice -n 10 "$CZ" -u relax_series_v3.py >> "$L" 2>&1; rc=$?
n=$(ls relax_v3/ZIF69_saIm025e*_relaxed.cif 2>/dev/null | wc -l); say "이완 rc=$rc, CIF $n/5"
[ "$n" -ge 5 ] || die "이완 5/5 아님"

# --- ③ 판정 (5/5 pass 아니면 사람이 본다) ---------------------------------
say "③ 판정"
"$CZ" -u judge_relax_v3.py >> "$L" 2>&1
"$CZ" - >> "$L" 2>&1 <<'PY' || die "판정 5/5 pass 아님 — 사람이 볼 것"
import json, sys
rows = json.load(open('relax_v3_judged.json'))['rows']
mine = [r for r in rows if r['name'].startswith('ZIF69_saIm025e')]
print([(r['name'], r['pass']) for r in mine])
sys.exit(0 if len(mine) >= 5 and all(r['pass'] for r in mine) else 1)
PY

# --- ④ 전하 (PACMAN DDEC6) ------------------------------------------------
say "④ 전하 PACMAN"
"$CT" -u charge_v3.py >> "$L" 2>&1
n=$(ls charged_v3/saIm025e*_DDEC6.cif 2>/dev/null | wc -l); say "전하 CIF $n/5"
[ "$n" -ge 5 ] || die "전하 5/5 아님"

# --- ⑤ 관문 (Zeo++, RASPA 0 인 지금 돌린다) -------------------------------
say "⑤ 관문 risk_screen_v3_sub (RISK_WORKERS 는 손대지 않음 — CLAUDE.md §5)"
RISK_SUB_TAGS="base,saIm025,saIm025e1,saIm025e2,saIm025e3,saIm025e4,saIm025e5" \
  nice -n 10 "$CZ" -u risk_screen_v3_sub.py >> "$L" 2>&1; rc=$?
say "관문 rc=$rc — 통과 여부는 종합자가 읽는다(등록 §4 결측 규칙)"
[ "$rc" -eq 0 ] || die "관문 rc=$rc — WC 를 띄우지 않고 멈춤. 종합자에게 보고"

# --- ⑥ 습윤 TSA WC 15작업 -------------------------------------------------
say "⑥ 습윤 WC — 타깃 $TAGS, 워커 $WW, 결과 $RESULT"
HWC_V3W_TARGETS="$TAGS" HWC_V3W_WORKERS="$WW" HWC_V3W_RESULT="$RESULT" \
  "$CZ" -u run_humid_wc_v3w.py >> "$L" 2>&1; rc=$?
say "WC rc=$rc"
[ -f "v3w_humid_wc/$RESULT" ] && say "결과 파일 생성 — 완주" || say "!! 결과 파일 없음 — 비정상"
say "사슬 종료"
