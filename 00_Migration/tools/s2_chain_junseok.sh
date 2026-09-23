#!/bin/bash
# s2_chain_junseok.sh — ASSIGN_20260903.md §2 (nbIm025 RH0 x4) + 선행 e1 확인 1회. 동시성 1, 순차.
#
# 등록(수 보기 전, COMMS/junseok.md 2026-09-24 08:3x 항목):
#   e1 확인  새 1회(e1ff)가 옛 n=8 의 95% 예측구간 [1.163620, 1.205875] 안이면 §2 착수, 밖이면 멈춤.
#            (평균 1.184747 · R̂ 0.008424 · t(0.975,7)=2.36462 · sqrt(1+1/8))
#   §2 판정  ASSIGN_20260903 §2-3 그대로 — F = s²(nbIm025, dof 3)/0.008424² · 임계 0.068 / 5.89.
#            판정은 세션이 등록식으로 합니다. 이 스크립트는 돌리기만 합니다.
#
# 지키는 것:
#   - 러너·설정 변경 금지(§2-2): 매 회차 전 run_water.py + run_water_repro.py 의 md5 를 착수 시점과
#     대조하고, 바뀌었으면 멈춥니다. postman 이 회차 사이 틈에 master 를 합칠 수 있어서입니다.
#   - 완주는 **값이 아니라 표지로**(CLAUDE.md §0, 09-21): .data 에 'Simulation finished' 가 있어야 셉니다.
#   - 이 스크립트는 **저장소 밖 사본**(~/.junseok_chain/)에서 돕니다 — 도는 bash 를 git 이 덮지 않게(§6).
#     저장소의 00_Migration/tools/s2_chain_junseok.sh 는 기록용 원본입니다.
set -u
G=/home/mangwon/mof_project
D=$G/21_ZIF69_MTV
CZ=/home/mangwon/miniconda3/envs/czeromof/bin
export PATH=$CZ:$PATH
LOG=$D/s2_chain_junseok.log
FF=$HOME/RASPA/simulations/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
PI_LO=1.163620
PI_HI=1.205875
V=""

say(){ printf '%s %s\n' "$(date '+%F %T')" "$1" >> "$LOG"; }
sum_runner(){ (cd "$D" && md5sum run_water.py run_water_repro.py | md5sum | cut -c1-32); }

cd "$D" || exit 1
SUM0=$(sum_runner)
say "사슬 시작 · 러너 md5 $SUM0 · 힘장 md5 $(md5sum "$FF" | cut -c1-8) · PID $$"

run(){   # $1 태그  $2 대상 — 결과 로딩은 전역 V 로
  local tag=$1 tgt=$2 now f
  V=""
  now=$(sum_runner)
  if [ "$now" != "$SUM0" ]; then
    say "!! 러너가 사슬 도중 바뀜 ($SUM0 -> $now) — 멈춤 (§2-2 러너·설정 변경 금지)"; exit 2
  fi
  if [ -e "v3_water_repro_$tag" ] || [ -e "water_runs_repro_$tag" ]; then
    say "!! 태그 $tag 폴더가 이미 있음 — 멈춤 (덮어쓰기 방지)"; exit 2
  fi
  bash "$G/00_Migration/tools/mail_guard_junseok.sh"
  say "착수 $tag $tgt"
  { echo; echo "===== $(date '+%F %T') $tag $tgt (ASSIGN_20260903 §2, 동시성 1) ====="; } >> "water_repro_$tag.log"
  REPRO_TAG=$tag REPRO_ONLY=$tgt REPRO_WORKERS=1 "$CZ/python" -u run_water_repro.py \
      >> "water_repro_$tag.log" 2>&1 < /dev/null
  f=$(ls water_runs_repro_"$tag"/*/Output/System_0/*.data 2>/dev/null | head -1)
  if [ -z "$f" ] || ! grep -q "Simulation finished" "$f"; then
    say "!! $tag 완주 표지 없음 — 멈춤 (값이 아니라 표지가 자, CLAUDE.md §0)"; exit 3
  fi
  V=$("$CZ/python" -c "import json;r=json.load(open('v3_water_repro_$tag/water_results.json'));print(r[0]['CO2_molkg'])" 2>/dev/null)
  if [ -z "$V" ]; then say "!! $tag 결과 JSON 없음 — 멈춤"; exit 3; fi
  say "완주 $tag $tgt CO2 $V"
}

run e1ff saIm0583e1
if "$CZ/python" -c "import sys; v=float('$V'); sys.exit(0 if $PI_LO <= v <= $PI_HI else 1)"; then
  say "e1 확인 통과: $V 는 [$PI_LO, $PI_HI] 안 — §2 착수"
else
  say "!! e1 확인 실패: $V 는 [$PI_LO, $PI_HI] 밖 — 대조군 R̂ 전제가 흔들림. §2 착수 안 함, 종합자 판단 대기"
  exit 4
fi

for i in 1 2 3 4; do run "nb$i" nbIm025; done
say "§2 4회 완주 — 판정은 세션이 등록식(F, 임계 0.068 / 5.89)으로"
