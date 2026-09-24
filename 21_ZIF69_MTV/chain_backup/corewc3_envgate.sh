#!/usr/bin/env bash
# §AW-2 메움 — 환경 선행 관문. **성공하면 RASPA_DIR 을 stdout 으로, 실패하면 rc≠0.**
#
# [왜]  러너에 환경 검사가 없습니다 — `run_aryl_gcmc` 는 `simulate` 를 그냥 부릅니다.
#   2026-09-23 10:39 에 데스크탑이 `RASPA_DIR` 을 한 단계 깊게 줘서 172종을 **3분 만에 전멸**시켰고,
#   큐는 비었는데 값은 0 이었습니다. 메움은 18 h 뒤에 깨므로 그 사이 환경이 바뀔 수 있습니다.
#
# [★ 오탐이 정탐보다 비쌉니다]  랩탑 11:4x 실측 — 관문을 넣자마자 `command -v simulate` 가
#   "없음" 을 냈는데 **그 순간 simulate 8개가 돌고 있었습니다**(그 셸 PATH 에 conda 가 없었음).
#   멀쩡한데 막으면 **아무도 메우지 않습니다.** 그래서 이 관문은 막기 전에 **스스로 고칩니다**:
#   경로를 추측하지 않고 **러너 자신에게 묻고**, 힘장이 안 잡히면 **찾아서 RASPA_DIR 을 다시 세웁니다.**
#   그래도 안 되면 그때만 물러나고, 그 경우는 데스크탑 보조 지표(값 칸 6 h)가 덮습니다.
set -u
CZ=$HOME/miniconda3/envs/czeromof/bin/python3
R=/home/mangwon1/mof_project/21_ZIF69_MTV
err(){ echo "관문: $*" >&2; }

# ① simulate — 추측하지 말고 러너에게 묻는다
SIM=$(cd "$R" && "$CZ" -c "import run_aryl_gcmc as rg; print(rg.SIMULATE)" 2>/dev/null)
[ -n "${SIM:-}" ] && [ -x "$SIM" ] || { err "simulate 를 못 찾음 ('${SIM:-}')"; exit 5; }

# ② 힘장 — 주어진 RASPA_DIR 로 잡히나? 안 잡히면 찾아서 다시 세운다(오탐 방지)
want=share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
cand="${RASPA_DIR:-$HOME/RASPA/simulations}"
if [ ! -f "$cand/$want" ]; then
  err "RASPA_DIR='$cand' 로 힘장이 안 잡힘 — 찾아서 다시 세웁니다"
  found=$(find "$HOME" -maxdepth 8 -path "*/$want" -print -quit 2>/dev/null)
  [ -n "$found" ] || { err "UFF_MOF 를 어디서도 못 찾음"; exit 5; }
  cand=${found%/$want}
  err "다시 세움: RASPA_DIR='$cand'"
fi

# ③ 고정값이 규약대로인가 (CLAUDE.md §1) — García-Sánchez 2009 CO₂
m="$cand/$want"
grep -qE '^\s*C_co2\s+lennard-jones\s+29\.933\s+2\.745' "$m" || { err "CO₂ LJ 가 규약값이 아님"; exit 5; }
grep -qE '^\s*Hw\s+none'  "$m" || { err "물 Hw none 아님"; exit 5; }
grep -qE '^\s*Lw\s+none'  "$m" || { err "물 Lw none 아님"; exit 5; }
grep -qE '^\s*C_co2\s+yes\s+C\s+C\s+0\s+12\.0\s+0\.6512' "$cand/share/raspa/forcefield/UFF_MOF/pseudo_atoms.def" \
  || { err "q_C 가 +0.6512 아님"; exit 5; }
[ -f "$cand/share/raspa/molecules/TraPPE/CO2.def" ] || { err "CO2.def 경로 없음"; exit 5; }

echo "$cand"
