#!/bin/bash
# postman.sh — 기기 공용 자동 우편배달부. 기동: cd ~/mof_project && setsid nohup bash postman.sh <기기이름> > /dev/null 2>&1 < /dev/null &
#
# [출처] 09-19 11:0x 데스크탑 세션 설계(POSTMAN.md). 랩탑·laptop2 가 14:34 에 띄운 44줄 판(md5 691c7d0f)을
#        기준으로 두고, 두 기기가 첫 주기에 실측으로 잡은 결함 셋만 고쳤습니다(15:0x, 종합자):
#   (1) tracked_dirty 영구 교착 — 랩탑 crontab 의 watchdog.sh 가 매시 21_ZIF69_MTV/watchdog.log 에 한 줄 붙임
#       → RESULT_PATTERNS 에 watchdog.log 추가(랩탑 (가) 권고). 같은 주기에 커밋돼 dirty 가 스스로 풀립니다.
#   (2) repo_bash_running 이 bash 스크립트만 봄 — §AK ⑥·§AM 1C 처럼 **파이썬 러너를 직접 띄운** 기기에서는
#       5분마다 pull 이 돌고, RESULT_PATTERNS 에 charged_v3/*_DDEC6.cif 가 있어 작업마다 CIF 를 복사하는 러너
#       (run_humid_wc.py:98) 밑에서 구조가 바뀔 수 있음(laptop2 지적) → runner_running() 추가, simulate 가 돌거나
#       run_*.py 가 살아 있으면 pull/merge 건너뜀.
#   (3) 첫 틱에 옛 로그 범람 — $STATE/sz_* 가 없으면 old=0 이라 로그 전체를 훑음(두 기기 다 09-03 tb5 줄이 올라옴)
#       → 기동 시 현재 크기로 미리 채움.
# 판정·착수·문서 편집은 하지 않습니다. pkill -f 없음(CLAUDE.md §4). 죽일 때는 PID 로.
set -u
MACHINE="${1:-$(hostname)}"; INTERVAL="${POSTMAN_INTERVAL:-300}"
cd "$(dirname "$0")" || exit 1; ROOT=$(pwd)
INBOX="$ROOT/.postman_inbox_$MACHINE"; LOG="$ROOT/.postman_$MACHINE.log"; FLAG="$ROOT/.postman_flag"
STATE="$ROOT/.postman_state_$MACHINE"; mkdir -p "$STATE"
RESULT_PATTERNS='21_ZIF69_MTV/v3w_humid_wc*/*.json 21_ZIF69_MTV/v3w_humid_wc*/*.jsonl 21_ZIF69_MTV/v3w_water*/*.json 21_ZIF69_MTV/results_*.json 21_ZIF69_MTV/risk_results*.json 21_ZIF69_MTV/relax_v3/*_relaxed.cif 21_ZIF69_MTV/charged_v3/*_DDEC6.cif 21_ZIF69_MTV/relax_v3_judged.json 21_ZIF69_MTV/risk_v3sub_index.json 21_ZIF69_MTV/COMMS/*.md 21_ZIF69_MTV/watchdog.log 21_ZIF69_MTV/tnf_results_*.json 21_ZIF69_MTV/tnf_widom_*.json'
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }
inbox(){ echo "[$(date '+%m-%d %H:%M')] $*" >> "$INBOX"; touch "$FLAG"; }
repo_bash_running(){ ps -eo args | grep -E "^(/bin/)?bash .*\.sh" | grep -v postman.sh | grep -vE "wsl_keepalive|lammps_watchdog|ensure_guards" | grep -qE "$ROOT|^bash [^/]"; }
runner_running(){ pgrep -x simulate >/dev/null || pgrep -f "python[0-9.]* .*run_[A-Za-z0-9_]*\.py" >/dev/null; }
# (4) 15:1x 데스크탑 실측 — ensure_guards 가 띄우는 wsl_keepalive.sh 가 상시 돌아 repo_bash_running 이 늘 참이 됐음(pull 영구 건너뜀). 저장소 밖 감시자 셋은 제외.
tracked_dirty(){ git status --porcelain --untracked-files=no | grep -vE "^ M \.claude/" | grep -q .; }
# (3) 첫 틱 범람 방지 — 이미 있는 로그는 지금 크기부터 증분만 본다
for f in "$ROOT"/.claude_work_*.out "$ROOT"/21_ZIF69_MTV/*_chain.log; do
  [ -f "$f" ] || continue; k=$(basename "$f")
  [ -f "$STATE/sz_$k" ] || stat -c %s "$f" > "$STATE/sz_$k"
done
[ -f "$STATE/tick" ] || touch "$STATE/tick"
say "시작 machine=$MACHINE branch=$(git rev-parse --abbrev-ref HEAD)"; inbox "postman 시작 ($MACHINE)"
prev_sim=$(pgrep -xc simulate)
while :; do
  BR=$(git rev-parse --abbrev-ref HEAD)
  if git fetch -q --all 2>>"$LOG"; then
    for rb in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -vE "HEAD|claude/|magi004-|junseok"); do
      key=$(echo "$rb" | tr '/' '_'); last=$(cat "$STATE/$key" 2>/dev/null || echo ""); cur=$(git rev-parse "$rb")
      if [ -n "$last" ] && [ "$last" != "$cur" ]; then
        git log --format="  %h %ad %s" --date=format:'%m-%d %H:%M' "$last..$cur" | head -8 | while read -r l; do inbox "[$rb] $l"; done
        if [ "$BR" = "master" ] && [ "$rb" != "origin/master" ]; then
          files=$(git diff --name-only "$last" "$cur" -- $RESULT_PATTERNS 2>/dev/null | grep -v COMMS/)
          if [ -n "$files" ]; then echo "$files" | xargs -r git checkout "$cur" -- 2>>"$LOG" && git add $files && \
            git commit -q -m "[postman:$MACHINE] $rb 결과 반입 ($(git rev-parse --short "$cur"))" && git push -q origin master 2>>"$LOG" && inbox "[반입] $rb → master: $(echo "$files" | tr '\n' ' ')"; fi
        fi
      fi; echo "$cur" > "$STATE/$key"
    done
  else say "fetch 실패"; fi
  if repo_bash_running || runner_running; then say "저장소 bash/러너 실행 중 — pull 건너뜀"; elif tracked_dirty; then say "추적 파일 수정 — pull 건너뜀"; else
    if [ "$BR" = "master" ]; then git pull -q --ff-only origin master 2>>"$LOG" || inbox "!! master ff-pull 실패"
    else git merge -q --no-edit origin/master 2>>"$LOG" || { git merge --abort 2>/dev/null; inbox "!! origin/master merge 충돌"; }; fi
  fi
  # (5) 15:4x 데스크탑 실측 — 안 맞는 글롭이 하나라도 있으면(예: tnf_widom_*.json 이 아직 없음) git add 가 rc=128 로
  #     **아무것도 안 올림**. ③ 이 조용히 죽어 있었음(15:07 기동 뒤 푸시 0건). 패턴별로 add 하고 실패는 로그에.
  for p in $RESULT_PATTERNS; do [ -e "$p" ] && { git add "$p" 2>>"$LOG" || say "add 실패 $p"; }; done
  if ! git diff --cached --quiet; then n=$(git diff --cached --name-only | wc -l)
    git commit -q -m "[postman:$MACHINE] 결과 파일 자동 반입 ${n}건" && git push -q origin "$BR" 2>>"$LOG" && inbox "[푸시] $BR ← 결과 ${n}건 $(git log -1 --format=%h)" || inbox "!! 자동 커밋/푸시 실패"; fi
  sim=$(pgrep -xc simulate); [ "$sim" != "$prev_sim" ] && { inbox "[simulate] $prev_sim → $sim"; prev_sim=$sim; }
  for f in "$ROOT"/.claude_work_*.out "$ROOT"/21_ZIF69_MTV/*_chain.log; do [ -f "$f" ] || continue
    k=$(basename "$f"); old=$(cat "$STATE/sz_$k" 2>/dev/null || echo 0); new=$(stat -c %s "$f")
    [ "$new" -gt "$old" ] && tail -c $((new-old)) "$f" | grep -E "rc=|Traceback|OOM|Killed|!!|\[OK\]|완주|사슬 종료|결과 파일" | head -5 | while read -r l; do inbox "[$k] $l"; done
    echo "$new" > "$STATE/sz_$k"; done
  find "$ROOT/21_ZIF69_MTV" -maxdepth 2 \( -name "*.json" -path "*v3w_*" -o -name "risk_results*.json" -o -name "tnf_results_*.json" -o -name "tnf_widom_*.json" \) -newer "$STATE/tick" 2>/dev/null | while read -r f; do inbox "[결과 파일] ${f#$ROOT/}"; done
  touch "$STATE/tick"; sleep "$INTERVAL"
done
