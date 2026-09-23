#!/bin/bash
# mail_guard_junseok.sh — Junseok 의 postman 생존 확인, 없으면 띄운다. (2026-09-24)
#
# 왜: 09-23 laptop2 의 WSL 이 재부팅되며 postman 이 같이 죽었고 되살리는 것이 없어
#     9시간 20분 배달 공백이 났다(ASSIGN_JUNSEOK_20260924.md §0 ④). 러너는 돌았는데
#     저장소에서는 "죽은 기기" 로 보였다.
# 누가 부르나: ① 러너 기동 줄(맨 앞)  ② cron 10분마다 — 재부팅 뒤 로그인만 되면 다시 붙는다.
#
# ⚠ 이름에 주의: 이 파일 이름을 `ensure_postman_junseok.sh` 로 지으면 그 이름이
#   `postman_junseok.sh` 를 **포함**해서, 아래 탐지가 **자기 자신**을 postman 으로 봅니다
#   (CLAUDE.md §4 자기매칭 — 이 기기에서만 다섯 번 밟은 함정). 그래서 이름을 비껴 짓고
#   패턴도 사본 경로(`.mof_postman/`)까지 붙여 좁힙니다.
MACH=junseok
G=/home/mangwon/mof_project
COPY="$HOME/.mof_postman/postman_${MACH}.sh"
LOG="$G/.mail_guard_${MACH}.log"
say(){ printf '%s %s\n' "$(date '+%F %T')" "$1" >> "$LOG"; }

alive(){ ps -eo args | grep -v grep | grep -qE "\.mof_postman/postman_${MACH}\.sh|[ /]postman\.sh ${MACH}\$"; }

alive && exit 0

if [ -f "$COPY" ]; then
  say "postman 이 없습니다 — 사본으로 되살립니다"
  ( cd "$G" && POSTMAN_ROOT="$G" setsid nohup bash "$COPY" "$MACH" \
      >> "$G/.postman_${MACH}.err" 2>&1 < /dev/null & )
else
  say "postman 사본이 없습니다 — 저장소 판으로 첫 기동합니다(스스로 사본을 뜹니다)"
  ( cd "$G" && setsid nohup bash postman.sh "$MACH" \
      >> "$G/.postman_${MACH}.err" 2>&1 < /dev/null & )
fi
sleep 3
alive && say "postman 기동 확인" || { say "!! postman 기동 실패 — .postman_${MACH}.err 를 보십시오"; exit 1; }
