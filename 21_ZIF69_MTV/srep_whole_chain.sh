#!/bin/bash
# s_rep 러너 축 가름 — nbIm025 RH0 통짜 4회 순차 (laptop2, ASSIGN_20260903 §7). 무인 실행용.
#   기동:   setsid nohup bash 21_ZIF69_MTV/srep_whole_chain.sh < /dev/null &
#   재기동: 같은 명령. 완주한 r 은 run_water 이어받기가 cached 로 회수합니다.
#   tb5_chain.sh 와 **동시에** 띄워도 됩니다(코어 1개, 순차). 둘 다 RASPA 이고 Zeo++ 는
#   tb5 체인 4단계에만 있으며 그때는 이 체인이 끝나 있습니다(6 h 대 ~18 h).
set -u
P="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGDIR="$HOME/.claude_work"; mkdir -p "$LOGDIR"
L="$LOGDIR/srep_whole.log"
CZ="$HOME/miniconda3/envs/czeromof/bin/python"
export RASPA_DIR="${RASPA_DIR:-$HOME/RASPA/simulations}"
export PATH="$HOME/miniconda3/envs/czeromof/bin:$PATH"
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" | tee -a "$L"; }
cd "$P" || exit 1
say "=== s_rep 통짜 4회 시작 (pid $$) ==="
for r in 1 2 3 4; do
  t0=$(date +%s)
  nice -n 10 "$CZ" -u run_water_whole_nbim025_rep.py --rep "$r" >> "$L" 2>&1
  say "r$r rc=$?  $(( ($(date +%s)-t0)/60 )) 분"
done
"$CZ" -u run_water_whole_nbim025_rep.py --summary 2>&1 | tee -a "$L"
say "=== 끝 -> v3_water_srep_whole/srep_whole_summary.json ==="
