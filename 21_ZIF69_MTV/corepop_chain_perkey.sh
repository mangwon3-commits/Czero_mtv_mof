#!/bin/bash
# [구조별 판 · desktop 2026-11-16] corepop_chain_keys.sh(e5f65f5a)와 같은 순서 · 같은 관문. 다른 것은 본 계산을 띄우는 방식 하나뿐.
#   사용자 지시 11-16 15:0x "b09는 지금 나눠서 최대한 계산하자. 중간에 끊어도 중단한 지점까지는 보존할 수 있게 해줘"
#   까닭: 러너(run_znbdt_e_humid3.py)는 작업이 **전부** 끝난 뒤에야 결과 · 감사를 씁니다. 한 러너에 여러 구조를 넣으면
#   중간에 끊을 때 끝난 구조까지 잃습니다. 그래서 구조마다 러너를 하나씩(COREPOP_F_MACHINE=<기기>_sNN, 워커 1) 띄웁니다.
#   결과 파일이 구조마다 생기므로, 끊으면 그때 돌던 구조만 잃습니다. 러너 · Zeo++ 래퍼는 무수정입니다.
#   Zeo++ 는 원판대로 호출마다 저장됩니다. Zeo++ 단계에서 끊기면:
#     python corepop_subset_blocks.py subset <막음 파일>  → <이름>a.json(세 탐침 ok 구조만 · finished 붙음)
#     ZEO_BF=<그 a 파일> 로 이 사슬을 다시 띄우면 Zeo++ 를 건너뛰고 스모크 · 본 계산만 합니다.
# 사용: cp corepop_chain_perkey.sh ~/.mof_chain/ && setsid nohup bash ~/.mof_chain/corepop_chain_perkey.sh <기기> <키 파일> [<기다릴 PID>] < /dev/null > /dev/null 2>&1 &
#   <기다릴 PID>: 그 기기에서 도는 앞 사슬의 실제 bash PID(CLAUDE.md §4). env MAXPAR(동시 러너 상한 · 기본 nproc) · STAG(띄우는 간격 초 · 기본 30).
# 순서: (앞 사슬 끝) → simulate 0 · network 0 → Zeo++ 막음(병렬 1) → 세 탐침 ok 구조만 → 스모크(최대 2종) → 구조마다 러너. 값 읽기 · 판정 없음.
# 끊기: 이 사슬 bash PID → 러너 파이썬 PID → simulate PID 순으로 PID 로(CLAUDE.md §4). PID 는 <로그>.pids 에 적힘.
set -u
M=$1; KF=$2; WP=${3:-}
REPO=${REPO:-$HOME/mof_project}
D=$REPO/21_ZIF69_MTV
PY=${PY:-$HOME/miniconda3/envs/czeromof/bin/python}
MAXPAR=${MAXPAR:-$(nproc)}; STAG=${STAG:-30}
L=$HOME/.mof_chain/corepop_${M}_perkey
say() { echo "$(date '+%F %T') $*" >> "$L.chain.log"; }
say "시작 기기 $M 키 파일 $KF 기다릴 PID ${WP:-없음} · ZEO_BF ${ZEO_BF:-없음} · MAXPAR $MAXPAR · STAG $STAG · PY $PY · 사슬 PID $$"
echo "chain $$" >> "$L.pids"
if [ -n "$WP" ]; then
  while kill -0 "$WP" 2>/dev/null; do sleep 60; done
  say "앞 사슬 PID $WP 끝"
fi
while [ "$(pgrep -xc network)" != "0" ] || [ "$(pgrep -xc simulate)" != "0" ]; do sleep 60; done
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
if [ -n "${ZEO_BF:-}" ]; then
  BF=$ZEO_BF
  say "Zeo++ 건너뜀 — 막음 파일 $BF"
else
  say "network 0 · simulate 0 — Zeo++ 착수(병렬 1)"
  COREPOP_MACHINE=$M COREPOP_KEYS_FILE=$KF COREPOP_ZEO_PAR=1 nice -n 5 "$PY" -u corepop_blocks_keys.py > "$L.zeo.log" 2>&1; rc=$?
  BF=results_corepop_blocks_${M}_${BATS//,/_}_heavy.json
  say "Zeo++ 끝 rc=$rc · $(tail -1 "$L.zeo.log")"
fi
grep -q '"finished"' "$BF" 2>/dev/null || { say "막음 완주 파일 없음($BF) — 멈춤"; exit 3; }
export BF
OKKEYS=$("$PY" - <<'PYEOF'
import json, os
d = json.load(open(os.environ['BF'], encoding='utf-8'))
ok = [r['key'] for r in d['rows'] if all(r.get(f'r{x}', {}).get('block_ok') is True and r.get(f'r{x}', {}).get('n_spheres') is not None for x in ('1.65', '1.82', '1.30'))]
print(','.join(ok))
PYEOF
)
IFS=, read -r -a OKA <<< "$OKKEYS"
NOK=${#OKA[@]}
say "막음 ok 구조 $NOK"
[ "$NOK" -gt 0 ] || { say "막음 ok 구조 0 — 멈춤"; exit 4; }
SK=$(echo "$OKKEYS" | cut -d, -f1-2)
WANT=$(( NOK < 2 ? NOK : 2 ))
rm -rf "$HOME/.mof_chain/corepop_e3_323_smoke_$M"
COREPOP_F_MACHINE=$M COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$SK" COREPOP_F_BLOCKS=$BF COREPOP_F_SMOKE=1 "$PY" -u run_corepop_e_humid3_323.py > "$L.smoke.log" 2>&1; rc=$?
SOK=$(grep -o '"n_ok": [0-9]*' "$L.smoke.log" | tail -1 | grep -o '[0-9]*$')
say "스모크 rc=$rc n_ok=$SOK (기대 $WANT)"
[ "$SOK" = "$WANT" ] || { say "스모크 실패 — 멈춤"; exit 5; }
declare -A PIDT
alive() { local n=0 p; for p in "${!PIDT[@]}"; do kill -0 "$p" 2>/dev/null && n=$((n+1)); done; echo "$n"; }
i=0
for k in "${OKA[@]}"; do
  while [ "$(alive)" -ge "$MAXPAR" ]; do sleep 30; done
  i=$((i+1)); T=$(printf '%s_s%02d' "$M" "$i")
  COREPOP_F_MACHINE=$T COREPOP_F_BATCHES=$BATS COREPOP_F_KEYS="$k" COREPOP_F_BLOCKS=$BF COREPOP_F_WORKERS=1 "$PY" -u run_corepop_e_humid3_323.py > "$L.gcmc_$T.log" 2>&1 &
  p=$!; PIDT[$p]=$T
  echo "runner $p $T $k" >> "$L.pids"
  say "본 계산 띄움 $T $k PID $p"
  sleep "$STAG"
done
while [ "${#PIDT[@]}" -gt 0 ]; do
  for p in "${!PIDT[@]}"; do
    if ! kill -0 "$p" 2>/dev/null; then
      wait "$p"; rc=$?; T=${PIDT[$p]}
      say "본 계산 끝 $T rc=$rc · $(grep -o '감사 .*' "$L.gcmc_$T.log" | tail -1)"
      unset "PIDT[$p]"
    fi
  done
  sleep 60
done
say "사슬 끝 · 구조 $NOK 종"
