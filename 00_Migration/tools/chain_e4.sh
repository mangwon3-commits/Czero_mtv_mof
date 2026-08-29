#!/bin/bash
# e5(h,i,j) 가 끝나 자리가 나면 e4 3회를 잇는다. 검정력 43% -> 59%.
# 가드: 자리 없으면 안 띄운다 / 한 번만 / 4시간 안에 안 나면 포기.
D=/home/mangwon/mof_project/21_ZIF69_MTV
LOCK=$D/.chain_e4.done
LOG=$D/chain_e4.log
log() { printf "%s %s\n" "$(date "+%F %T")" "$1" >> "$LOG"; }

[ -f "$LOCK" ] && { log "이미 실행됨 — 중단"; exit 0; }

export PATH=/home/mangwon/miniconda3/envs/czeromof/bin:$PATH
cd "$D" || exit 1
log "대기 시작 (simulate <=6 이 될 때까지, 최대 4시간)"

for i in $(seq 1 480); do
  n=$(pgrep -c -x simulate); n=${n:-0}
  if [ "$n" -le 6 ]; then
    free_gb=$(free -g | awk "NR==2{print \$7}")
    if [ "${free_gb:-0}" -lt 8 ]; then log "자리는 났으나 여유메모리 ${free_gb}GB — 대기"; sleep 30; continue; fi
    log "자리 남 (simulate ${n}개, 여유 ${free_gb}GB) — e4 3회 착수"
    : > "$LOCK"
    for T in q r s; do
      rm -rf water_runs_repro_$T v3_water_repro_$T
      { echo; echo "===== $(date "+%F %T") e4 반복 $T (자동 연결) ====="; } >> water_repro_$T.log
      REPRO_TAG=$T REPRO_ONLY=saIm0583e4 REPRO_WORKERS=1 \
        setsid nohup python -u run_water_repro.py >> water_repro_$T.log 2>&1 < /dev/null &
      sleep 8
    done
    sleep 30
    log "착수 완료 — simulate $(pgrep -c -x simulate)개"
    exit 0
  fi
  sleep 30
done
log "!! 4시간 안에 자리가 안 남 — 포기 (수동 확인 필요)"
