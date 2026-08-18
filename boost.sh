#!/bin/bash
# 자원 현황과 안전한 여유분을 계산한다. /boost 슬래시 명령이 이것을 먼저 부른다.
#
# [왜 스크립트로 두는가]
#   자원 판단을 매번 즉흥으로 하다가 2026-08-12 에 WSL 을 통째로 먹통으로
#   만들었습니다. Zeo++ 를 RASPA 위에 얹어 OOM 이 나고 dbus-daemon 까지 죽어
#   **모든 셸 도구가 실패**했습니다(cwd 가 WSL UNC 경로라서). 사람이 밖에서
#   `wsl --shutdown` 을 해야 복구됐습니다.
#
#   그래서 한도를 코드에 박아 둡니다. 규칙은 전부 실측에서 나온 것입니다.
#
# [실측된 한도]
#   물리 8 코어 / 논리 16
#   RASPA simulate      약 471 MB/건   -> 메모리는 병목이 아님. 코어가 한도
#   Zeo++ network       약 3.2 GB/건   -> **RASPA 가 바쁠 때 절대 동시 실행 금지**
#   lmp_serial          약 1 GB/건
#   메모리 여유는 4 GB 이상 남긴다 (WSL 자체와 dbus 가 죽지 않게)
#
# 사용:
#   bash boost.sh            현황과 권고만 출력
#   bash boost.sh --json     기계가 읽을 형태로

PHYS=8
MEM_FLOOR_GB=4
RASPA_MB=471
ZEO_GB=3.2

n() { local c; c=$(pgrep -c "$1" 2>/dev/null); case "$c" in ''|*[!0-9]*) c=0;; esac; echo "$c"; }
nf() { local c; c=$(pgrep -cf "$1" 2>/dev/null); case "$c" in ''|*[!0-9]*) c=0;; esac; echo "$c"; }

SIM=$(n simulate)
LMP=$(n lmp_serial)
ZEO=$(nf 'network ')
NICED=$(ps -eo ni,comm --no-headers | awk '$2=="simulate" && $1>=10' | wc -l)
HOT=$((SIM - NICED))
AVAIL=$(free -g | awk 'NR==2{print $7}')
LOAD1=$(cut -d' ' -f1 /proc/loadavg)

# 여유 코어 = 물리 코어 - 우선순위 높은(nice<10) 작업 수
FREE=$((PHYS - HOT - LMP))
[ "$FREE" -lt 0 ] && FREE=0
# 메모리로도 한 번 자른다
MEM_ROOM=$(( (AVAIL - MEM_FLOOR_GB) * 1024 / RASPA_MB ))
[ "$MEM_ROOM" -lt 0 ] && MEM_ROOM=0
SAFE=$FREE
[ "$MEM_ROOM" -lt "$SAFE" ] && SAFE=$MEM_ROOM

ZEO_OK="아니오"
ZEO_WHY="RASPA/LAMMPS 가 돌고 있음 -- 08-12 OOM 조합"
if [ "$SIM" -eq 0 ] && [ "$LMP" -eq 0 ]; then
  ZEO_N=$(python3 -c "print(max(0,int(($AVAIL-$MEM_FLOOR_GB)/$ZEO_GB)))" 2>/dev/null || echo 0)
  [ "$ZEO_N" -gt "$PHYS" ] && ZEO_N=$PHYS
  if [ "$ZEO_N" -gt 0 ]; then ZEO_OK="예 (최대 ${ZEO_N}건)"; ZEO_WHY="계산이 유휴 상태"; fi
fi

if [ "$1" = "--json" ]; then
  printf '{"simulate":%s,"hot":%s,"niced":%s,"lmp":%s,"zeo":%s,"avail_gb":%s,' \
    "$SIM" "$HOT" "$NICED" "$LMP" "$ZEO" "$AVAIL"
  printf '"load1":%s,"free_cores":%s,"safe_new_nice0":%s,"zeo_allowed":"%s"}\n' \
    "$LOAD1" "$FREE" "$SAFE" "$ZEO_OK"
  exit 0
fi

echo "=== 지금 ==="
printf "  simulate %s (우선순위 높음 %s / nice 양보 %s)   lmp_serial %s   Zeo++ %s\n" \
  "$SIM" "$HOT" "$NICED" "$LMP" "$ZEO"
printf "  부하 %s   메모리 가용 %s GB   물리 코어 %s\n" \
  "$(cut -d' ' -f1-3 /proc/loadavg)" "$AVAIL" "$PHYS"
echo
echo "  --- 무엇이 도는가 ---"
for pid in $(pgrep -x simulate); do
  d=$(readlink /proc/$pid/cwd 2>/dev/null)
  ni=$(ps -o ni= -p $pid 2>/dev/null | tr -d ' ')
  printf "    nice %-3s %-9s %s\n" "$ni" \
    "$(ps -o etime= -p $pid 2>/dev/null | tr -d ' ')" \
    "$(basename "$(dirname "$d")")/$(basename "$d")"
done

echo
echo "=== 여유 ==="
printf "  새 작업을 **우선순위 0** 으로 몇 개까지: %s\n" "$SAFE"
printf "     (코어 기준 %s, 메모리 기준 %s 중 작은 값)\n" "$FREE" "$MEM_ROOM"
printf "  nice 19 로는: 사실상 제한 없음 -- 남는 CPU 만 받으므로 본 계산을 밀지 않습니다\n"
printf "               (C-H A/B 4건, 밀도맵 4건이 이 방식으로 방해 없이 완주)\n"
printf "  Zeo++ 를 지금 띄워도 되나: **%s**  (%s)\n" "$ZEO_OK" "$ZEO_WHY"

echo
echo "=== 규칙 ==="
cat <<'EOF'
  1. Zeo++(network)는 한 건에 3.2 GB. RASPA 가 돌 때 절대 같이 띄우지 마세요.
     2026-08-12 에 이 조합이 OOM 을 냈고 dbus-daemon 까지 죽어 WSL 배포판이
     통째로 먹통이 됐습니다. 밖에서 `wsl --shutdown` 을 해야 복구됐습니다.
  2. 부수적인 작업은 `nice -n 19` 로 띄우세요. 본 계산에 양보합니다.
  3. 메모리는 4 GB 이상 남기세요.
  4. 띄울 때는 `setsid nohup ... < /dev/null &` 로 완전히 분리하세요.
     그러지 않으면 세션이 끝날 때 같이 죽습니다.
  5. **돌고 있는 bash 스크립트를 편집하지 마세요.** bash 는 바이트 오프셋으로
     읽어서 엉뚱한 줄을 실행합니다. 고쳤으면 죽이고 다시 띄우세요.
  6. 다른 세션이 같은 트리를 씁니다. 띄우기 전에 SESSION_LOG.md 를 보고,
     띄운 뒤에는 적어 두세요.
EOF
exit 0
