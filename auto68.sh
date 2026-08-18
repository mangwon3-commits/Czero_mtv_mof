#!/bin/bash
# 68시간 무인 운전 — 2026-08-19 00:10 ~ 08-21 20:00 (사용자 여행 복귀)
#
# AUTOMATION_60H.md 의 설계를 이 창에 맞게 구현한 것입니다. 중심은 처리량이
# 아니라 **관문**입니다. 무인 시간이 길수록 잘못된 규약으로 그만큼을 쌓을 수
# 있고, 이 프로젝트가 11일에 근본 결함 4건을 낸 이유가 전부 그것이었습니다.
#
# 단계
#   S1  습윤 작업 용량 v3 완주 대기 -> 수확 -> 커밋
#   S2  증거표 -- 지금까지의 v3 를 한 표로 (계산 아님)
#   S3  조성 격자 세분 62.5 / 87.5%  <- 이 창의 주 산출물
#         빌드 -> 검사 -> PACMAN -> 연기시험 -> 전체 GCMC
#   S4  최종 포장 -- 결과 노트, 커밋, 노션 대기열
#
# 관문을 못 넘으면 **다음으로 가지 않고 멈춰 서서 이유를 남깁니다.**
# 절반 성공이 틀린 숫자 30종보다 낫습니다.

set -u
P=/home/mangwon1/mof_project
Z=$P/21_ZIF69_MTV
W=/home/mangwon1/.claude_work
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin
LOG=$W/auto68.log
STATE=$W/auto68.state
NOTION=$W/notion_queue.md
export RASPA_DIR=/home/mangwon1/RASPA/simulations

say()  { echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$LOG"; }
mark() { echo "$*" > "$STATE"; }

halt() {
  say "!! 중단: $*"
  mark "중단됨 ($(date '+%m-%d %H:%M')) — $*"
  { echo; echo "## [중단] $(date '+%m-%d %H:%M')"; echo "$*"; } >> "$NOTION"
  exit 1
}

disk_guard() {
  local free
  free=$(df -BM /mnt/c 2>/dev/null | awk 'NR==2{gsub("M","",$4); print $4}')
  [ -z "$free" ] && return 0
  say "  C: 여유 ${free} MB"
  [ "$free" -lt 2000 ] && halt "C: 여유 ${free} MB. 새 계산을 띄우지 않습니다."
  return 0
}

commit() {   # $1 제목, $2 본문파일, 나머지 경로
  local t="$1" b="$2"; shift 2
  cd "$P" || return 1
  git add "$@" 2>/dev/null
  git diff --cached --quiet && { say "  커밋할 변경 없음 ($t)"; return 0; }
  { echo "$t"; echo; cat "$b"; echo;
    echo "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"; } > "$W/_a68.txt"
  git commit -F "$W/_a68.txt" --quiet && say "  커밋: $(git log --oneline -1)"
  git push origin master --quiet 2>/dev/null && say "  푸시 완료" || say "  푸시 보류(원격 갈림 — 사람이 병합)"
}

say "================ 68시간 파이프라인 시작 ================"
mark "S0: 사전비행"

# ---------------------------------------------------------------- S0
say "=== S0. 사전비행 ==="
cd "$Z" || halt "작업 폴더 없음"
for m in run_humid_wc_v3 run_gcmc_v3 run_wc_v3 rebuild_structures charge_v3; do
  "$CZ/python" -c "import ast,sys;ast.parse(open('$m.py').read())" 2>/dev/null \
    || halt "$m.py 구문 오류 — 편집 후 재기동 때 터지는 그 경우입니다"
done
say "  러너 구문 확인"
FF=$RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
grep -q "C_co2 *lennard-jones *29.933 *2.745" "$FF" \
  || halt "힘장이 다릅니다. C_co2 가 29.933/2.745 가 아닙니다"
say "  힘장 확인 (Garcia-Sanchez)"
disk_guard

# ---------------------------------------------------------------- S1
mark "S1: 습윤 작업 용량 v3"
say "=== S1. 습윤 작업 용량 v3 ==="
t0=$(date +%s); end=$((t0 + 10*3600))
while [ "$(date +%s)" -lt "$end" ]; do
  pgrep -f run_humid_wc_v3.py > /dev/null 2>&1 || break
  sleep 300
done
sleep 60
if [ -f "$Z/v3_humid_wc/humid_working_capacity.json" ]; then
  n=$("$CZ/python" -c "
import json;d=json.load(open('$Z/v3_humid_wc/humid_working_capacity.json'))
r=d.get('rows',d) if isinstance(d,dict) else d;print(len(r))" 2>/dev/null || echo 0)
  say "  결과 $n 종"
  { echo "습윤 조건에서 흡착-재생을 한 사이클 돌려 실제 회수량을 냈습니다($n 종)."
    echo "TSA 는 승온으로 포화증기압이 올라 RH 가 90 -> 2.8% 로 떨어집니다."
    echo "온도만 올려도 물이 스스로 빠지는지, 아니면 자리를 계속 차지하는지가"
    echo "이 배치의 질문이었습니다."; } > "$W/_a68b.txt"
  commit "Wet regeneration, measured rather than assumed" "$W/_a68b.txt" \
    21_ZIF69_MTV/v3_humid_wc
  echo "- 습윤 작업 용량 v3 $n 종 완료 — 노션 Part 3" >> "$NOTION"
else
  say "  !! 결과 JSON 없음. 이어서 진행하되 노션에 남깁니다."
  echo "- ⚠️ 습윤 WC v3 결과 없음 — 확인 필요" >> "$NOTION"
fi

# ---------------------------------------------------------------- S2
mark "S2: 증거표"
say "=== S2. 증거표 ==="
"$CZ/python" "$P/tools/v3report.py" > "$W/evidence_v3.txt" 2>&1 || true
"$CZ/python" "$P/tools/wc32.py" >> "$W/evidence_v3.txt" 2>&1 || true
cp "$W/evidence_v3.txt" "$Z/EVIDENCE_V3.txt" 2>/dev/null
{ echo "지금까지 확정된 v3 를 한 자리에 모았습니다. 계산이 아니라 집계입니다."
  echo "1.5시그마 미만 차이에는 순위를 매기지 않는다는 규율을 그대로 적용합니다."; } \
  > "$W/_a68b.txt"
commit "Put every accepted v3 number in one place" "$W/_a68b.txt" \
  21_ZIF69_MTV/EVIDENCE_V3.txt

# ---------------------------------------------------------------- S3
mark "S3: 조성 격자 세분 62.5 / 87.5%"
say "=== S3. 조성 격자 세분 ==="
disk_guard
say "  왜: v3 에서 saIm075(31.42) 와 saIm100(34.01) 사이가 비어 있습니다."
say "      목표대(30~40) 진입 지점을 짚으려면 그 사이가 필요합니다."

# [무인 운전은 구조를 만들지 않습니다 -- 08-19 00:20 에 실제로 사고날 뻔했습니다]
#
#   rebuild_structures.py 에는 argparse 가 없습니다. --help 를 줘도 무시하고
#   **즉시 전체 재빌드를 시작해 structures_v2/ 를 덮어씁니다.** 확인하려고
#   부른 명령이 생산 데이터를 건드렸습니다. 다행히 빌더가 고정 시드라
#   바이트가 같아 피해가 없었지만, 무인 상태였다면 그 사실조차 몰랐을 것입니다.
#
#   그리고 구조 생성은 검사 항목이 다릅니다 -- 충돌·고아 원자·조성 개수의
#   정확성이고, 08-14 결함이 정확히 그 자리에서 났습니다. 무인 창에서 새 구조를
#   만들지 않습니다.
#
#   대신 **사람이 미리 만들어 둔 격자 구조가 있으면** 그 위에서 검증된 러너로
#   GCMC 만 돕니다. 없으면 조용히 건너뜁니다 -- 없는 숫자를 만들지 않습니다.
GRID="$Z/charged_v3grid"
NG=$(ls "$GRID"/*_DDEC6.cif 2>/dev/null | wc -l)
if [ "$NG" -ge 2 ]; then
  say "  격자 구조 $NG 종 발견 -- 검증된 러너로 GCMC 만 돕니다"
  cd "$Z" || halt "폴더 없음"
  if V3_WORKERS=7 "$CZ/python" run_gcmc_v3.py --out results_v3grid.json >> "$LOG" 2>&1; then
    echo "saIm075(31.42) 와 saIm100(34.01) 사이를 12.5% 간격으로 채웠습니다." > "$W/_a68b.txt"
    commit "Fill the gap where the target band opens" "$W/_a68b.txt" 21_ZIF69_MTV/results_v3grid.json
    echo "- 조성 격자 GCMC 완료" >> "$NOTION"
  else
    say "  !! 격자 GCMC 실패 -- 로그 확인"
  fi
else
  say "  격자 구조가 없습니다($NG 종). 건너뜁니다 -- 없는 숫자를 만들지 않습니다."
  say "  사람이 charged_v3grid/ 를 만들어 두면 다음 실행에서 자동으로 집습니다."
  echo "- S3 조성 격자: 구조 생성은 사람이 붙어 있을 때만. 지금은 건너뜀" >> "$NOTION"
fi

# ---------------------------------------------------------------- S4
mark "S4: 포장"
say "=== S4. 포장 ==="
{ echo "68시간 창의 결과를 정리했습니다."
  echo "완료: $(ls $Z/v3_humid_wc/*.json 2>/dev/null | wc -l) 습윤 WC, 증거표."
  echo "S3 조성 격자는 빌더 인자 확인이 필요하면 건너뜁니다 -- 무인 운전에서"
  echo "구조 생성은 검사 항목이 다르고(충돌·고아 원자·조성 개수), 08-14 결함이"
  echo "정확히 그 자리에서 났기 때문입니다."; } > "$W/_a68b.txt"
commit "Close the 68-hour window with what actually landed" "$W/_a68b.txt" \
  21_ZIF69_MTV/EVIDENCE_V3.txt 21_ZIF69_MTV/v3_humid_wc

mark "완료 ($(date '+%m-%d %H:%M'))"
say "================ 68시간 파이프라인 끝 ================"
exit 0
