#!/bin/bash
# 12시간 무인 운전 — v3 파이프라인을 끝까지 잇는다.
#
# [설계 원칙: 조용한 실패가 최악이다]
#   이 프로젝트에서 반복된 사고 유형은 **실패가 결과처럼 보이는 것**입니다.
#   무인으로 12시간을 돌리면 그 위험이 가장 큽니다. 그래서 단계마다 관문을 두고,
#   관문을 못 넘으면 **다음 단계로 가지 않고 멈춰 서서 이유를 남깁니다.**
#   절반 성공한 상태로 끝나는 편이, 틀린 숫자가 30종어치 쌓이는 것보다 낫습니다.
#
# [단계]
#   A  진행 중인 이완 30종이 끝나기를 기다린다
#   B  판정(judge_relax_v3) -> 통과 30종이어야 진행. 커밋
#   C  수분 v2 마지막 1건이 끝나기를 기다린다. 결과 JSON 확인 후 커밋
#   D  정리 — 수확 끝난 실행 폴더 삭제(약 6.6 GB). vhdx 가 더 안 자라게
#   E  전하(charge_v3) — 이완된 기하 위에서 PACMAN 다시. 커밋
#   F  **연기 시험** — 모체 1종만 GCMC. Q_st 가 말이 되는 값인지 본다
#   G  전체 GCMC v3 (30종 x 3 = 90작업). 커밋
#
# [디스크 감시]
#   C: 가 마르면 ext4 가 깨질 수 있습니다(08-12 먹통과 같은 계열). 무거운
#   단계를 띄우기 전마다 재고, 1.5 GB 미만이면 **띄우지 않고 멈춥니다.**
#
# [노션]
#   셸에서는 못 합니다. 단계마다 NOTION_QUEUE 에 무엇을 반영해야 하는지 적어
#   두고, 사람(또는 클로드)이 다음에 붙었을 때 그것을 읽고 올립니다.

set -u
P=/home/mangwon1/mof_project/21_ZIF69_MTV
R=/home/mangwon1/mof_project
W=/home/mangwon1/.claude_work
CZ=/home/mangwon1/miniconda3/envs/czeromof/bin
CT=/home/mangwon1/miniconda3/envs/coremof_tools/bin
LOG=$W/overnight.log
STATE=$W/overnight.state
NOTION=$W/notion_queue.md
export RASPA_DIR=/home/mangwon1/RASPA/simulations

say() { echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$LOG"; }
mark() { echo "$*" > "$STATE"; }

halt() {   # 관문을 못 넘었을 때. 다음 단계로 가지 않는다.
  say "!! 중단: $*"
  mark "중단됨 ($(date '+%m-%d %H:%M')) — $*"
  {
    echo
    echo "## [중단] $(date '+%m-%d %H:%M')"
    echo "$*"
    echo "로그: $LOG"
  } >> "$NOTION"
  exit 1
}

disk_guard() {
  local free
  free=$(df -BM /mnt/c 2>/dev/null | awk 'NR==2{gsub("M","",$4); print $4}')
  [ -z "$free" ] && return 0
  say "  C: 여유 ${free} MB"
  [ "$free" -lt 1500 ] && halt "C: 여유가 ${free} MB. 무거운 단계를 띄우지 않습니다."
  return 0
}

wait_gone() {   # $1 = pgrep 패턴, $2 = 설명, $3 = 최대 시간(초)
  local t0 end
  t0=$(date +%s); end=$((t0 + $3))
  say "  기다림: $2"
  while [ "$(date +%s)" -lt "$end" ]; do
    if ! pgrep -f "$1" > /dev/null 2>&1; then
      say "  끝남: $2 ($(( ($(date +%s)-t0)/60 )) 분 기다림)"
      sleep 30       # 결과 파일이 떨어질 시간
      return 0
    fi
    sleep 120
  done
  halt "$2 이(가) $(($3/3600))시간 안에 안 끝났습니다."
}

commit() {   # $1 = 제목, $2 = 본문 파일, 나머지 = 경로들
  local title="$1" body="$2"; shift 2
  cd "$R" || return 1
  git add "$@" 2>/dev/null
  if git diff --cached --quiet; then
    say "  커밋할 변경 없음 ($title)"
    return 0
  fi
  { echo "$title"; echo; cat "$body"; echo;
    echo "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"; } > "$W/_ovn_msg.txt"
  git commit -F "$W/_ovn_msg.txt" --quiet && say "  커밋: $(git log --oneline -1)"
}

say "================ 밤샘 파이프라인 시작 ================"
mkdir -p "$(dirname "$NOTION")"
echo "# 노션 반영 대기열 — $(date '+%Y-%m-%d %H:%M') 시작" >> "$NOTION"

# ---------------------------------------------------------------- A
mark "A: 이완 30종 대기"
wait_gone "relax_series_v3.py" "v3 이완 30종" $((6*3600))

# ---------------------------------------------------------------- B
mark "B: 이완 판정"
say "=== B. 이완 판정 ==="
cd "$P" && "$CZ/python" judge_relax_v3.py 2>&1 | tee -a "$LOG"
n_ok=$("$CZ/python" -c "
import json;d=json.load(open('$P/relax_v3_judged.json'))
print(sum(1 for r in d['rows'] if r['pass']))" 2>/dev/null || echo 0)
n_all=$("$CZ/python" -c "
import json;print(json.load(open('$P/relax_v3_judged.json'))['n'])" 2>/dev/null || echo 0)
say "  판정 통과 $n_ok / $n_all"
[ "$n_all" -lt 30 ] && halt "이완이 30종을 못 채웠습니다($n_all)."
[ "$n_ok" -lt 25 ] && halt "판정 통과가 $n_ok 종뿐입니다. 사람이 봐야 합니다."

# 궤적 파일은 무겁습니다. 결과 CIF 와 판정만 올립니다.
grep -q '^21_ZIF69_MTV/relax_v3/\*/$' "$R/.gitignore" 2>/dev/null || \
  echo '21_ZIF69_MTV/relax_v3/*/' >> "$R/.gitignore"
{
  echo "이완 $n_all 종 중 $n_ok 종이 사전 등록 기준을 통과했습니다."
  echo "기준: C-H 1.05~1.12 / 방향족 C-C 폭 <0.08 / Zn-N 1.90~2.10 / 최소거리 >0.9 / 셀 고정"
  echo
  sed -n '/구조 /,/판정$/p' "$LOG" | tail -35
} > "$W/_ovn_body.txt"
commit "Relax all thirty, and let the criteria say so one structure at a time" \
  "$W/_ovn_body.txt" 21_ZIF69_MTV/relax_v3 21_ZIF69_MTV/relax_v3_judged.json .gitignore
echo "- v3 이완 $n_ok/$n_all 통과 — Part 0-D 7-2 와 SCHEDULE.md 갱신 필요" >> "$NOTION"

# ---------------------------------------------------------------- C
# [2026-08-16 재설계] 여기서 수분 v2 를 **기다리지 않습니다.**
#
#   원래는 wait_gone 으로 막아 두었습니다. 그런데 컴퓨터가 꺼지면서 마지막 1건
#   (rh90_saIm100)이 통째로 날아갔고, 처음부터 돌리면 22~26시간이 걸립니다.
#   v3 GCMC 는 수분 v2 에 **아무것도 의존하지 않습니다** -- 별개의 산출물입니다.
#   묶어 두면 v3 가 하루를 서서 기다립니다. 풀어 놓고 병렬로 갑니다.
#
#   수확은 맨 끝(H)에서 합니다. 그때까지 끝나 있으면 커밋하고, 아니면 다음 사람이
#   이어받습니다 -- run_water.py 는 작업 단위 이어받기가 있어서 완주분을 캐시로
#   회수합니다(2026-08-06 에 절전으로 같은 일을 겪고 넣은 장치).
mark "C: 수분 v2 는 병렬로 두고 진행"
say "=== C. 수분 v2 — 기다리지 않고 병렬 진행 ==="
if pgrep -f run_water_v2.py > /dev/null 2>&1; then
  say "  수분 v2 가 돌고 있습니다. 끝에서 수확합니다."
else
  say "  !! 수분 v2 가 돌고 있지 않습니다. 노션에 적어 둡니다."
  echo "- ⚠️ 수분 v2 미가동 — 재기동 필요" >> "$NOTION"
fi

# ---------------------------------------------------------------- D
mark "D: 정리"
say "=== D. 정리 (수확 끝난 실행 폴더) ==="
bash "$R/cleanup_for_compact.sh" --now 2>&1 | tee -a "$LOG"
say "  WSL 디스크: $(df -h / | awk 'NR==2{print $4" 여유"}')"
disk_guard

# ---------------------------------------------------------------- E
mark "E: 전하 v3"
say "=== E. 전하 (PACMAN DDEC6, 이완된 기하) ==="
cd "$P" && "$CT/python" charge_v3.py 2>&1 | tee -a "$LOG"
n_ch=$("$CZ/python" -c "
import json;print(len(json.load(open('$P/charged_v3.json'))['charged']))" 2>/dev/null || echo 0)
say "  전하 완료 $n_ch 종"
[ "$n_ch" -lt 25 ] && halt "전하가 $n_ch 종뿐입니다."
{
  echo "이완된 기하 위에서 PACMAN DDEC6 전하를 다시 계산했습니다($n_ch 종)."
  echo "전하는 기하의 함수이므로 v2 전하를 이완 구조에 재사용하면 짝이 맞지 않습니다."
  echo "감사(AUDIT_20260814.md)가 잰 K_H 4.7~6.8% 이동의 절반이 이 경로였습니다."
} > "$W/_ovn_body.txt"
commit "Recompute the charges on the geometry that actually moved" \
  "$W/_ovn_body.txt" 21_ZIF69_MTV/charged_v3 21_ZIF69_MTV/charged_v3.json \
  21_ZIF69_MTV/charge_v3.py 21_ZIF69_MTV/run_gcmc_v3.py
echo "- v3 전하 $n_ch 종 완료" >> "$NOTION"

# ---------------------------------------------------------------- E-2
# 지인에게 넘길 꾸러미. 사용자가 "그때 만들어 달라" 고 승인했습니다(08-17 00:0x).
# **전하가 생긴 직후가 유일하게 옳은 시점**입니다 -- 그 전에 만들면 전하 없는
# 구조가 나가서 상대가 GCMC 를 못 돌리고, 그 사실을 상대가 먼저 발견하게 됩니다.
# prepare_handoff.sh 자체에도 같은 관문이 있어 이중으로 막힙니다.
mark "E-2: 지인 전달 꾸러미"
say "=== E-2. 전달 꾸러미 (D 드라이브) ==="
if bash "$R/prepare_handoff.sh" --go 2>&1 | tee -a "$LOG"; then
  sz=$(du -sh /mnt/d/MTV-ZIF_계산지원 2>/dev/null | cut -f1)
  nf=$(find /mnt/d/MTV-ZIF_계산지원 -type f 2>/dev/null | wc -l)
  say "  꾸러미 완료 — ${sz}, 파일 ${nf}개"
  {
    echo "생성 $(date '+%m-%d %H:%M')"
    echo "위치 D:\\MTV-ZIF_계산지원"
    echo "크기 ${sz} / 파일 ${nf}개 / 전하 CIF ${n_ch}종"
  } > "$W/handoff_ready.flag"
  echo "- ✅ **지인 전달 꾸러미 생성 완료** (D:\\MTV-ZIF_계산지원, ${sz}, ${nf}개 파일)" \
    " — 사용자에게 **채팅으로 알릴 것**" >> "$NOTION"
else
  say "  !! 꾸러미 생성 실패"
  echo "실패 $(date '+%m-%d %H:%M') — overnight.log 확인" > "$W/handoff_failed.flag"
  echo "- ⚠️ 전달 꾸러미 생성 실패 — 사용자에게 알릴 것" >> "$NOTION"
fi

# ---------------------------------------------------------------- F
mark "F: 연기 시험 (모체 1종)"
say "=== F. 연기 시험 — 모체 1종만 돌려 본다 ==="
disk_guard
cd "$P" && V3_WORKERS=3 "$CZ/python" run_gcmc_v3.py --only base \
  --out results_v3_smoke.json 2>&1 | tee -a "$LOG"
verdict=$("$CZ/python" - <<'EOF' 2>/dev/null || echo FAIL
import json
d = json.load(open('/home/mangwon1/mof_project/21_ZIF69_MTV/results_v3_smoke.json'))
r = [x for x in d['rows'] if x.get('status') == 'ok']
if not r:
    print('FAIL'); raise SystemExit
q = r[0]['Qst_CO2']
# 이 계열의 Q_st 는 v2 에서 28~37 kJ/mol 이었습니다. 이완으로 몇 % 움직이는 것은
# 예상되지만, 10 밖으로 나가면 무언가 근본적으로 틀린 것입니다.
print('OK' if 10 < q < 60 else 'FAIL', f'{q:.2f}')
EOF
)
say "  연기 시험 판정: $verdict"
case "$verdict" in
  OK*) : ;;
  *)   halt "연기 시험 실패($verdict). 90작업을 띄우지 않습니다." ;;
esac

# ---------------------------------------------------------------- G
mark "G: 전체 GCMC v3 (90작업)"
say "=== G. 전체 GCMC v3 ==="
disk_guard
# [2026-08-16 자원 재배분] 워커 6 -> 7.
#   사용자가 9시간 동안 이 기기를 안 씁니다. boost.sh 실측이 "우선순위 0 으로
#   7개까지" 라고 계산했고(물리 8코어 - 수분 v2 의 RASPA 1건), RASPA 는 건당
#   약 471 MB 라 메모리는 병목이 아닙니다. 90작업짜리 단계라 17% 가 1.5시간입니다.
cd "$P" && V3_WORKERS=7 "$CZ/python" run_gcmc_v3.py 2>&1 | tee -a "$LOG"
n_res=$("$CZ/python" -c "
import json;d=json.load(open('$P/results_v3.json'))
print(sum(1 for r in d['rows'] if r.get('status')=='ok'))" 2>/dev/null || echo 0)
say "  GCMC v3 성공 $n_res 종"
{
  echo "이완된 구조 위에서 GCMC 를 다시 돌렸습니다($n_res 종 성공)."
  echo "규약은 v2 와 한 글자도 다르지 않습니다 -- 15000 사이클, UFF_MOF, DDEC6,"
  echo "0.15 bar, 298 K. 바뀐 것은 입력 기하뿐이라 차이를 '이완 때문' 이라고"
  echo "말할 수 있습니다."
  echo
  echo "v2 와의 비교는 아직 하지 않았습니다. 1.5σ 미만 차이에는 순위를 매기지 않습니다."
} > "$W/_ovn_body.txt"
commit "The same protocol on a better geometry" "$W/_ovn_body.txt" \
  21_ZIF69_MTV/results_v3.json 21_ZIF69_MTV/results_v3_smoke.json
echo "- **v3 GCMC $n_res 종 완료** — v2 대비 Q_st/선택도 변화를 노션 본문에 반영 필요" >> "$NOTION"

# ---------------------------------------------------------------- H
mark "H: 수분 v2 수확 (끝나 있으면)"
say "=== H. 수분 v2 수확 ==="
if [ -f "$P/v2_water/water_results.json" ]; then
  {
    echo "수분 경쟁 v2 20종(RH 0/25/50/90 x saIm 0~100%)."
    echo
    echo "작업 비용이 조합에 따라 13배까지 벌어집니다 -- rh00_base 1.5시간,"
    echo "rh90_saIm075 20.2시간. 평균 처리율로 잡은 일정이 꼬리에서 어긋난 이유이고,"
    echo "v3 큐는 비싼 것부터 넣어야 합니다(LPT, 표준 makespan 휴리스틱)."
  } > "$W/_ovn_body.txt"
  commit "Water competition v2, all twenty" "$W/_ovn_body.txt" 21_ZIF69_MTV/v2_water
  echo "- 수분 경쟁 v2 20/20 완료 — 노션 수분 절 갱신 필요" >> "$NOTION"
else
  say "  아직입니다(마지막 1건이 22~26시간짜리). 다음 사람이 이어받습니다."
  echo "- 수분 v2 진행 중 — 완주분은 캐시로 회수되므로 재기동만 하면 됩니다" >> "$NOTION"
fi

mark "완료 ($(date '+%m-%d %H:%M')) — v3 GCMC $n_res 종까지"
say "================ 밤샘 파이프라인 끝 ================"
exit 0
