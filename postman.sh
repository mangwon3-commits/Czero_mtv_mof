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
#   (8) 09-21 15:1x laptop2 지적 — §AV 결과(core_pop_results_*.json)가 RESULT_PATTERNS 에 없어 master 에
#       영영 안 올라갔음. §9-1 재배분이 그 파일을 읽어야 발동하므로 **재배분이 통째로 막힐 뻔했음.**
#       core_pop_results_*.json 과 bridge_core_results.json 추가. (돌던 판은 PID 로 정지 후 편집 — §6)
#   (9) 09-21 15:2x 랩탑 Melchior 발견 — ★ **postman 이 자기 발을 밟습니다.** 5분마다 pull/merge 를 하는데
#       그 pull 이 `postman.sh` **자신을** 덮어쓸 수 있고, bash 는 스크립트를 **바이트 오프셋으로** 읽으므로
#       돌던 판이 엉뚱한 줄을 실행합니다(CLAUDE.md §6). 실측: 랩탑의 도는 프로세스가 09-19 15:46 기동인데
#       파일 mtime 이 09-20 10:03 — **29시간을 운으로 버텼습니다.** 세 기기가 같은 노출이었습니다.
#       해법(종합자 결정, 랩탑이 낸 두 길의 합): **저장소 밖 사본을 돌린다.** git 이 건드릴 수 없는 자리라
#       창이 아예 없습니다. 그리고 **틱마다 저장소 판과 견줘 다르면 사본을 새로 떠서 `exec`** 하므로
#       (가)의 낡음 문제도 없습니다. 교체는 `mv`(원자적 rename)라 돌던 프로세스는 옛 inode 를 계속 씁니다.
# 판정·착수·문서 편집은 하지 않습니다. pkill -f 없음(CLAUDE.md §4). 죽일 때는 PID 로.
set -u
MACHINE="${1:-$(hostname)}"; INTERVAL="${POSTMAN_INTERVAL:-300}"
ROOT="${POSTMAN_ROOT:-$(cd "$(dirname "$0")" && pwd)}"
RUNDIR="$HOME/.mof_postman"; RUNSELF="$RUNDIR/postman_$MACHINE.sh"
if [ "$(cd "$(dirname "$0")" && pwd)" != "$RUNDIR" ]; then   # (9) 저장소 안에서 떴으면 밖 사본으로 넘어간다
  mkdir -p "$RUNDIR" && cp -f "$0" "$RUNSELF.new" && bash -n "$RUNSELF.new" \
    && mv -f "$RUNSELF.new" "$RUNSELF" && POSTMAN_ROOT="$ROOT" exec bash "$RUNSELF" "$MACHINE"
  rm -f "$RUNSELF.new"; echo "!! 사본 뜨기 실패(문법 오류거나 복사 실패) — 저장소 판으로 계속" >&2
fi
cd "$ROOT" || exit 1
INBOX="$ROOT/.postman_inbox_$MACHINE"; LOG="$ROOT/.postman_$MACHINE.log"; FLAG="$ROOT/.postman_flag"
STATE="$ROOT/.postman_state_$MACHINE"; mkdir -p "$STATE"
RESULT_PATTERNS='21_ZIF69_MTV/v3w_humid_wc*/*.json 21_ZIF69_MTV/v3w_humid_wc*/*.jsonl 21_ZIF69_MTV/v3w_water*/*.json 21_ZIF69_MTV/results_*.json 21_ZIF69_MTV/risk_results*.json 21_ZIF69_MTV/relax_v3/*_relaxed.cif 21_ZIF69_MTV/charged_v3/*_DDEC6.cif 21_ZIF69_MTV/relax_v3_judged.json 21_ZIF69_MTV/risk_v3sub_index.json 21_ZIF69_MTV/COMMS/*.md 21_ZIF69_MTV/watchdog.log 21_ZIF69_MTV/tnf_results_*.json 21_ZIF69_MTV/tnf_widom_*.json 21_ZIF69_MTV/core_pop_results_*.json 21_ZIF69_MTV/bridge_core_results.json 21_ZIF69_MTV/core_wc_results_*.json 21_ZIF69_MTV/pair_times_*.json 21_ZIF69_MTV/MACHINE_CAPABILITIES.md'
say(){ echo "[$(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }
inbox(){ echo "[$(date '+%m-%d %H:%M')] $*" >> "$INBOX"; touch "$FLAG"; }
repo_bash_running(){ ps -eo args | grep -E "^(/bin/)?bash .*\.sh" | grep -v postman.sh | grep -vE "wsl_keepalive|lammps_watchdog|ensure_guards" | grep -qE "$ROOT|^bash [^/]"; }
runner_running(){ pgrep -x simulate >/dev/null || pgrep -f "python[0-9.]* .*run_[A-Za-z0-9_]*\.py" >/dev/null; }
# (11) 09-23 10:2x — **같은 결함이 §AW 에서 반복**. (8)에서 `core_pop_results_*` 를 넣었는데
#      §AW 의 `core_wc_results_*` 는 **또 빠져** 있었습니다. 패턴이 **시험 이름마다 늘어나는 구조**라
#      새 시험을 열 때마다 같은 자리에서 막힙니다. `pair_times_*` 와 `MACHINE_CAPABILITIES.md`
#      (어제 두 기기가 **손으로** 올려야 했던 것)도 같이 넣습니다.
#      ⚠ **새 시험을 열면 결과 경로를 여기 먼저 넣으십시오** — 안 넣으면 결과가 영영 master 에 안 옵니다.
# (10) 09-21 15:3x laptop2 지적 — ★ **깨진 결과 파일을 올리지 않습니다.**
#      러너가 쓰는 중인 결과 JSON 에 git 이 충돌 표시를 박을 수 있고(§6, 랩탑 실측), 러너가 다음 쓰기로
#      덮어 복구하기까지 **최대 한 작업 길이(13~50분)** 가 걸립니다. 그 창에서 **postman 이 5분마다
#      그 깨진 파일을 master 로 밀어냅니다** — 사람이 안 보는 사이에. 그래서 올리기 전에 봅니다.
#      충돌 표시는 확정 증거이고, 괄호 끝맞춤은 잘림을 싸게 잡습니다(파이썬 없이도 됩니다).
file_broken(){
  grep -qE '^(<<<<<<<|=======$|>>>>>>>)' "$1" && return 0
  case "$1" in *.json)
      head -c 200 "$1" | tr -d '[:space:]' | grep -qE '^[[{]' || return 0
      tail -c 200 "$1" | tr -d '[:space:]' | grep -qE '[]}]$' || return 0 ;;
  esac
  return 1
}
# (4) 15:1x 데스크탑 실측 — ensure_guards 가 띄우는 wsl_keepalive.sh 가 상시 돌아 repo_bash_running 이 늘 참이 됐음(pull 영구 건너뜀). 저장소 밖 감시자 셋은 제외.
tracked_dirty(){ git status --porcelain --untracked-files=no | grep -vE "^ M \.claude/" | grep -q .; }
# (3) 첫 틱 범람 방지 — 이미 있는 로그는 지금 크기부터 증분만 본다
for f in "$ROOT"/.claude_work_*.out "$ROOT"/21_ZIF69_MTV/*_chain.log; do
  [ -f "$f" ] || continue; k=$(basename "$f")
  [ -f "$STATE/sz_$k" ] || stat -c %s "$f" > "$STATE/sz_$k"
done
[ -f "$STATE/tick" ] || touch "$STATE/tick"
say "시작 machine=$MACHINE branch=$(git rev-parse --abbrev-ref HEAD) 판=$(md5sum "$RUNSELF" 2>/dev/null | cut -c1-8)"
# (9-2) 도는 판의 md5 를 남깁니다 — laptop2: **"보호가 실제로 그 기기에 도착했는지 그 기기가 확인해야 한다."**
#       보낸 쪽은 볼 수 없는 자리입니다. 같은 형태로 오늘 세 번 났습니다(패턴·자기복사판·(10) 관문).
inbox "postman 시작 ($MACHINE) 판 $(md5sum "$RUNSELF" 2>/dev/null | cut -c1-8)"
prev_sim=$(pgrep -xc simulate)
while :; do
  # (9) 저장소 판이 바뀌었으면 사본을 새로 떠서 넘어간다. **루프 맨 위**에 둡니다 —
  #     처음엔 pull 블록 뒤에 뒀는데 그 블록이 `runner_running` 가드 안이라, 러너가 도는 동안
  #     (= 대개의 시간) 영영 안 걸렸습니다. 저장소 판은 postman 의 pull 말고도 사람·다른 세션의
  #     merge 로 바뀝니다. `if…fi` 는 bash 가 통째로 읽은 뒤 실행하고 교체는 mv(원자적 rename)라
  #     돌던 파일은 안 바뀝니다.
  BR=$(git rev-parse --abbrev-ref HEAD)
  if git fetch -q --all 2>>"$LOG"; then
    for rb in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep -vE "HEAD|claude/|magi004-|junseok|^origin$"); do  # (7) 15:5x: 짧은 이름 origin(=origin/HEAD) 이 브랜치로 취급돼 master 의 남의 푸시를 ④ 로 재커밋(e202853) → 갈래가 생김. 제외.
      key=$(echo "$rb" | tr '/' '_'); last=$(cat "$STATE/$key" 2>/dev/null || echo ""); cur=$(git rev-parse "$rb")
      if [ -n "$last" ] && [ "$last" != "$cur" ]; then
        git log --format="  %h %ad %s" --date=format:'%m-%d %H:%M' "$last..$cur" | head -8 | while read -r l; do inbox "[$rb] $l"; done
      fi; echo "$cur" > "$STATE/$key"
      # (12) 2026-09-23 laptop2 — **반입을 state 에서 떼어 냅니다.** 위 `echo "$cur" > $STATE/$key` 는 `fi` 밖이라
      #      **반입이 안 됐어도 state 가 올라갑니다.** 그래서 패턴이 없던 시각에 틱이 그 커밋을 한 번 보고 지나가면
      #      그 커밋이 last 로 박히고, 이후 틱은 `cur ^last` 범위만 보므로 **그 파일은 영영 안 옵니다 —
      #      패턴을 나중에 고쳐도 소급되지 않습니다.** 09-23 §AW 가 이 창에 걸릴 뻔했습니다(내용은 무사).
      #      그래서 커밋 범위를 버리고 **트리를 직접 견줍니다.** 어느 창을 놓쳐도 다음 틱이 스스로 회복합니다.
      #      ^HEAD 가 하던 "master 가 더 새것이면 덮지 않기"(결함 (6)) 는 **파일별 조상 검사**로 대신합니다 —
      #      브랜치에서 그 파일을 마지막으로 만진 커밋이 이미 master 안이면 건너뜁니다.
      if [ "$BR" = "master" ] && [ "$rb" != "origin/master" ]; then
        set -f; cand=$(git diff --name-only HEAD "$cur" -- $RESULT_PATTERNS 2>/dev/null | grep -v COMMS/); set +f
        files=""
        for f in $cand; do
          bc=$(git log -1 --format=%H "$cur" -- "$f" 2>/dev/null)
          [ -n "$bc" ] || continue                                   # 브랜치엔 없는 파일(master 쪽 삭제/신규) — 건드리지 않는다
          git merge-base --is-ancestor "$bc" HEAD 2>/dev/null && continue   # master 가 이미 그 커밋을 가짐 → 더 오래된 판으로 덮지 않는다
          files="$files$f
"
        done
        files=$(printf '%s' "$files" | sed '/^$/d')
        if [ -n "$files" ]; then echo "$files" | xargs -r git checkout "$cur" -- 2>>"$LOG" && git add $files && \
          git commit -q -m "[postman:$MACHINE] $rb 결과 반입 ($(git rev-parse --short "$cur"))" && \
          { git push -q origin master 2>>"$LOG" || { \
              # (13) 2026-09-23 — push 가 거절되면 **이후 매 바퀴 ff-pull 이 실패해 반입이 영구 정지**합니다.
              #      10:32~10:33 데스크탑 실측(laptop2 손 커밋 fc7dc3e8 과 ④ 반입이 경주). postman 은 자기 반입
              #      커밋을 rebase 하지 않았습니다. 한 번 rebase 하고 다시 밉니다 — 실패하면 우편함에 적고 넘어갑니다.
              say "push 거절 — rebase 재시도"; git pull --rebase -q origin master 2>>"$LOG" && git push -q origin master 2>>"$LOG"; }; } \
          && inbox "[반입] $rb → master: $(echo "$files" | tr '\n' ' ')"; fi
      fi
    done
  else say "fetch 실패"; fi
  # (9-3) 09-21 15:4x — 판정을 **fetch 뒤**로 옮겼습니다(랩탑이 넘긴 판단).
  #   앞에 있으면 직전 틱이 받아 온 ref 를 써서 새 판이 **최대 두 틱(~10분)** 뒤에 넘어갔습니다.
  #   랩탑 우려("fetch 실패한 틱에서 판정이 통째로 건너뛰어진다")는 **배치로 피합니다** —
  #   `if git fetch …; then … fi` **블록 밖**에 두었으므로 fetch 가 실패해도 판정은 돕니다
  #   (그 틱은 낡은 ref 로 보는 것뿐, 예전과 같음). 두 걱정을 동시에 없앱니다.
  # (9-2) 09-21 15:3x laptop2 발견 — ★ **작업트리와 견주면 안 됩니다.**
  #   작업트리는 pull/merge 로만 바뀌는데 그 pull 을 postman 자신이 `runner_running` 가드로 건너뜁니다.
  #   그래서 **러너가 도는 기기에서는 (9)가 영영 안 걸리고, 러너가 도는 기기가 바로 보호가 필요한 기기**입니다.
  #   laptop2 실측: origin/master fe4a3bf0 / 작업트리 cb16a7b7 / 사본 cb16a7b7 — 둘이 같아 갱신이 안 걸림.
  #   -> **`origin/master` 판과 견줍니다.** fetch 는 가드 밖이라 러너가 돌아도 돕니다.
  #      작업트리를 건드리지 않으므로 §6 위험도 없습니다.
  NEWSELF="$RUNDIR/.new_$MACHINE"
  if git show origin/master:postman.sh > "$NEWSELF" 2>>"$LOG" && [ -s "$NEWSELF" ] \
     && ! cmp -s "$NEWSELF" "$RUNSELF"; then
    if bash -n "$NEWSELF" 2>>"$LOG"; then
      say "postman.sh 갱신 감지(origin/master $(md5sum "$NEWSELF" | cut -c1-8)) — 사본을 새로 떠서 재기동"
      inbox "postman 자체 갱신 -> 재기동 (판 $(md5sum "$NEWSELF" | cut -c1-8))"
      mv -f "$NEWSELF" "$RUNSELF" && POSTMAN_ROOT="$ROOT" exec bash "$RUNSELF" "$MACHINE"
    else say "!! origin/master 판이 잘렸거나 문법 오류 — 이번 틱은 넘어감"; rm -f "$NEWSELF"; fi
  else rm -f "$NEWSELF"; fi
  if repo_bash_running || runner_running; then say "저장소 bash/러너 실행 중 — pull 건너뜀"; elif tracked_dirty; then say "추적 파일 수정 — pull 건너뜀"; else
    if [ "$BR" = "master" ]; then git pull -q --ff-only origin master 2>>"$LOG" || inbox "!! master ff-pull 실패"
    else git merge -q --no-edit origin/master 2>>"$LOG" || { git merge --abort 2>/dev/null; inbox "!! origin/master merge 충돌"; }; fi
  fi
  # (5) 15:4x 데스크탑 실측 — 안 맞는 글롭이 하나라도 있으면(예: tnf_widom_*.json 이 아직 없음) git add 가 rc=128 로
  #     **아무것도 안 올림**. ③ 이 조용히 죽어 있었음(15:07 기동 뒤 푸시 0건). 패턴별로 add 하고 실패는 로그에.
  for p in $RESULT_PATTERNS; do [ -e "$p" ] && { git add "$p" 2>>"$LOG" || say "add 실패 $p"; }; done
  # (10) 깨진 것은 스테이지에서 도로 뺍니다. **다음 틱에 다시 봅니다** — 러너가 덮어쓰면 저절로 풀립니다.
  for f in $(git diff --cached --name-only); do
    [ -f "$f" ] || continue
    if file_broken "$f"; then git restore --staged "$f" 2>/dev/null || git reset -q HEAD -- "$f"
      say "!! 깨진 결과 파일 — 올리지 않음: $f"; inbox "!! **깨진 결과 파일 반려** $f (러너가 덮어쓰면 다음 틱에 올라갑니다)"; fi
  done
  if ! git diff --cached --quiet; then n=$(git diff --cached --name-only | wc -l)
    if git commit -q -m "[postman:$MACHINE] 결과 파일 자동 반입 ${n}건" && git push -q origin "$BR" 2>>"$LOG"; then
      inbox "[푸시] $BR ← 결과 ${n}건 $(git log -1 --format=%h)"
    else
      # (14) 2026-09-23 — **(13) 은 ④ 반입 경로만 고쳤고 여기는 안 고쳤습니다.** 그래서 남이 먼저 밀면
      #      이 push 가 거절되고, 그 뒤로 매 틱 같은 자리에서 실패합니다. `repo_bash_running` 가드가
      #      pull 을 건너뛰므로 **스스로는 영영 안 풀립니다** — 데스크탑이 09-23 20:0x 에 그 상태였습니다
      #      (로컬 3 앞 · 1 뒤, 실패 22회 누적).
      #      **`reset --mixed` 는 작업트리를 하나도 안 건드립니다** — 러너가 결과 JSON 을 쓰는 중에도
      #      안전한 유일한 되돌리기입니다(`--hard` 는 절대 금지: 09-21 의 충돌 표시 사고와 같은 자리).
      #      HEAD 만 원격 끝으로 옮기면 다음 틱의 add/commit 이 **현재 작업트리를** 올립니다.
      #      혹시 남의 파일이 한 틱 뒤처지더라도 (12) 의 트리 대조가 다음 틱에 다시 들여옵니다.
      say "push 거절 — origin/$BR 로 재동기화(작업트리 불변) 뒤 다음 틱에 재시도"
      if git fetch -q origin "$BR" 2>>"$LOG" && git reset -q --mixed "origin/$BR" 2>>"$LOG"; then
        inbox "!! 푸시 거절 — origin/$BR 로 재동기화했습니다(작업트리 안 건드림). 다음 틱에 재시도합니다."
      else inbox "!! 자동 커밋/푸시 실패 — 재동기화도 실패"; fi
    fi; fi
  sim=$(pgrep -xc simulate); [ "$sim" != "$prev_sim" ] && { inbox "[simulate] $prev_sim → $sim"; prev_sim=$sim; }
  for f in "$ROOT"/.claude_work_*.out "$ROOT"/21_ZIF69_MTV/*_chain.log; do [ -f "$f" ] || continue
    k=$(basename "$f"); old=$(cat "$STATE/sz_$k" 2>/dev/null || echo 0); new=$(stat -c %s "$f")
    [ "$new" -gt "$old" ] && tail -c $((new-old)) "$f" | grep -E "rc=|Traceback|OOM|Killed|!!|\[OK\]|완주|사슬 종료|결과 파일" | head -5 | while read -r l; do inbox "[$k] $l"; done
    echo "$new" > "$STATE/sz_$k"; done
  find "$ROOT/21_ZIF69_MTV" -maxdepth 2 \( -name "*.json" -path "*v3w_*" -o -name "risk_results*.json" -o -name "tnf_results_*.json" -o -name "tnf_widom_*.json" \) -newer "$STATE/tick" 2>/dev/null | while read -r f; do inbox "[결과 파일] ${f#$ROOT/}"; done
  touch "$STATE/tick"; sleep "$INTERVAL"
done
