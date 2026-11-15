#!/bin/bash
# [겹침 판 · 랩탑 2026-11-15] corepop_chain_keys.sh(e5f65f5a)에서 두 곳만 다름: Zeo++ 를 simulate 0 이 아니라 simulate ≤ ALLOW_SIM(기본 1)에서 띄움(래퍼 corepop_blocks_keys_overlap.py).
#   사용자 결정 11-15 23:2x "같이 돌려. 시간이 없다" — b05 의 마지막 GCMC 한 작업이 도는 동안 무거운 구조의 Zeo++ 를 돌림. 스모크 · 본 계산 줄은 그대로.
# COREPOP-H323 무거운 구조 사슬(사용자 지시 2026-11-15 "랩탑으로 넘겨"). corepop_chain.sh(ec27c8b3)와 같은 순서 · 같은 관문 — 대상만 키 파일.
#   cp corepop_chain_keys.sh ~/.mof_chain/ && setsid nohup bash ~/.mof_chain/corepop_chain_keys.sh <기기> <키 파일> <Zeo++ 병렬> <워커> [<기다릴 PID>] < /dev/null > /dev/null 2>&1 &
# <기다릴 PID>: 그 기기에서 도는 앞 사슬의 bash PID(ps -eo pid,args 로 찾은 실제 PID · CLAUDE.md §4). 앞 사슬의 Zeo++ 끝과 GCMC 시작 사이
#   simulate 0 틈에 이 사슬의 Zeo++ 가 끼어들면 RASPA 와 겹칩니다(CLAUDE.md §5). 그래서 그 PID 가 끝난 뒤에 simulate 0 · network 0 을 봅니다.
# 순서: (앞 사슬 끝) → simulate 0 · network 0 → Zeo++ 막음(corepop_blocks_keys.py) → 세 탐침 ok 구조만 → 스모크 2종 → 본 계산. 값 읽기 · 판정 없음.
set -u
M=$1; KF=$2; PAR=$3; W=$4; WP=${5:-}; ALLOW=${ALLOW_SIM:-1}
REPO=${REPO:-$HOME/mof_project}
D=$REPO/21_ZIF69_MTV
PY=${PY:-$HOME/miniconda3/envs/czeromof/bin/python}
L=$HOME/.mof_chain/corepop_${M}_heavy
say() { echo "$(date '+%F %T') $*" >> "$L.chain.log"; }
say "시작 기기 $M 키 파일 $KF Zeo++ 병렬 $PAR 워커 $W 기다릴 PID ${WP:-없음} · PY $PY"
if [ -n "$WP" ]; then
  while kill -0 "$WP" 2>/dev/null; do sleep 60; done
  say "앞 사슬 PID $WP 끝"
fi
while [ "$(pgrep -xc network)" != "0" ]; do sleep 60; done
say "network 0 · simulate $(pgrep -xc simulate) — Zeo++ 착수(simulate ≤ $ALLOW 이면 같이 돎 · 사용자 결정 11-15 23:2x)"
cd "$D" || { say "저장소 없음 $D"; exit 2; }
export KF
BATS=$("$PY" - <<'PYEOF'
import json, os
t = {r['key']: r['batch'] for r in json.load(open('corepop_humid323_targets.json', encoding='utf-8'))['rows']}
k = json.load(open(os.environ['KF'], encoding='utf-8'))['keys']
print(','.join(sorted({t[x] for x in k})))
PYEOF
)
[ -n "$BATS" ] || { say "키 파일에서 묶음을 못 읽음 — 멈춤"; exit 2; }
COREPOP_MACHINE=$M COREPOP_KEYS_FILE=$KF COREPOP_ZEO_PAR=$PAR COREPOP_ZEO_ALLOW_SIM=$ALLOW nice -n 5 "$PY" -u corepop_blocks_keys_overlap.py > "$L.zeo.log" 2>&1; rc=$?
BF=results_corepop_blocks_${M}_${BATS//,/_}_heavy.json
say "Zeo++ 끝 rc=$rc · $(tail -1 "$L.zeo.log")"
grep -q '"finished"' "$BF" 2>/dev/null || { say "막음 완주 파일 없음($BF) — 멈춤"; exit 3; }
export BF
OKKEYS=$("$PY" - <<'PYEOF'
import json, os
d = json.load(open(os.environ['BF'], encoding='utf-8'))
ok = [r['key'] for r in d['rows'] if all(r.get(f'r{x}', {}).get('block_ok') is True and r.get(f'r{x}', {}).get('n_spheres') is not None for x in ('1.65', '1.82', '1.30'))]
print(','.join(ok))
PYEOF
)
NOK=$(echo "$OKKEYS" | tr ',' '\n' | grep -c .)
say "막음 ok 구조 $NOK"
[ "$NOK" -gt 0 ] || { say "막음 ok 구조 0 — 멈춤"; exit 4; }
SK=$(echo "$OKKEYS" | cut -d, -f1-2)
rm -rf "$HOME/.mof_chain/corepop_e3_323_smoke_$M"
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$SK" COREPOP_F_BLOCKS=$BF COREPOP_F_SMOKE=1 "$PY" -u run_corepop_e_humid3_323.py > "$L.smoke.log" 2>&1; rc=$?
SOK=$(grep -o '"n_ok": [0-9]*' "$L.smoke.log" | tail -1 | grep -o '[0-9]*$')
say "스모크 rc=$rc n_ok=$SOK (기대 2)"
[ "$SOK" = "2" ] || { say "스모크 실패 — 멈춤"; exit 5; }
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$OKKEYS" COREPOP_F_BLOCKS=$BF COREPOP_F_WORKERS=$W "$PY" -u run_corepop_e_humid3_323.py > "$L.gcmc.log" 2>&1; rc=$?
say "본 계산 끝 rc=$rc · $(grep -o '감사 .*' "$L.gcmc.log" | tail -1)"
