#!/bin/bash
# COREPOP-H323 한 묶음 사슬 (ASSIGN_COREPOP_HUMID323_20261114.md). 저장소 밖으로 복사해서 띄움(CLAUDE.md §9):
#   cp corepop_chain.sh ~/.mof_chain/ && setsid nohup bash ~/.mof_chain/corepop_chain.sh <기기> <묶음> <Zeo++ 병렬> <워커> < /dev/null > /dev/null 2>&1 &
# 순서: simulate 0 기다림 → Zeo++ 막음(corepop_blocks.py) → 막음 ok 구조만 → 스모크(10 사이클 · 2종) → 본 계산(run_corepop_e_humid3_323.py)
# 어느 단계든 실패하면 그 자리에서 멈추고 ~/.mof_chain/corepop_<기기>_<묶음>.chain.log 에 적음. 값 읽기 · 판정 없음.
set -u
M=$1; B=$2; PAR=$3; W=$4
REPO=${REPO:-$HOME/mof_project}
D=$REPO/21_ZIF69_MTV
PY=${PY:-$HOME/miniconda3/envs/czeromof/bin/python}
L=$HOME/.mof_chain/corepop_${M}_${B}
say() { echo "$(date '+%F %T') $*" >> "$L.chain.log"; }
say "시작 기기 $M 묶음 $B Zeo++ 병렬 $PAR 워커 $W · PY $PY"
while [ "$(pgrep -xc simulate)" != "0" ]; do sleep 60; done
say "simulate 0 — Zeo++ 착수"
cd "$D" || { say "저장소 없음 $D"; exit 2; }
COREPOP_MACHINE=$M COREPOP_BATCHES=$B COREPOP_ZEO_PAR=$PAR nice -n 5 "$PY" -u corepop_blocks.py > "$L.zeo.log" 2>&1; rc=$?
BF=results_corepop_blocks_${M}_${B}.json
say "Zeo++ 끝 rc=$rc · $(tail -1 "$L.zeo.log")"
grep -q '"finished"' "$BF" 2>/dev/null || { say "막음 완주 파일 없음 — 멈춤"; exit 3; }
export BF B
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
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$B COREPOP_F_KEYS="$SK" COREPOP_F_BLOCKS=$BF COREPOP_F_SMOKE=1 "$PY" -u run_corepop_e_humid3_323.py > "$L.smoke.log" 2>&1; rc=$?
SOK=$(grep -o '"n_ok": [0-9]*' "$L.smoke.log" | tail -1 | grep -o '[0-9]*$')
say "스모크 rc=$rc n_ok=$SOK (기대 2)"
[ "$SOK" = "2" ] || { say "스모크 실패 — 멈춤"; exit 5; }
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$B COREPOP_F_KEYS="$OKKEYS" COREPOP_F_BLOCKS=$BF COREPOP_F_WORKERS=$W "$PY" -u run_corepop_e_humid3_323.py > "$L.gcmc.log" 2>&1; rc=$?
say "본 계산 끝 rc=$rc · $(grep -o '감사 .*' "$L.gcmc.log" | tail -1)"
