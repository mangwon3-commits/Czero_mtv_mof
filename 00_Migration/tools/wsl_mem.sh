#!/bin/bash
# WSL 메모리 상한을 20GB <-> 24GB 로 바꾼다.
#
# [언제 쓰나]
#   ASE 구조 감사(`audit_orphans.py` 계열)를 **여러 구조에 대해 한 프로세스에서**
#   돌릴 때만. get_all_distances(mic=True) 가 skew 큰 삼사정계 셀의 주기 이미지를
#   대량 전개하고, 구조를 연달아 감사하면 누적돼 14.4 GB 까지 갔던 전례가 있다.
#
#   **RASPA 계산에는 필요 없다.** 2026-08-07 실측으로 10프로세스가 5.0 GB,
#   20 GB 중 6.2 GB 사용, 스왑 0 MB 였다. 병목은 물리 코어 8개다.
#
# [비용]
#   적용하려면 윈도우에서 `wsl --shutdown` 을 해야 하고, **도는 계산이 전부 죽는다.**
#   그래서 이 스크립트는 긴 작업이 돌고 있으면 거부한다.
#
# [더 나은 길]
#   감사 루프를 구조마다 별도 프로세스로 쪼개면 메모리가 그때그때 반환돼
#   이 조정 자체가 필요 없어진다. 증설은 임시방편이다.
#
# 사용법:
#   bash wsl_mem.sh status
#   bash wsl_mem.sh 24        # 감사 전
#   bash wsl_mem.sh 20        # 감사 후 되돌리기
#   bash wsl_mem.sh 24 --force
set -u
CFG=/mnt/c/Users/mangw/.wslconfig
CMD=${1:-status}
FORCE=${2:-}

cur() { grep -oP '^memory=\K[0-9]+' "$CFG" 2>/dev/null; }

busy_report() {
  local s l p n
  s=$(pgrep -c simulate 2>/dev/null); case "$s" in ''|*[!0-9]*) s=0;; esac
  l=$(pgrep -c lmp_serial 2>/dev/null); case "$l" in ''|*[!0-9]*) l=0;; esac
  p=$(pgrep -cf 'python run_' 2>/dev/null); case "$p" in ''|*[!0-9]*) p=0;; esac
  n=$((s + l))
  echo "  simulate $s / lmp_serial $l / 실행 스크립트 $p"
  echo "$n"
}

if [ "$CMD" = "status" ]; then
  echo "=== 현재 설정 ==="
  echo "  memory=$(cur)GB (적용값: $(free -g | awk 'NR==2{print $2}')GB)"
  echo "  사용 $(free -g | awk 'NR==2{print $3}')GB / 가용 $(free -g | awk 'NR==2{print $7}')GB / 스왑사용 $(free -m | awk 'NR==3{print $3}')MB"
  echo "=== 실행 중 ==="
  busy_report | head -1
  echo
  echo "  적용된 값과 설정값이 다르면 wsl --shutdown 이 아직 안 된 것입니다."
  exit 0
fi

case "$CMD" in
  20|24) ;;
  *) echo "사용법: bash wsl_mem.sh [status|20|24] [--force]"; exit 1;;
esac

if [ "$(cur)" = "$CMD" ]; then
  echo "이미 memory=${CMD}GB 입니다."
  exit 0
fi

echo "=== 안전 점검 ==="
out=$(busy_report); echo "$out" | head -1
n=$(echo "$out" | tail -1)
if [ "$n" -gt 0 ] && [ "$FORCE" != "--force" ]; then
  echo
  echo "!! 계산 $n개가 돌고 있습니다. wsl --shutdown 은 이것들을 전부 죽입니다."
  echo "   RASPA 작업은 CrashRestart 로 분자 배치는 살아남지만 생산 사이클은 다시 돕니다."
  echo "   그래도 진행하려면: bash wsl_mem.sh $CMD --force"
  exit 1
fi

cp "$CFG" "${CFG}.bak"
sed -i "s/^memory=[0-9]*GB/memory=${CMD}GB/" "$CFG"
echo
echo "=== 변경됨 ==="
grep -n "^memory=" "$CFG" | sed 's/^/  /'
# 비ASCII 가 섞이면 WSL 이 파일을 통째로 무시한다(실제 사례).
if LC_ALL=C grep -qP '[^\x00-\x7F]' "$CFG"; then
  echo "  !! 비ASCII 문자 발견 — WSL 이 이 파일을 무시합니다. 되돌립니다."
  mv "${CFG}.bak" "$CFG"; exit 1
fi
echo "  ASCII 검사 통과"
echo
echo "=== 적용하려면 윈도우 PowerShell 에서 ==="
echo "    wsl --shutdown"
echo "  그 뒤 아무 WSL 명령이나 실행하면 새 값으로 다시 뜹니다."
echo "  확인: bash wsl_mem.sh status"
exit 0
