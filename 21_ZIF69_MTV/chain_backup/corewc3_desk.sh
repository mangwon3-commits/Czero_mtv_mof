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
MACH=desktop
T1=$(date -d '2026-09-24 10:00' +%s)    # ① 이 시각 이후라야 착수
T2=$(date -d '2026-09-25 12:00' +%s)    # 최후 보루 — ②를 무시하고 착수
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

# [postman 되살리기 — 2026-09-23 laptop2 지적]
#   laptop2 의 WSL 이 11:05 에 재부팅되면서 postman 이 같이 죽었고 **되살리는 것이 없어**
#   9시간 20분 동안 그 기기의 진척이 저장소에 안 나타났습니다. 제 메움 지표는 **배달 경로를 거쳐**
#   재므로, 그 상태를 "그 기기가 죽었다" 로 읽습니다 — 10:00 게이트가 아니었으면 겹쳐 돌았을 것입니다.
#   **러너를 띄우는 자리가 postman 을 되살릴 유일한 자리입니다**(재부팅 뒤 러너는 사람이 띄우므로).
#   죽이지 않고 **보고 없으면 띄우기만** 합니다. 탐지는 `ps`+`grep -v grep` — `pgrep -f` 금지(CLAUDE.md §4).
ensure_postman(){
  if ps -eo args | grep -v grep | grep -q "postman_${MACH}\.sh"; then return 0; fi
  if [ ! -x "$HOME/.mof_postman/postman_${MACH}.sh" ] && [ ! -f "$HOME/.mof_postman/postman_${MACH}.sh" ]; then
    say "!! postman 사본이 없습니다 — 되살리지 못했습니다"; return 1; fi
  say "!! postman 이 죽어 있습니다 — 되살립니다"
  ( cd "$G" && POSTMAN_ROOT="$G" setsid nohup bash "$HOME/.mof_postman/postman_${MACH}.sh" "$MACH" \
      >> "$G/.postman_${MACH}.err" 2>&1 < /dev/null & )      # stderr 를 버리지 않습니다(laptop2 ②)
  sleep 3
  ps -eo args | grep -v grep | grep -q "postman_${MACH}\.sh" \
    && say "postman 되살림 확인" || say "!! postman 되살리기 실패 — .postman_${MACH}.err 를 보십시오"
}

ensure_postman
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
ensure_postman

# 밀도맵이 끝난 뒤 계산이 실제로 멎었는지 다시 확인하고 메움 감시로 넘어갑니다.
q=0; while [ "$q" -lt 3 ]; do if [ "$(pgrep -xc simulate)" = "0" ]; then q=$((q+1)); else q=0; fi; sleep 60; done
say "simulate 재정지 확인 — 메움 감시 시작"
# ───────────────────────────────────────────────────────────────────────────

# 생존 문턱 둘 — 랩탑 11:3x 의 정리대로 두 지표는 **전량 실패 중인 기기**에서 갈립니다.
#   주  `run_status` 지표가 **9 h** 안 바뀌면 죽음  (실패해도 오르므로 **중복을 덜 냅니다**)
#   보조 `값` 칸이 **10 h** 안 늘면 죽음            (주 지표만 두면 **남이 전량 실패에 빠졌을 때
#        run_status 만 계속 올라 아무도 안 메웁니다** — 10:39 에 제가 172종을 3분 만에
#        전부 `[no-output]` 낸 그 상태. 랩탑 지표가 덮지만 그쪽이 같이 죽으면 남는 자리입니다.)
# ★ 문턱을 **짐작하지 않고 러너에서 유도**했습니다 (2026-09-24, laptop2 지적).
#   `run_aryl_gcmc.py:203` 의 `timeout=28800` — **단일 작업은 8 h 를 넘을 수 없습니다.**
#   그러므로 **9 h 무변화는 "도는 것이 없다" 를 뜻합니다.** 3 h 는 짧았습니다:
#   laptop2 의 `2024_Cd__dia_3_FSR_1`(N_super 4928)이 0.15 bar 에서 8 h 에 잘려 **혼자 재시도 중**인데,
#   재시도는 같은 칸이 timeout→ok 로 **바뀔 뿐**이라 개수 지표가 안 움직이고, 그 5.5 h 동안
#   3 h 문턱이면 메움이 깨어 **같은 구조를 겹쳐 돕니다.**
#   (지표 자체도 내용 민감하게 고쳤습니다 — corewc3_missing.py 의 `1 + len(status)`.)
prevc=-1; prevv=-1; sc=0; sv=0; n=0
while :; do
  ensure_postman
  git -C "$G" fetch -q --all 2>/dev/null
  out=$("$PY" "$HOME/.mof_chain/corewc3_missing.py" 2>>"$LOG" | tail -1)
  n=$(echo "$out" | awk '{print $1}'); cells=$(echo "$out" | awk '{print $2}'); vals=$(echo "$out" | awk '{print $3}')
  case "${n:-x}${cells:-x}${vals:-x}" in *[!0-9]*) say "지표 계산 실패 ('$out') — 15분 뒤 다시"; sleep 900; continue;; esac
  [ "$cells" = "$prevc" ] && sc=$((sc+1)) || sc=0; prevc=$cells
  [ "$vals"  = "$prevv" ] && sv=$((sv+1)) || sv=0; prevv=$vals
  say "남은 ${n}종 · run_status ${cells}(정지 ${sc}/36) · 값 ${vals}(정지 ${sv}/40)"
  [ "$n" = "0" ] && { say "남은 것 0 — 조용히 종료"; exit 0; }
  now=$(date +%s)
  if { [ "$now" -ge "$T1" ] && { [ "$sc" -ge 36 ] || [ "$sv" -ge 40 ]; }; } || [ "$now" -ge "$T2" ]; then break; fi
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

say "메움 착수 ${n}종 (run_status ${prevc} 정지 ${sc}/36 · 값 ${prevv} 정지 ${sv}/40)"
export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH" RASPA_DIR="$GD"
cd "$R" || exit 1
export COREWC_ASSIGN=desktop COREWC_MACHINE=desktop COREWC_WORKERS=8
export COREWC_PICK="$R/core_wc_pick3_desktop_run.json"
export COREWC_OUT="$R/core_wc_results_ext2_desktop.json"
python3 run_core_wc.py >> "$LOG" 2>&1
say "메움 종료"
