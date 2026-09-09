#!/bin/bash
# 무인 잇기 (PLAN_30H_20260908 §2, 랩탑) — 2026-09-08 11:2x
# ⚠️ 돌고 있는 이 스크립트를 편집하지 마십시오 (CLAUDE.md §6, 바이트 오프셋으로 읽습니다).
cd /home/skyjun/mof_project/21_ZIF69_MTV
PY=/home/skyjun/miniconda3/envs/czeromof/bin/python

# PID 재사용 함정을 피합니다 — kill -0 만 보면 남의 프로세스를 기다립니다.
wait_pid () {   # $1 = PID, $2 = 명령줄에 있어야 할 문자열
  while kill -0 "$1" 2>/dev/null; do
    ps -p "$1" -o args= 2>/dev/null | grep -q "$2" || break
    sleep 120
  done
}

# ① 사슬: 라운드 1(929943) 이 끝나면 --rounds 3 --no-local-stop (상한 4 는 도구가 유지)
(
  wait_pid 929943 extend_chain_v3w.py
  CHAIN_ROOT=water_runs_v3w_chunk nice -n 5 $PY -u extend_chain_v3w.py \
      --rounds 3 --no-local-stop --names base saIm050 >> extend_r2plus.log 2>&1
) &

# ② e6·e8(928643) 이 끝나면 힘장·씨앗 재기록.
#    ⚠️ 데스크탑 지시의 `run_water_v3w.py --stamp-only` 는 **틀립니다** — 그 러너의
#    TARGETS 는 saIm 11종이라 sa50nb50e* 를 안 찍습니다. 이 계열의 러너는 run_tmtv2w.py 입니다.
(
  wait_pid 928643 run_tmtv2w.py
  nice -n 5 $PY -u run_tmtv2w.py --stamp-only >> tmtv2w_stamp.log 2>&1
) &
wait
