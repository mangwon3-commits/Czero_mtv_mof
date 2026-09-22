#!/bin/bash
# T-C10 이어받기 — ⑤관문(환경 정정) → ⑥습윤 WC. 등록 21_ZIF69_MTV/TC10_REGISTRATION_20260920.md.
#
# [왜 다시] 09-21 17:09:28 에 원 사슬(.claude_work_tc10_chain.sh)이 ⑤관문에서 rc=2 로 멈췄습니다.
#   원인은 계산이 아니라 **인터프리터**입니다 — 사슬이 $CZ(czeromof)로 관문을 띄웠는데
#   risk_screen_v3_sub.py 는 lammps_interface·lmp_serial 이 필요하고 그건 lammps_mof 환경에 있습니다.
#   관문의 사전검사가 "아무것도 안 돌리고 중단" 한 것은 **옳은 동작**입니다(§0 — 실패가 결과처럼 보이지 않게).
#   그래서 그 뒤 6시간 동안 데스크탑이 놀았습니다(17:09 → 23:0x).
#
# [고친 것 하나] 관문만 lammps_mof 파이썬으로. **다른 것은 아무것도 안 바꿉니다** — 태그·워커·결과 경로·
#   나머지 단계 전부 원 사슬 그대로입니다(§AS 계열 고정값 불변, CLAUDE.md §1).
#
# 기동: cd ~/mof_project && setsid nohup bash .claude_work_tc10_resume.sh > .claude_work_tc10_resume.out 2>&1 < /dev/null &
# 돌고 있는 이 파일을 편집하지 마십시오(CLAUDE.md §6). 죽일 때는 PID 로(§4).
set -u
cd "$(dirname "$0")/21_ZIF69_MTV" || exit 1
: "${RASPA_DIR:=$HOME/RASPA/simulations}"; export RASPA_DIR
CZ=$HOME/miniconda3/envs/czeromof/bin/python
LM=$HOME/miniconda3/envs/lammps_mof/bin/python
TAGS="saIm0583e6,saIm0583e7,saIm0583e8,saIm0583e9,saIm0583e10"
RESULT="humid_working_capacity_w2_saIm0583e_ext_desk.json"
WW="${HWC_V3W_WORKERS:-8}"
L=tc10_chain.log
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" | tee -a "$L"; }
die(){ say "!! $*"; exit 1; }

say "================ T-C10 이어받기 (관문 환경 정정) ================"
[ -x "$LM" ] || die "lammps_mof 파이썬 없음: $LM"
"$LM" -c 'import lammps_interface' 2>/dev/null || die "lammps_interface 임포트 실패"
[ -x "$HOME/miniconda3/envs/lammps_mof/bin/lmp_serial" ] || die "lmp_serial 없음"
export PATH="$HOME/miniconda3/envs/lammps_mof/bin:$PATH"

# ⑤ 관문 — Zeo++ 는 RASPA 와 동시에 못 돕니다(CLAUDE.md §5). 3분 연속 0 을 다시 확인합니다.
q=0; while [ $q -lt 3 ]; do
  if [ "$(pgrep -xc simulate)" -gt 0 ] || [ "$(pgrep -xc network)" -gt 0 ]; then q=0; else q=$((q+1)); fi
  sleep 60
done
say "simulate·network 0 (3분 연속) 확인 — 관문 착수 (lammps_mof 파이썬)"
[ -f risk_results_v3sub.json ] && cp -a risk_results_v3sub.json "risk_results_v3sub.before_tc10r_$(date +%m%d%H%M).json"
[ -f risk_v3sub_index.json ] && cp -a risk_v3sub_index.json "risk_v3sub_index.before_tc10r_$(date +%m%d%H%M).json"
RISK_SUB_TAGS="base,saIm0583,saIm0583e6,saIm0583e7,saIm0583e8,saIm0583e9,saIm0583e10" \
  nice -n 10 "$LM" -u risk_screen_v3_sub.py >> "$L" 2>&1; rc=$?
say "관문 rc=$rc — 통과 여부는 종합자가 읽습니다(등록 §4)"
[ "$rc" -eq 0 ] || die "관문 rc=$rc — WC 를 안 띄우고 멈춤"
cp -a risk_results_v3sub.json risk_results_tc10.json 2>/dev/null

# ⑥ 습윤 WC 15작업 — 원 사슬 그대로, czeromof 파이썬
say "⑥ 습윤 WC — 타깃 $TAGS, 워커 $WW, 결과 $RESULT"
HWC_V3W_TARGETS="$TAGS" HWC_V3W_WORKERS="$WW" HWC_V3W_RESULT="$RESULT" \
  "$CZ" -u run_humid_wc_v3w.py >> "$L" 2>&1; rc=$?
say "WC rc=$rc"
[ -f "v3w_humid_wc/$RESULT" ] && say "결과 파일 생성 — 완주" || say "!! 결과 파일 없음 — 비정상"
say "T-C10 이어받기 종료. 판정은 등록 §3·§4 그대로."
