#!/bin/bash
# COREPOP-H323 게시 도구(기기 공용) — 우편함 글 · SESSION_LOG 한 줄 · 결과 파일을 master 에 올림.
# 랩탑의 ~/.mof_chain/post_master_laptop.sh(11-11 부터 씀)를 기기 이름을 받도록 넓힌 판. HANDOVER_COREPOP_NEWMACHINE_20261115.md §6.
# 임시 인덱스 + commit-tree + push 라 작업트리를 건드리지 않음(러너가 결과 JSON 을 쓰는 중에도 안전 · CLAUDE.md §6).
# 저장소 밖으로 복사해서 씀:  cp 21_ZIF69_MTV/corepop_post.sh ~/.mof_chain/
# 쓰는 법:
#   bash ~/.mof_chain/corepop_post.sh <기기> <커밋 메시지 파일> <우편함 글 파일> <SESSION_LOG 줄 파일|-> [<원본 경로>=<저장소 경로> ...]
#   · 우편함 글은 21_ZIF69_MTV/COMMS/<기기>.md 맨 앞에(최신이 위). 우편함이 master 에 없으면 머리말과 함께 새로 만듦.
#   · SESSION_LOG 줄은 첫 '## MM-DD' 줄 앞에. '-' 면 건드리지 않음.
#   · POST_DRY=1 이면 push 하지 않고 만들어질 커밋만 보여 줌(먼저 이것으로 확인).
#   · REPO(기본 ~/mof_project) 는 env 로 덮을 수 있음.
set -u
[ $# -ge 4 ] || { echo "쓰는 법: corepop_post.sh <기기> <커밋 메시지 파일> <우편함 글 파일> <SESSION_LOG 줄 파일|-> [원본=저장소경로 ...]"; exit 2; }
M=$1
case "$M" in *[!a-z0-9_]*|'') echo "!! 기기 이름은 소문자 · 숫자 · _ 만: $M"; exit 2;; esac
REPO=${REPO:-$HOME/mof_project}
MSG=$(realpath "$2") || exit 2
POST=$(realpath "$3") || exit 2
if [ "$4" = "-" ]; then SLOG=-; else SLOG=$(realpath "$4") || exit 2; fi
shift 4
MAIL=21_ZIF69_MTV/COMMS/$M.md
[ -s "$MSG" ] && [ -s "$POST" ] || { echo "!! 커밋 메시지 또는 우편함 글 파일이 비었음"; exit 2; }
for try in 1 2 3 4 5; do
  git -C "$REPO" fetch -q origin master || { echo "fetch 실패 — 60초 뒤 다시"; sleep 60; continue; }
  BASE=$(git -C "$REPO" rev-parse refs/remotes/origin/master) || exit 1
  IDX=$(mktemp /tmp/cpost_idx.XXXXXX); TMPD=$(mktemp -d /tmp/cpost_tmp.XXXXXX)
  export GIT_INDEX_FILE=$IDX
  git -C "$REPO" read-tree "$BASE" || exit 1
  ok=1
  for pair in "$@"; do
    src=${pair%%=*}; dst=${pair#*=}
    [ -f "$src" ] || { echo "!! 원본 없음 $src"; ok=0; continue; }
    case "$dst" in /*|*..*) echo "!! 저장소 경로가 이상함 $dst"; ok=0; continue;; esac
    b=$(git -C "$REPO" hash-object -w "$src") && git -C "$REPO" update-index --add --cacheinfo "100644,$b,$dst" || ok=0
  done
  if git -C "$REPO" cat-file -e "$BASE:$MAIL" 2>/dev/null; then
    git -C "$REPO" show "$BASE:$MAIL" > "$TMPD/old_mail" || exit 1
  else
    printf '# %s 우편함 — %s 만 씁니다\n\n이 파일은 **%s 만** 씁니다. 규약은 `21_ZIF69_MTV/COMMS.md`. 최신 글이 위에 옵니다.\n' "$M" "$M" "$M" > "$TMPD/old_mail"
  fi
  python3 - "$POST" "$TMPD/old_mail" "$TMPD/new_mail" <<'E'
import sys
post = open(sys.argv[1], encoding='utf-8').read().rstrip('\n')
old = open(sys.argv[2], encoding='utf-8').read()
open(sys.argv[3], 'w', encoding='utf-8').write(post + '\n\n---\n\n' + old)
E
  b=$(git -C "$REPO" hash-object -w "$TMPD/new_mail") && git -C "$REPO" update-index --add --cacheinfo "100644,$b,$MAIL" || ok=0
  if [ "$SLOG" != "-" ]; then
    git -C "$REPO" show "$BASE:SESSION_LOG.md" > "$TMPD/old_slog" || exit 1
    python3 - "$SLOG" "$TMPD/old_slog" "$TMPD/new_slog" <<'E'
import re, sys
add = open(sys.argv[1], encoding='utf-8').read().rstrip('\n') + '\n\n'
lines = open(sys.argv[2], encoding='utf-8').read().splitlines(keepends=True)
i = next((n for n, l in enumerate(lines) if re.match(r'## \d\d-\d\d ', l)), len(lines))
open(sys.argv[3], 'w', encoding='utf-8').write(''.join(lines[:i]) + add + ''.join(lines[i:]))
E
    b=$(git -C "$REPO" hash-object -w "$TMPD/new_slog") && git -C "$REPO" update-index --add --cacheinfo "100644,$b,SESSION_LOG.md" || ok=0
  fi
  [ $ok = 1 ] || { echo "!! 인덱스 준비 실패 — 올리지 않음"; unset GIT_INDEX_FILE; rm -rf "$IDX" "$TMPD"; exit 1; }
  TREE=$(git -C "$REPO" write-tree); unset GIT_INDEX_FILE
  C=$(git -C "$REPO" commit-tree "$TREE" -p "$BASE" -F "$MSG")
  rm -rf "$IDX" "$TMPD"
  [ -n "$C" ] || { echo "!! 커밋을 만들지 못함(git user.name · user.email 설정 확인)"; exit 1; }
  if [ -n "${POST_DRY:-}" ]; then
    echo "POST_DRY — push 안 함 · 커밋 $C"; git -C "$REPO" diff --stat "$BASE" "$C"
    git -C "$REPO" show "$C:$MAIL" | head -8
    exit 0
  fi
  if git -C "$REPO" push -q origin "$C:refs/heads/master"; then
    echo "게시 $C (부모 $BASE)"; exit 0
  fi
  echo "push 거절 — 다시 받아 시도 $try"; sleep 30
done
echo "!! 게시 실패 5회"; exit 1
