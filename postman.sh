#!/bin/bash
# postman.sh — 기기 공용 자동 우편배달부. 기동: cd ~/mof_project && setsid nohup bash postman.sh <기기이름> > /dev/null 2>&1 < /dev/null &
set -u
MACHINE="${1:-$(hostname)}"; INTERVAL="${POSTMAN_INTERVAL:-300}"
cd "$(dirname "$0")" || exit 1; ROOT=$(pwd)
INBOX="$ROOT/.postman_inbox_$MACHINE"; LOG="$ROOT/.postman_$MACHINE.log"; FLAG="$ROOT/.postman_flag"
STATE="$ROOT/.postman_state_$MACHINE"; mkdir -p "$STATE"
RESULT_PATTERNS='21_ZIF69_MTV/v3w_humid_wc*/*.json 21_ZIF69_MTV/v3w_humid_wc*/*.jsonl 21_ZIF69_MTV/v3w_water*/*.json 21_ZIF69_MTV/results_*.json 21_ZIF69_MTV/risk_results*.json 21_ZIF69_MTV/relax_v3/*_relaxed.cif 21_ZIF69_MTV/charged_v3/*_DDEC6.cif 21_ZIF69_MTV/relax_v3_judged.json 21_ZIF69_MTV/risk_v3sub_index.json 21_ZIF69_MTV/COMMS/*.md'
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }
inbox(){ echo "[$(date '+%m-%d %H:%M')] $*" >> "$INBOX"; touch "$FLAG"; }
repo_bash_running(){ ps -eo args | grep -E "^(/bin/)?bash .*\.sh" | grep -v postman.sh | grep -qE "$ROOT|^bash [^/]"; }
tracked_dirty(){ git status --porcelain --untracked-files=no | grep -vE "^ M \.claude/" | grep -q .; }
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
  if repo_bash_running; then say "bash 실행 중 — pull 건너뜀"; elif tracked_dirty; then say "추적 파일 수정 — pull 건너뜀"; else
    if [ "$BR" = "master" ]; then git pull -q --ff-only origin master 2>>"$LOG" || inbox "!! master ff-pull 실패"
    else git merge -q --no-edit origin/master 2>>"$LOG" || { git merge --abort 2>/dev/null; inbox "!! origin/master merge 충돌"; }; fi
  fi
  git add $RESULT_PATTERNS 2>/dev/null
  if ! git diff --cached --quiet; then n=$(git diff --cached --name-only | wc -l)
    git commit -q -m "[postman:$MACHINE] 결과 파일 자동 반입 ${n}건" && git push -q origin "$BR" 2>>"$LOG" && inbox "[푸시] $BR ← 결과 ${n}건 $(git log -1 --format=%h)" || inbox "!! 자동 커밋/푸시 실패"; fi
  sim=$(pgrep -xc simulate); [ "$sim" != "$prev_sim" ] && { inbox "[simulate] $prev_sim → $sim"; prev_sim=$sim; }
  for f in "$ROOT"/.claude_work_*.out "$ROOT"/21_ZIF69_MTV/*_chain.log; do [ -f "$f" ] || continue
    k=$(basename "$f"); old=$(cat "$STATE/sz_$k" 2>/dev/null || echo 0); new=$(stat -c %s "$f")
    [ "$new" -gt "$old" ] && tail -c $((new-old)) "$f" | grep -E "rc=|Traceback|OOM|Killed|!!|\[OK\]|완주|사슬 종료|결과 파일" | head -5 | while read -r l; do inbox "[$k] $l"; done
    echo "$new" > "$STATE/sz_$k"; done
  find "$ROOT/21_ZIF69_MTV" -maxdepth 2 \( -name "*.json" -path "*v3w_*" -o -name "risk_results*.json" \) -newer "$STATE/tick" 2>/dev/null | while read -r f; do inbox "[결과 파일] ${f#$ROOT/}"; done
  touch "$STATE/tick"; sleep "$INTERVAL"
done
