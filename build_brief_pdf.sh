#!/bin/sh
# 전달용 브리핑을 PDF 로 굽는다.
#
# [왜 스크립트로 두나]
#     LINKER_DESIGN_BRIEF.md 는 프로젝트 밖 사람에게 건네는 문서라 내용이 바뀔
#     때마다 다시 구워야 한다. 명령을 기억에 의존하면 폰트 옵션이 빠진 채로
#     구워져 한글이 통째로 깨진 PDF 가 나간다.
#
# [폰트]
#     WSL 리눅스 쪽에는 CJK 폰트가 하나도 등록돼 있지 않다. 윈도우의 Malgun Gothic
#     을 ~/.local/share/fonts 에 심볼릭 링크로 걸고 fc-cache 로 등록해서 쓴다:
#         ln -sf /mnt/c/Windows/Fonts/malgun.ttf   ~/.local/share/fonts/
#         ln -sf /mnt/c/Windows/Fonts/malgunbd.ttf ~/.local/share/fonts/
#         fc-cache -f
#
# [엔진]
#     pandoc + typst. LaTeX 를 쓰지 않는 이유는 CJK 조판에 xelatex + 폰트 설정이
#     추가로 필요하고 설치가 훨씬 무겁기 때문이다. typst 는 단일 바이너리이고
#     fontconfig 에 등록된 폰트를 그대로 본다.
#
#     conda create -n docs -c conda-forge pandoc typst
set -e

BIN="$HOME/miniconda3/envs/docs/bin"
# pandoc 은 --pdf-engine 을 **PATH 에서** 찾는다. 환경을 activate 하지 않고
# 절대경로로 부르면 "'typst' not found" 로 죽는다.
PATH="$BIN:$PATH"
export PATH
SRC="${1:-$(dirname "$0")/LINKER_DESIGN_BRIEF.md}"
OUT="${2:-${SRC%.md}.pdf}"

# gfm: 표(pipe table)와 취소선(~~...~~)을 쓴다. tex_math_dollars: $...$ 두 군데.
"$BIN/pandoc" "$SRC" -o "$OUT" \
    -f gfm+tex_math_dollars \
    --pdf-engine=typst \
    --toc --toc-depth=2 \
    -V mainfont="Malgun Gothic" \
    -V monofont="Malgun Gothic" \
    -V fontsize=9pt \
    -V margin-x=1.8cm \
    -V margin-y=1.8cm \
    -M title="새 링커 설계 브리핑" \
    -M date="$(date +%Y-%m-%d)"

echo "[OK] $OUT  ($(du -h "$OUT" | cut -f1))"
