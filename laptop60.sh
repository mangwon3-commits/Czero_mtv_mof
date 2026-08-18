#!/bin/bash
# 랩탑 60시간 무인 운전 — 2026-08-19 ~ 08-21 18:00
#
# 랩탑은 08-19 02:00 에 안정성 관문 v3 를 닫고(28/31) 비었습니다. 남은 60시간의
# 주 산출물은 **조성 격자**입니다. 구조 네 종은 08-19 아침에 데스크탑에서
# **사람이 붙어 있을 때** 만들어 검사까지 마치고 저장소에 올렸습니다
# (커밋 ecc4f42). 이 스크립트는 구조를 만들지 않습니다 — 검증된 러너만 돕니다.
#
# 단계
#   L0  사전비행    구문 + 힘장 + 디스크 + 메모리 + git pull
#   L1  이완        GFN-FF 셀 고정, 새 4종만 (기존 30종은 건너뜀)
#   L2  판정+전하   judge_relax_v3 -> charge_v3
#   L3  격자 GCMC   0.15 bar / 298 K / 15000 사이클, 규약 그대로
#   L4  안정성 v3   격자 4종 포함해 관문 재실행 (RASPA 가 멈춘 뒤에만)
#   L5  습윤 WC     saIm0625 의 ads / tsa / vsa
#   L6  포장        결과 노트 + 커밋
#
# 관문을 못 넘으면 다음으로 가지 않고 멈춰 서서 이유를 남깁니다.
# 절반 성공이 틀린 숫자 네 종보다 낫습니다.
#
# 실행:
#   setsid nohup bash ~/mof_project/laptop60.sh > /dev/null 2>&1 < /dev/null &
# 확인:
#   cat ~/.claude_work/laptop60.state ; tail -30 ~/.claude_work/laptop60.log

set -u
P=$HOME/mof_project
Z=$P/21_ZIF69_MTV
W=$HOME/.claude_work
CZ=$HOME/miniconda3/envs/czeromof/bin
LOG=$W/laptop60.log
STATE=$W/laptop60.state
NOTION=$W/notion_queue.md
export RASPA_DIR=$HOME/RASPA/simulations

# 사용자 복귀 2시간 전. 이 시각을 넘기면 새 무거운 단계를 시작하지 않습니다.
DEADLINE=$(date -d "2026-08-21 18:00" +%s 2>/dev/null || echo 99999999999)

GRID="saIm0583 saIm0625 saIm0667 saIm0875"

mkdir -p "$W"
say()  { echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$LOG"; }
mark() { echo "$*" > "$STATE"; }

halt() {
  say "!! 중단: $*"
  mark "중단됨 ($(date '+%m-%d %H:%M')) — $*"
  { echo; echo "## [랩탑 중단] $(date '+%m-%d %H:%M')"; echo "$*"; } >> "$NOTION"
  exit 1
}

late() {   # $1 = 단계 이름. 마감을 넘겼으면 0 을 돌려준다.
  [ "$(date +%s)" -ge "$DEADLINE" ] && {
    say "  마감(08-21 18:00) 을 넘겨 $1 을 시작하지 않습니다."
    return 0; }
  return 1
}

commit() {   # $1 제목, $2 본문파일, 나머지 경로
  local t="$1" b="$2"; shift 2
  cd "$P" || return 1
  git add "$@" 2>/dev/null
  git diff --cached --quiet && { say "  커밋할 변경 없음 ($t)"; return 0; }
  { echo "$t"; echo; cat "$b"; echo;
    echo "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"; } > "$W/_l60.txt"
  git commit -F "$W/_l60.txt" --quiet && say "  커밋: $(git log --oneline -1)"
  # 데스크탑도 같은 가지에 밀고 있습니다. 갈리면 rebase 로 얹고, 그래도 안 되면
  # 보류합니다 — 무인 상태에서 강제로 밀지 않습니다.
  git push origin master --quiet 2>/dev/null && { say "  푸시 완료"; return 0; }
  git pull --rebase --quiet origin master 2>/dev/null \
    && git push origin master --quiet 2>/dev/null \
    && { say "  rebase 후 푸시 완료"; return 0; }
  say "  푸시 보류(원격 갈림 — 사람이 병합). 커밋은 남아 있습니다."
}

say "================ 랩탑 60시간 시작 ================"
mark "L0: 사전비행"

# ---------------------------------------------------------------- L0
say "=== L0. 사전비행 ==="
[ -d "$Z" ] || halt "작업 폴더 없음: $Z"
[ -x "$CZ/python" ] || halt "conda 환경 없음: $CZ/python"

cd "$P" || halt "저장소 없음"
git pull --ff-only origin master 2>&1 | tail -2 | while read -r l; do say "  $l"; done
say "  HEAD $(git log --oneline -1)"

cd "$Z" || halt "작업 폴더 없음"
for m in relax_series_v3 judge_relax_v3 charge_v3 run_gcmc_v3 \
         risk_screen_v3 risk_screen_v3_run run_humid_wc_v3grid; do
  "$CZ/python" -c "import ast;ast.parse(open('$m.py').read())" 2>/dev/null \
    || halt "$m.py 구문 오류 — 편집 후 재기동 때 터지는 그 경우입니다"
done
say "  러너 구문 확인 7종"

FF=$RASPA_DIR/share/raspa/forcefield/UFF_MOF/force_field_mixing_rules.def
[ -f "$FF" ] || halt "힘장 파일 없음: $FF (RASPA_DIR 확인)"
grep -q "C_co2 *lennard-jones *29.933 *2.745" "$FF" \
  || halt "힘장이 다릅니다. C_co2 가 29.933/2.745 가 아닙니다"
say "  힘장 확인 (Garcia-Sanchez 2009)"

# 격자 구조 네 종이 실제로 받아졌는지. 없으면 아무것도 할 수 없습니다.
NS=0
for t in $GRID; do [ -f "$Z/structures_v2/ZIF69_$t.cif" ] && NS=$((NS+1)); done
[ "$NS" -eq 4 ] || halt "격자 구조가 $NS/4 종만 있습니다. git pull 을 확인하세요."
say "  격자 구조 4종 확인 ($GRID)"

FREE=$(df -BG "$HOME" | awk 'NR==2{gsub("G","",$4); print $4}')
say "  디스크 여유 ${FREE} GB"
[ "${FREE:-0}" -lt 10 ] && halt "디스크 여유 ${FREE} GB. 새 계산을 띄우지 않습니다."

AVAIL=$(awk '/MemAvailable/{printf "%d", $2/1048576}' /proc/meminfo)
CORES=$(nproc)
say "  가용 메모리 ${AVAIL} GB, 논리 코어 ${CORES}"
[ "${AVAIL:-0}" -lt 6 ] && halt "가용 메모리 ${AVAIL} GB. 08-18 OOM 을 되풀이하지 않습니다."

# RASPA 워커는 코어에서, Zeo++ 워커는 메모리에서. 숫자를 문서에서 베끼지 않습니다.
GW=$(( CORES / 2 )); [ "$GW" -lt 2 ] && GW=2; [ "$GW" -gt 6 ] && GW=6
say "  GCMC 워커 $GW (RASPA 약 0.5 GB/건이라 코어가 병목)"

# ---------------------------------------------------------------- L1
mark "L1: 이완 (GFN-FF, 격자 4종)"
say "=== L1. 이완 — 격자 4종 ==="
say "  relax_series_v3.py 는 결과 CIF 가 있으면 건너뜁니다. 기존 30종은 안 돕니다."
# 글로브를 쓰지 않습니다. ZIF69_saIm0* 는 기존 saIm025 / saIm050 / saIm075 도
# 잡아서 "이미 다 됐다" 로 읽힙니다. 격자 태그만 이름으로 셉니다.
nrelaxed() {
  local n=0 t
  for t in $GRID; do
    [ -f "$Z/relax_v3/ZIF69_${t}_relaxed.cif" ] && n=$((n+1))
  done
  echo "$n"
}
if [ "$(nrelaxed)" -ge 4 ]; then
  say "  이미 격자 4종 이완 완료. 건너뜁니다."
else
  # relax_v3_results.json 은 이번 실행이 통째로 다시 씁니다(기존 30종은
  # skipped 로만 남습니다). 판정의 근거는 judge_relax_v3 가 만드는
  # relax_v3_judged.json 이므로 결론은 바뀌지 않지만, 원본 소요시간을
  # 잃지 않게 한 벌 보관합니다.
  [ -f "$Z/relax_v3_results.json" ] && \
    cp -n "$Z/relax_v3_results.json" "$Z/relax_v3_results.30only.json" 2>/dev/null
  cd "$Z" || halt "폴더 없음"
  nice -n 10 "$CZ/python" -u relax_series_v3.py >> "$LOG" 2>&1
  rc=$?
  say "  이완 종료 (rc=$rc)"
  N=$(nrelaxed)
  [ "$N" -ge 4 ] || halt "격자 이완 결과가 $N/4 종입니다. 로그를 보세요."
fi

# ---------------------------------------------------------------- L2
mark "L2: 판정 + 전하"
say "=== L2. 이완 판정 -> PACMAN 전하 ==="
cd "$Z" || halt "폴더 없음"
"$CZ/python" -u judge_relax_v3.py >> "$LOG" 2>&1 || halt "judge_relax_v3 실패"
say "  판정 완료 -> relax_v3_judged.json"

# 판정을 통과하지 못한 격자 구조는 여기서 걸립니다. 전하는 깨진 구조에도
# 숫자를 뱉으므로 이 관문이 없으면 GCMC 까지 흘러갑니다(08-14).
# 태그를 인자로 넘깁니다. 접두어 + 길이로 거르면 ZIF69_saIm025(13자)도
# 격자로 오인합니다 — 이름 규칙으로 짐작하지 않고 목록을 그대로 씁니다.
BADG=$(Z="$Z" "$CZ/python" - $GRID <<'PY'
import json, os, sys
want = {"ZIF69_" + t for t in sys.argv[1:]}
j = json.load(open(os.path.join(os.environ["Z"], "relax_v3_judged.json"),
                   encoding="utf-8"))
print(" ".join(r["name"] for r in j["rows"]
               if r["name"] in want and not r.get("pass")))
PY
)
[ -n "$BADG" ] && say "  !! 이완 판정 미달: $BADG (전하·GCMC 로 보내지 않습니다)"

"$CZ/python" -u charge_v3.py >> "$LOG" 2>&1 || halt "charge_v3 실패"
NC=0
for t in $GRID; do [ -f "$Z/charged_v3/${t}_DDEC6.cif" ] && NC=$((NC+1)); done
say "  전하 완료 — 격자 $NC/4 종"
[ "$NC" -ge 1 ] || halt "격자 전하 파일이 하나도 없습니다."

{ echo "구조는 08-19 아침 데스크탑에서 사람이 붙어 만들었고(ecc4f42), 랩탑은"
  echo "검증된 러너만 돌렸습니다. 이완 -> 판정 -> PACMAN 전하까지 통과."
  echo "격자 $NC/4 종이 charged_v3 에 들어왔습니다."
  [ -n "$BADG" ] && echo "이완 판정 미달: $BADG"; } > "$W/_l60b.txt"
commit "Relax and charge the four grid compositions" "$W/_l60b.txt" \
  21_ZIF69_MTV/relax_v3_judged.json 21_ZIF69_MTV/charged_v3.json

# ---------------------------------------------------------------- L3
mark "L3: 격자 GCMC"
say "=== L3. 격자 GCMC (0.15 bar, 298 K, 15000 사이클) ==="
if late "L3"; then :; else
  cd "$Z" || halt "폴더 없음"
  # 규약은 한 글자도 바꾸지 않습니다. 바뀐 것은 입력 구조뿐이어야
  # v3 의 30종과 같은 표에 놓을 수 있습니다.
  V3_WORKERS=$GW nice -n 10 "$CZ/python" -u run_gcmc_v3.py \
    --only $GRID --out results_v3grid.json >> "$LOG" 2>&1 \
    || halt "격자 GCMC 실패 — 로그를 보세요"
  say "  격자 GCMC 완료 -> results_v3grid.json"
  { echo "saIm 치환율 격자를 12.5% 간격으로 채웠습니다."
    echo "v3 에서 목표대(30~40 kJ/mol)에 든 것은 saIm075(31.42)와"
    echo "saIm100(34.01) 뿐이고 둘 다 08-19 안정성 관문에서 탈락했습니다."
    echo "통과한 마지막 조성은 saIm050(29.51, 문턱 밑)입니다."
    echo "흡착이 문턱을 넘는 지점과 구조가 무너지는 지점이 같은 구간에 있어,"
    echo "이 네 종이 그 구간을 가릅니다."
    echo
    echo "규약은 v3 30종과 동일합니다 — 0.15 bar, 298 K, 15000 사이클,"
    echo "UFF_MOF, DDEC6. 바뀐 것은 입력 구조뿐입니다."; } > "$W/_l60b.txt"
  commit "Fill the gap where the target band opens" "$W/_l60b.txt" \
    21_ZIF69_MTV/results_v3grid.json
fi

# ---------------------------------------------------------------- L4
mark "L4: 안정성 관문 (격자 포함)"
say "=== L4. 안정성 관문 v3 — 격자 4종 포함 ==="
if late "L4"; then :; else
  cd "$Z" || halt "폴더 없음"
  # risk_screen_v3 는 RASPA 가 돌고 있으면 스스로 2 를 돌려주고 멈춥니다.
  # L3 가 끝난 뒤라 비어 있어야 정상입니다.
  NS=$(pgrep -x simulate | wc -l)
  if [ "$NS" -gt 0 ]; then
    say "  !! RASPA $NS 건이 아직 돕니다. 30분 간격으로 최대 4시간 기다립니다."
    for _ in 1 2 3 4 5 6 7 8; do
      sleep 1800
      NS=$(pgrep -x simulate | wc -l); [ "$NS" -eq 0 ] && break
    done
  fi
  if [ "$NS" -gt 0 ]; then
    say "  RASPA 가 계속 돕니다. 안정성 관문을 건너뛰고 L5 로 갑니다."
  else
    # 워커는 주지 않습니다. risk_screen_v3 가 /proc/meminfo 에서 계산합니다
    # (Zeo++ 는 랩탑 실측 9.5 GB/건. 문서의 3.2 는 v1 구조의 옛 값이었습니다).
    nice -n 10 "$CZ/python" -u risk_screen_v3_run.py >> "$LOG" 2>&1
    say "  안정성 관문 종료 (rc=$?)"
    { echo "격자 4종을 넣어 관문을 다시 닫았습니다."
      echo "판정은 사전 등록된 그대로입니다 — PLD > 3.3 / LCD 감소 < 20% /"
      echo "AV > 20 A^3 / 최소거리 > 0.7 A. 통과한 것들 사이의 순위는"
      echo "여기서 매기지 않습니다."; } > "$W/_l60b.txt"
    commit "Re-close the stability gate with the grid inside it" "$W/_l60b.txt" \
      21_ZIF69_MTV/risk_results_v3.json 21_ZIF69_MTV/risk_v3_index.json
  fi
fi

# ---------------------------------------------------------------- L5
mark "L5: 습윤 작업 용량 (saIm0625)"
say "=== L5. 습윤 작업 용량 — saIm0625 ==="
if late "L5"; then :; else
  cd "$Z" || halt "폴더 없음"
  if [ -f "$Z/charged_v3/saIm0625_DDEC6.cif" ]; then
    HWC_V3G_WORKERS=3 nice -n 10 "$CZ/python" -u run_humid_wc_v3grid.py \
      >> "$LOG" 2>&1 && say "  습윤 WC 완료" || say "  !! 습윤 WC 실패 — 로그 확인"
    { echo "데스크탑이 base / saIm050 / saIm075 / saIm100 을 했습니다."
      echo "62.5% 는 그 표의 빠진 칸이고, 안정성 판정이 어느 쪽으로 나오든"
      echo "쓸 수 있는 창이 어디서 닫히는지 말하려면 이 수치가 필요합니다."
      echo "결과 파일과 작업 폴더를 데스크탑과 분리했습니다 — 같은 이름을 쓰면"
      echo "이어받기가 상대 작업을 '이미 됐다' 로 읽습니다."; } > "$W/_l60b.txt"
    commit "Measure the humid working capacity at the boundary composition" \
      "$W/_l60b.txt" 21_ZIF69_MTV/v3_humid_wc/humid_working_capacity_grid.json
  else
    say "  saIm0625 전하 파일이 없어 건너뜁니다."
  fi
fi

# ---------------------------------------------------------------- L6
mark "L6: 포장"
say "=== L6. 포장 ==="
{ echo "랩탑 60시간 창을 닫습니다."
  echo
  echo "격자 GCMC   $([ -f "$Z/results_v3grid.json" ] && echo 완료 || echo 없음)"
  echo "안정성 v3   $([ -f "$Z/risk_results_v3.json" ] && echo 완료 || echo 없음)"
  echo "습윤 WC     $([ -f "$Z/v3_humid_wc/humid_working_capacity_grid.json" ] \
        && echo 완료 || echo 없음)"
  echo
  echo "구조 생성은 이 창에서 하지 않았습니다. 네 종 전부 08-19 아침에"
  echo "사람이 붙어 있을 때 만들어 검사를 마친 것입니다(ecc4f42)."; } \
  > "$W/_l60b.txt"
commit "Close the laptop window with what actually landed" "$W/_l60b.txt" \
  21_ZIF69_MTV/results_v3grid.json 21_ZIF69_MTV/risk_results_v3.json \
  21_ZIF69_MTV/v3_humid_wc

mark "완료 ($(date '+%m-%d %H:%M'))"
say "================ 랩탑 60시간 끝 ================"
exit 0
