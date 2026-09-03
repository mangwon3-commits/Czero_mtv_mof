#!/bin/bash
# T-B5 + T-C1 장기 체인 (laptop2 배정, ASSIGN_20260903.md §6) — 무인 실행용.
#
#   구조 22종(azbIm 025/050/075 × e0~e4, azbIm100, bIm025 × e0~e4, bIm100) + 대조 base
#   이완(GFN-FF 셀 고정) -> 판정 -> 전하(PACMAN) -> Zeo++ -> 건조 GCMC -> [T-B6 예비 물]
#
# [설계 원칙 — Claude 세션이 죽어도 WSL 이 계속 돌아야 합니다]
#   * 기동: setsid nohup bash 21_ZIF69_MTV/tb5_chain.sh < /dev/null &   (단 한 번)
#   * 모든 단계가 이어받기입니다. 죽으면 **같은 명령을 다시 치면** 완주분을 건너뜁니다.
#       이완   relax_v3/<name>_relaxed.cif 있으면 건너뜀 (relax_series_v3.py 자체 규칙)
#       전하   charged_v3/<tag>_DDEC6.cif 있으면 [이미있음]
#       GCMC   runs_v3/ 출력에 최종 로딩 줄이 있으면 cached (run_aryl_gcmc 규칙)
#       물     water_runs_lowrh_tb6/ 출력이 완주면 cached (run_water 규칙)
#   * 한 구조가 실패해도 체인은 멈추지 않습니다. 통과분만 다음 단계로 넘기고 실패는
#     로그에 남깁니다. 단계 전체가 0건이면 그때만 멈춥니다.
#   * 이 스크립트를 **돌고 있는 동안 편집하지 마세요**(CLAUDE.md §6). 고치려면 죽이고
#     고친 뒤 다시 띄우세요 — 이어받기가 완주분을 회수합니다.
#   * Zeo++ 는 이 체인 안에서 RASPA 와 겹치지 않습니다(순차). 체인이 도는 동안 **다른
#     RASPA 나 Zeo++ 를 손으로 띄우지 마세요.** run_gcmc_v3.py 가 /proc/meminfo 로 워커를
#     정하지만, 그것은 안전장치이지 허가가 아닙니다.
#
# [기기 이식성]
#   경로는 전부 $HOME 기준. 데스크탑 절대경로 없음. xtb 는 XTB_BIN 으로 덮습니다.
#   사전검사에서 하나라도 빠지면 아무것도 돌리지 않고 무엇을 설치할지 찍고 끝납니다.
#
# [환경변수 — 필요할 때만]
#   XTB_BIN            xtb 실행파일 (기본 $HOME/miniconda3/envs/spectra/bin/xtb)
#   TB5_GCMC_WORKERS   건조 GCMC 동시 작업 수 (기본 5 — laptop2 물리 6코어)
#   TB5_WATER_WORKERS  T-B6 예비 물 동시 작업 수 (기본 5)
#   TB5_SKIP_WATER=1   5단계(T-B6 예비 물) 생략
#   TB5_PREFLIGHT_ONLY=1  사전검사만 하고 끝 (띄우기 전에 한 번 돌려 보세요)
#   ZEO_GB_PER_JOB     Zeo++ 건당 메모리 GB (기본 9.5, v3 실측)

set -u
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGDIR="$HOME/.claude_work"; mkdir -p "$LOGDIR"
L="$LOGDIR/tb5_chain.log"
CZ="$HOME/miniconda3/envs/czeromof/bin/python"
CT="$HOME/miniconda3/envs/coremof_tools/bin/python"
export XTB_BIN="${XTB_BIN:-$HOME/miniconda3/envs/spectra/bin/xtb}"
export RASPA_DIR="${RASPA_DIR:-$HOME/RASPA/simulations}"
export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH"
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$L"; }
cd "$P" || exit 1

# 22종 + 대조 base. 태그(charged_v3 이름) / 구조 이름(structures_v2, relax_v3 이름)
TAGS="azbIm025 azbIm025e1 azbIm025e2 azbIm025e3 azbIm025e4 \
azbIm050 azbIm050e1 azbIm050e2 azbIm050e3 azbIm050e4 \
azbIm075 azbIm075e1 azbIm075e2 azbIm075e3 azbIm075e4 azbIm100 \
bIm025 bIm025e1 bIm025e2 bIm025e3 bIm025e4 bIm100"

say "=================== T-B5 체인 시작 (pid $$) ==================="
say "저장소 $P   로그 $L"

# ---------------------------------------------------------------- 0. 사전검사
fail=0
need(){ [ -e "$1" ] || { say "!! 없음: $1   ($2)"; fail=1; }; }
need "$CZ"  "czeromof env — NEW_MACHINE_20260822.md §3-2"
need "$CT"  "coremof_tools env — 아래 설치 안내"
need "$XTB_BIN" "xtb — XTB_BIN 으로 경로 지정 (laptop2 는 spectra env, COMMS/laptop2.md 09-03)"
need "$RASPA_DIR/share/raspa/forcefield/UFF_MOF/pseudo_atoms.def" "RASPA 힘장 트리 — NEW_MACHINE §3-3"
need "$RASPA_DIR/share/raspa/molecules/TraPPE/CO2.def" "CO2 정의(경로만 TraPPE, 모델은 García-Sánchez) — NEW_MACHINE §3-3"
need "$P/../19_WaterCompetition/water.def" "5자리 물 정의"
command -v simulate >/dev/null 2>&1 || { say "!! simulate 없음 (czeromof 의 raspa2)"; fail=1; }
command -v network  >/dev/null 2>&1 || [ -x "$HOME/miniconda3/envs/czeromof/bin/network" ] \
  || { say "!! Zeo++ network 없음 -> conda install -n czeromof -c conda-forge zeopp-lsmo=0.4.7"; fail=1; }
if [ -e "$CT" ]; then
  "$CT" -c "from PACMANCharge import pmcharge" >/dev/null 2>&1 \
    || { say "!! PACMANCharge import 실패 (coremof_tools) — 아래 설치 안내"; fail=1; }
fi
q=$(grep -E '^C_co2' "$RASPA_DIR/share/raspa/forcefield/UFF_MOF/pseudo_atoms.def" 2>/dev/null | awk '{print $7}')
[ "$q" = "0.6512" ] || { say "!! C_co2 전하가 0.6512 가 아님($q) — 힘장 트리가 우리 것이 아님"; fail=1; }
nsite=$(awk 'NF>4 && ($2=="Ow"||$2=="Hw"||$2=="Lw")' "$P/../19_WaterCompetition/water.def" 2>/dev/null | wc -l)
[ "$nsite" = "5" ] || { say "!! 물 정의 사이트 $nsite 개(5 여야 함)"; fail=1; }
n=0; for t in $TAGS; do [ -f "structures_v2/ZIF69_${t}.cif" ] && n=$((n+1)); done
[ "$n" -eq 22 ] || { say "!! structures_v2 에 22종 중 $n 종만 있음 — master 취합(build_azbim.py 결과) 확인"; fail=1; }
need "relax_fixcell/base_relaxed_gfnff_fixcell.cif" "이완 모체(charge_v3 대조군)"
need "charged_v3/base_DDEC6.cif" "모체 전하 CIF"
if [ "$fail" -ne 0 ]; then
  say "!! 사전검사 실패 — 아무것도 돌리지 않았습니다."
  say "   coremof_tools 설치(PACMAN, 데스크탑과 같은 판):"
  say "     conda create -n coremof_tools python=3.9 -y"
  say "     $HOME/miniconda3/envs/coremof_tools/bin/pip install PACMAN-charge==1.4.2 torch==2.7.0 pymatgen==2024.8.9 ase==3.26.0"
  say "   Zeo++:  conda install -n czeromof -c conda-forge zeopp-lsmo=0.4.7 -y"
  say "   고친 뒤 같은 명령으로 다시 띄우세요."
  exit 2
fi
free_gb=$(awk '/MemAvailable/{printf "%d", $2/1048576}' /proc/meminfo)
say "사전검사 통과. 코어 $(nproc)  가용메모리 ${free_gb} GB  xtb $XTB_BIN"
[ "$free_gb" -ge 14 ] || say "   주의: Zeo++ 건당 9.5 GB. 가용 ${free_gb} GB 면 워커 1 로 돕니다(자동)."
[ "${TB5_PREFLIGHT_ONLY:-0}" = "1" ] && { say "사전검사만(TB5_PREFLIGHT_ONLY=1) — 여기서 끝."; exit 0; }

# ---------------------------------------------------------------- 1. 이완
# relax_series_v3.py 는 structures_v2 전부를 훑되 relax_v3 에 있으면 건너뜁니다.
# master 에서 22종만 비어 있으므로 사실상 22종만 돕니다(워커 3 × 스레드 2).
# 실패 구조는 CIF 를 남기지 않으므로(가짜 고착 방지) 재기동하면 다시 시도합니다.
say "--- 1. 이완 (GFN-FF 셀 고정, FIRE fmax 0.05) ---"
t0=$(date +%s)
nice -n 10 "$CZ" -u relax_series_v3.py >> "$L" 2>&1
rc=$?
n=0; miss=""; for t in $TAGS; do
  if [ -f "relax_v3/ZIF69_${t}_relaxed.cif" ]; then n=$((n+1)); else miss="$miss $t"; fi; done
say "이완 완료 $n/22  (rc=$rc, $(( ($(date +%s)-t0)/60 )) 분)  미완:${miss:- 없음}"
[ "$n" -ge 1 ] || { say "!! 이완 결과 0건 — 중단. 로그 위쪽의 xtb 오류를 보세요."; exit 1; }

# ---------------------------------------------------------------- 2. 판정
say "--- 2. 판정 (judge_relax_v3.py) ---"
"$CZ" -u judge_relax_v3.py >> "$L" 2>&1
rc=$?   # 0 전부 통과 / 2 미달 있음(체인은 계속) / 1 판정 불가
[ "$rc" -ne 1 ] || { say "!! 판정 불가 — 중단"; exit 1; }
"$CZ" - "$TAGS" <<'PY' 2>&1 | tee -a "$L"
import json, sys
tags = sys.argv[1].split()
d = json.load(open('relax_v3_judged.json'))
rows = {r['name'].replace('ZIF69_', ''): r for r in d['rows']}
ok  = [t for t in tags if rows.get(t, {}).get('pass')]
bad = [t for t in tags if t in rows and not rows[t].get('pass')]
absent = [t for t in tags if t not in rows]
print(f'판정 통과 {len(ok)}/22   미달 {bad or "없음"}   미판정(이완 미완) {absent or "없음"}')
for t in bad:
    print('   미달 항목', t, [k for k, v in rows[t]['criteria'].items() if not v])
PY

# ---------------------------------------------------------------- 3. 전하
say "--- 3. 전하 (PACMAN DDEC6, coremof_tools) ---"
nice -n 10 "$CT" -u charge_v3.py >> "$L" 2>&1
rc=$?
ONLY=""; n=0; for t in $TAGS; do [ -f "charged_v3/${t}_DDEC6.cif" ] && { ONLY="$ONLY $t"; n=$((n+1)); }; done
say "전하 CIF $n/22 (rc=$rc)"
[ "$n" -ge 1 ] || { say "!! 전하 결과 0건 — 중단"; exit 1; }
# 판정 통과분에 전하가 다 붙었는지: charged_v3.json 이 통과 목록이므로 그것을 그대로 씁니다.
# (charge_v3 는 판정 미달을 스스로 제외합니다. 여기서 다시 거르지 않습니다.)

# ---------------------------------------------------------------- 4. Zeo++ + 건조 GCMC
# base 를 같은 기기에서 다시 돌려 대조군을 **같은 기기** 값으로 둡니다(3작업 추가).
# 결과는 results_tb5.json 한 파일. runs_v3/ 는 다른 태그와 공유하지만 이름이 겹치지 않습니다.
GW="${TB5_GCMC_WORKERS:-5}"
say "--- 4. Zeo++ -> 건조 GCMC (Widom CO2/N2 + GCMC 0.15 bar)  대상 $n 종 + base, 워커 $GW ---"
t0=$(date +%s)
V3_WORKERS="$GW" nice -n 10 "$CZ" -u run_gcmc_v3.py --only base $ONLY --out results_tb5.json >> "$L" 2>&1
rc=$?
say "건조 GCMC 끝 (rc=$rc, $(( ($(date +%s)-t0)/3600 )) 시간) -> results_tb5.json"
[ -f results_tb5.json ] || { say "!! results_tb5.json 없음 — 중단"; exit 1; }
"$CZ" -u tb5_report.py 2>&1 | tee -a "$L"

# ---------------------------------------------------------------- 5. T-B6 예비 — 저RH 물
# 정식 T-B6 판정은 T-B1(TIP5P-Ew ΔH_vap 자) 이후입니다. 여기서는 **수치만** 만듭니다.
# 대상 azbIm050 / azbIm100 / bIm100 이 전하까지 갔을 때만 돕니다.
if [ "${TB5_SKIP_WATER:-0}" = "1" ]; then
  say "--- 5. T-B6 예비 물 생략(TB5_SKIP_WATER=1) ---"
else
  w=0; for t in azbIm050 azbIm100 bIm100; do [ -f "charged_v3/${t}_DDEC6.cif" ] && w=$((w+1)); done
  if [ "$w" -eq 3 ]; then
    say "--- 5. T-B6 예비 물 (RH 0.15/0.10/0.05 × azbIm050 azbIm100 bIm100) ---"
    t0=$(date +%s)
    WATER_TB6_WORKERS="${TB5_WATER_WORKERS:-5}" nice -n 10 "$CZ" -u run_water_lowrh_tb6.py >> "$L" 2>&1
    say "T-B6 예비 물 끝 (rc=$?, $(( ($(date +%s)-t0)/3600 )) 시간) -> v3_water_lowrh_tb6/water_results.json"
  else
    say "--- 5. T-B6 예비 물 건너뜀: 대상 3종 중 전하 CIF $w 종 ---"
  fi
fi

say "=================== T-B5 체인 끝 ==================="
say "보고: results_tb5.json, relax_v3_judged.json, (v3_water_lowrh_tb6/water_results.json)"
say "      tb5_report.py 출력이 위에 있습니다. 커밋 규칙 ASSIGN_20260903.md §4 ①."
