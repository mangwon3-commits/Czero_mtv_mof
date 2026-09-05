#!/bin/bash
# B 드라이버(PID 인자)가 끝나면 확장 7종 + CO2 대조를 띄운다.
# 패턴이 아니라 PID 로 기다린다 (CLAUDE.md §4: pkill/pgrep -f 함정).
PY=/home/mangwon1/miniconda3/envs/czeromof/bin/python
WAIT_PID="$1"
cd /home/mangwon1/mof_project/21_ZIF69_MTV || exit 1
echo "[chain] B 드라이버 PID $WAIT_PID 종료 대기 시작 $(date '+%F %T')"
while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 60; done
echo "[chain] B 종료 감지 $(date '+%F %T') — 확장 착수"
TB2_WORKERS=8 exec "$PY" run_tb2_ext.py
