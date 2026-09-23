#!/usr/bin/env bash
# §AW-2 데스크탑 **메움 사슬** — 172종이 끝난 뒤, 452종 중 **아무도 안 한 것**을 뒤늦게 메웁니다.
#
# [왜 고정 배정이 아니라 메움인가]  laptop2 가 109종 전량을 직접 돕니다. 고정 배정이면 제 완주가
#   더 이를 때 laptop2 의 **아직 도는 꼬리**를 못 걸러 정면으로 같이 돕니다(laptop2 지적).
#   그렇다고 끊으면 "죽으면 그때 다시 걸면 된다" 가 **또 사람**입니다(09-22 의 13시간).
#   그래서 늦게 깨어 남은 것만 집습니다. 목표는 `core_wc_pick2.json` **452종 전체**라
#   어느 기기가 죽든 그 몫이 자동으로 남은 집합에 들어옵니다.
#
# [★ 살아 있음은 **칸**으로 잽니다 — 남은 종 수로도, 손댄 **종** 수로도 재면 안 됩니다]  laptop2 11:2x.
#   `run_core_wc.py:104` 의 **바깥 루프가 압력**이라 0.15 bar 단계(작업합의 ~70 %, ~11.6 h) 내내
#   "두 압력 다 끝난 종" 은 **0 에서 안 움직입니다.** 기기가 꽉 차 도는데 "아무도 안 돈다" 로 읽힙니다.
#   `run_status` 는 작업마다·실패해도 채워지므로 두 단계 모두에서 단조 증가합니다.
#
# [저장소 밖·절대경로]  postman 의 repo_bash_running 가드에 안 걸리게(결함 (14)).
# [대조는 git show]  작업트리를 안 건드려 러너가 돌아도 안전하고 postman 5분 틱과 경주하지 않습니다.
set -u
R=/home/mangwon1/mof_project/21_ZIF69_MTV
G=/home/mangwon1/mof_project
LOG=$G/.claude_work_corewc3_desk.out
DRV=2012109                       # 앞 드라이버. PID 로만 봅니다 — pkill -f 금지(CLAUDE.md §4)
PY=$HOME/miniconda3/envs/czeromof/bin/python3
T1=$(date -d '2026-09-24 10:00' +%s)    # ① 이 시각 이후라야 착수
T2=$(date -d '2026-09-25 12:00' +%s)    # 최후 보루 — ②를 무시하고 착수
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

say "메움 사슬(생존=run_status 칸) 시작 — 앞 드라이버 PID $DRV 대기"
while kill -0 "$DRV" 2>/dev/null; do sleep 120; done
say "앞 드라이버 종료 확인"
q=0; while [ "$q" -lt 3 ]; do if [ "$(pgrep -xc simulate)" = "0" ]; then q=$((q+1)); else q=0; fi; sleep 60; done
say "simulate 정지 3분 확인"

# ───────────────────────────────────────────────────────────────────────────
# [밀도맵 빈칸 메움 — 2026-09-23 사용자 지시 "넣어"]  메움 감시보다 **먼저** 돕니다.
#   왜 직렬인가: 둘 다 8코어를 쓰므로 겹치면 서로 느려집니다(CLAUDE.md §5). 그리고
#   밀도맵이 도는 동안은 simulate 가 살아 있어, 아래 메움 감시의 "안정" 판정이
#   **잘못 발동하지 않습니다** — 순서 자체가 가드입니다.
#   실패해도 **메움은 그대로 진행**합니다(|| true). 밀도맵은 그림 근거이지 판정이 아닙니다.
DLOG=$G/.claude_work_density_gap.out
say "밀도맵 빈칸 메움 착수 — 건조(saIm0583·mslm050 × 전하 ON/OFF, 6워커) + 습윤 RH90 2건"
( cd "$R" && export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH" RASPA_DIR="$HOME/RASPA/simulations" \
    DENSITY_GAP_WORKERS=6
  echo "=== $(date '+%m-%d %H:%M:%S') 건조 밀도맵 착수 ===" >> "$DLOG"
  python3 run_density_v3_gap.py >> "$DLOG" 2>&1
  echo "=== $(date '+%m-%d %H:%M:%S') 건조 끝 rc=$? ===" >> "$DLOG" ) &
DP1=$!
for t in saIm0583 mslm050; do
  ( cd "$R" && export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH" RASPA_DIR="$HOME/RASPA/simulations" \
      DW_EXTRA=saIm0583,mslm050 DW_SUB="gap_$t"
    echo "=== $(date '+%m-%d %H:%M:%S') 습윤 RH90 $t 착수 ===" >> "$DLOG"
    python3 run_density_water_v3w.py "$t" >> "$DLOG" 2>&1
    echo "=== $(date '+%m-%d %H:%M:%S') 습윤 $t 끝 rc=$? ===" >> "$DLOG" ) &
done
wait $DP1 || true
wait || true
say "밀도맵 빈칸 메움 종료 — 로그 $DLOG"

# 밀도맵이 끝난 뒤 계산이 실제로 멎었는지 다시 확인하고 메움 감시로 넘어갑니다.
q=0; while [ "$q" -lt 3 ]; do if [ "$(pgrep -xc simulate)" = "0" ]; then q=$((q+1)); else q=0; fi; sleep 60; done
say "simulate 재정지 확인 — 메움 감시 시작"
# ───────────────────────────────────────────────────────────────────────────

# 생존 문턱 둘 — 랩탑 11:3x 의 정리대로 두 지표는 **전량 실패 중인 기기**에서 갈립니다.
#   주  `run_status` 칸이 **3 h** 안 늘면 죽음   (실패해도 오르므로 **중복을 덜 냅니다**)
#   보조 `값` 칸이 **6 h** 안 늘면 죽음          (주 지표만 두면 **남이 전량 실패에 빠졌을 때
#        run_status 만 계속 올라 아무도 안 메웁니다** — 10:39 에 제가 172종을 3분 만에
#        전부 `[no-output]` 낸 그 상태. 랩탑 지표가 덮지만 그쪽이 같이 죽으면 남는 자리입니다.)
prevc=-1; prevv=-1; sc=0; sv=0; n=0
while :; do
  git -C "$G" fetch -q --all 2>/dev/null
  out=$("$PY" "$HOME/.mof_chain/corewc3_missing.py" 2>>"$LOG" | tail -1)
  n=$(echo "$out" | awk '{print $1}'); cells=$(echo "$out" | awk '{print $2}'); vals=$(echo "$out" | awk '{print $3}')
  case "${n:-x}${cells:-x}${vals:-x}" in *[!0-9]*) say "지표 계산 실패 ('$out') — 15분 뒤 다시"; sleep 900; continue;; esac
  [ "$cells" = "$prevc" ] && sc=$((sc+1)) || sc=0; prevc=$cells
  [ "$vals"  = "$prevv" ] && sv=$((sv+1)) || sv=0; prevv=$vals
  say "남은 ${n}종 · run_status ${cells}(정지 ${sc}/12) · 값 ${vals}(정지 ${sv}/24)"
  [ "$n" = "0" ] && { say "남은 것 0 — 조용히 종료"; exit 0; }
  now=$(date +%s)
  if { [ "$now" -ge "$T1" ] && { [ "$sc" -ge 12 ] || [ "$sv" -ge 24 ]; }; } || [ "$now" -ge "$T2" ]; then break; fi
  sleep 900
done

# 환경 선행 관문 (랩탑 11:4x 제안). **막기 전에 스스로 고칩니다** — 이 자리에서는
# 오탐이 정탐보다 비쌉니다(멀쩡한데 막으면 아무도 메우지 않음). 양방향 시험 완료:
#   올바른 env → 통과 · 10:39 의 틀린 RASPA_DIR → 자가 교정 · 힘장 값 위반 셋 → rc=5 로 막음
say "환경 관문 시작"
GD=$(RASPA_DIR="$HOME/RASPA/simulations" bash "$HOME/.mof_chain/corewc3_envgate.sh" 2>>"$LOG")
if [ -z "${GD:-}" ]; then
  say "!! 환경 관문 실패 — **착수하지 않습니다.** 망가진 env 로 돌면 큐만 비고 값은 0 입니다."
  say "   이 경우 랩탑의 값-칸 지표가 제 정지를 보고 덮습니다."
  exit 5
fi
say "환경 관문 통과 — RASPA_DIR=$GD"

say "메움 착수 ${n}종 (run_status ${prevc} 정지 ${sc}/12 · 값 ${prevv} 정지 ${sv}/24)"
export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH" RASPA_DIR="$GD"
cd "$R" || exit 1
export COREWC_ASSIGN=desktop COREWC_MACHINE=desktop COREWC_WORKERS=8
export COREWC_PICK="$R/core_wc_pick3_desktop_run.json"
export COREWC_OUT="$R/core_wc_results_ext2_desktop.json"
python3 run_core_wc.py >> "$LOG" 2>&1
say "메움 종료"
