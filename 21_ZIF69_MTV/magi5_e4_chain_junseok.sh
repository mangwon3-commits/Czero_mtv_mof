#!/bin/bash
# MAGI-005 E-4 Widom 뒷절반 사슬 (Junseok 몫: zif3 · zif6 · zif10 · zif20 · zif7) — ASSIGN_MAGI5B §Junseok 2차
# 전하본 charged_v3/e4zif<NN>_DDEC6.cif 가 origin/master 에 올라오는 대로 착수한다.
# ⚠ 러너가 도는 동안 postman 은 master 를 병합하지 않고, 수동 병합·체크아웃도 금지(CLAUDE.md) →
#   작업 트리를 건드리지 않고 `git fetch` + `git show origin/master:<경로>` 로 저장소 **밖**에 꺼내 쓴다(blob 해시를 로그에).
#   charged_v3/ 에 추적 안 되는 사본을 두면 나중 병합이 "untracked would be overwritten" 으로 막히므로 두지 않는다.
# 드라이버는 저장소의 run_magi5_widom.py(1a9b6ae1 정정본) 그대로, 인자도 배정문 그대로. 구조 사이 착수 ≥ 20 s(씨앗).
G=/home/mangwon/mof_project; D=$G/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin
E=$HOME/.junseok_chain/e4; mkdir -p $E
LOG=$D/magi5_e4_chain_junseok.log
export RASPA_DIR=$HOME/RASPA/simulations; export PATH=$CZ:$PATH
MINE="3 6 10 20 7"
echo "$(date '+%F %T') 사슬 시작 — 몫 e4zif{3,6,10,20,7} · 드라이버 $(cd $G && git log --oneline -1 -- 21_ZIF69_MTV/run_magi5_widom.py | cut -c1-8)" >> $LOG
last=0
for i in $(seq 1 150); do                       # 150 × 120 s = 5 h
  (cd $G && git fetch -q origin master) 2>> $LOG
  pending=0
  for n in $MINE; do
    tag=e4zif$n
    [ -e $E/$tag.launched ] && continue
    pending=1
    p=21_ZIF69_MTV/charged_v3/${tag}_DDEC6.cif
    (cd $G && git cat-file -e origin/master:$p) 2>/dev/null || continue
    blob=$(cd $G && git rev-parse origin/master:$p)
    (cd $G && git show origin/master:$p) > $E/${tag}_DDEC6.cif
    [ -s $E/${tag}_DDEC6.cif ] || { echo "$(date +%T) !! $tag 빈 파일 — 다음 회차" >> $LOG; continue; }
    if [ -e $D/magi5_runs_$tag ]; then
      echo "$(date +%T) !! magi5_runs_$tag 이미 있음 — 착수 안 함(이어받기 방지)" >> $LOG; touch $E/$tag.launched; continue
    fi
    now=$(date +%s); w=$(( last + 20 - now )); [ $w -gt 0 ] && sleep $w
    (cd $D && setsid nohup $CZ/python -u run_magi5_widom.py --cif $E/${tag}_DDEC6.cif --tag $tag --workers 1 --temp 298 \
        >> $D/magi5_e4_${tag}_junseok.log 2>&1 < /dev/null &)
    last=$(date +%s); touch $E/$tag.launched
    echo "$(date '+%F %T') 착수 $tag · origin/master blob $blob · CIF $E/${tag}_DDEC6.cif" >> $LOG
  done
  [ $pending = 0 ] && { echo "$(date '+%F %T') 다섯 모두 착수 — 사슬 끝" >> $LOG; exit 0; }
  sleep 120
done
echo "$(date '+%F %T') !! 5 h 시한 — 안 온 구조가 있음" >> $LOG
