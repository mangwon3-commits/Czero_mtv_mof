#!/bin/bash
# [다음 묶음 겹침 판 · 랩탑 2026-11-16] 사용자 결정 11-16 01:1x "바로 시작해" — 앞 사슬의 GCMC 가 도는 동안 다음 묶음의 Zeo++ 를 같이 돌림(CLAUDE.md §5 를 이 묶음에서 풂).
# corepop_chain_keys_overlap.sh(0667627a)에서 다른 곳:
#   · 기록 이름에 꼬리표(일곱째 인자)를 씀 — 앞 사슬의 corepop_<기기>_heavy.* 기록을 덮지 않으려는 것.
#   · Zeo++ 는 앞 사슬의 Zeo++ 래퍼 PID(다섯째 인자)가 끝나고 network 0 이 된 뒤에 띄움 — Zeo++ 둘이 겹치지 않음. simulate 는 ALLOW_SIM(기본 16) 이하이면 같이 돎.
#   · 래퍼는 corepop_blocks_keys_overlap2.py(부피 작은 순 · 재시도는 simulate 0 뒤). nice 를 붙이지 않음(simulate 16개와 같은 몫으로 돌게 함).
#   · 스모크 · 본 계산은 앞 사슬 PID(여섯째 인자)가 끝나고 simulate 0 · network 0 이 된 뒤에 띄움 — GCMC 둘이 겹치지 않음. 그 두 줄 자체는 그대로.
#   cp corepop_chain_keys_next.sh ~/.mof_chain/ && setsid nohup bash ~/.mof_chain/corepop_chain_keys_next.sh <기기> <키 파일> <Zeo++ 병렬> <워커> <앞 Zeo++ 래퍼 PID> <앞 사슬 PID> <꼬리표> < /dev/null > /dev/null 2>&1 &
# 순서: (앞 사슬의 Zeo++ 끝) → network 0 → Zeo++ 막음(GCMC 와 같이) → 세 탐침 ok 구조만 → (앞 사슬 끝 · simulate 0 · network 0) → 스모크 2종 → 본 계산. 값 읽기 · 판정 없음.
set -u
[ $# -eq 7 ] || { echo "인자 7개: <기기> <키 파일> <Zeo++ 병렬> <워커> <앞 Zeo++ 래퍼 PID> <앞 사슬 PID> <꼬리표>"; exit 2; }
M=$1; KF=$2; PAR=$3; W=$4; WZ=$5; WC=$6; TAG=$7; ALLOW=${ALLOW_SIM:-16}
case "$TAG" in *[!a-z0-9_]*|''|heavy) echo "!! 꼬리표는 소문자 · 숫자 · _ 만, heavy 는 안 됨: $TAG"; exit 2;; esac
REPO=${REPO:-$HOME/mof_project}
D=$REPO/21_ZIF69_MTV
PY=${PY:-$HOME/miniconda3/envs/czeromof/bin/python}
L=$HOME/.mof_chain/corepop_${M}_${TAG}
[ -e "$L.chain.log" ] && { echo "!! $L.chain.log 가 이미 있음 — 다른 꼬리표를 쓰세요"; exit 2; }
say() { echo "$(date '+%F %T') $*" >> "$L.chain.log"; }
say "시작 기기 $M 키 파일 $KF Zeo++ 병렬 $PAR 워커 $W 앞 Zeo++ 래퍼 PID $WZ 앞 사슬 PID $WC 꼬리표 $TAG · PY $PY"
while kill -0 "$WZ" 2>/dev/null; do sleep 60; done
say "앞 사슬의 Zeo++ 래퍼 PID $WZ 끝"
while [ "$(pgrep -xc network)" != "0" ]; do sleep 60; done
say "network 0 · simulate $(pgrep -xc simulate) — Zeo++ 착수(simulate ≤ $ALLOW 이면 같이 돎 · 사용자 결정 11-16 01:1x)"
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
COREPOP_MACHINE=$M COREPOP_KEYS_FILE=$KF COREPOP_ZEO_PAR=$PAR COREPOP_ZEO_ALLOW_SIM=$ALLOW "$PY" -u corepop_blocks_keys_overlap2.py > "$L.zeo.log" 2>&1; rc=$?
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
while kill -0 "$WC" 2>/dev/null; do sleep 60; done
say "앞 사슬 PID $WC 끝"
while [ "$(pgrep -xc simulate)" != "0" ] || [ "$(pgrep -xc network)" != "0" ]; do sleep 60; done
say "simulate 0 · network 0 — 스모크 착수"
SK=$(echo "$OKKEYS" | cut -d, -f1-2)
rm -rf "$HOME/.mof_chain/corepop_e3_323_smoke_$M"
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$SK" COREPOP_F_BLOCKS=$BF COREPOP_F_SMOKE=1 "$PY" -u run_corepop_e_humid3_323.py > "$L.smoke.log" 2>&1; rc=$?
SOK=$(grep -o '"n_ok": [0-9]*' "$L.smoke.log" | tail -1 | grep -o '[0-9]*$')
say "스모크 rc=$rc n_ok=$SOK (기대 2)"
[ "$SOK" = "2" ] || { say "스모크 실패 — 멈춤"; exit 5; }
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$OKKEYS" COREPOP_F_BLOCKS=$BF COREPOP_F_WORKERS=$W "$PY" -u run_corepop_e_humid3_323.py > "$L.gcmc.log" 2>&1; rc=$?
say "본 계산 끝 rc=$rc · $(grep -o '감사 .*' "$L.gcmc.log" | tail -1)"
