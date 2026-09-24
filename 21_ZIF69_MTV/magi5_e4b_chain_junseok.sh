#!/bin/bash
# MAGI-005 E-4b 사슬 — Zeo++ 단계가 끝나면(e4b_zeo.py 없음 · network 0) (b) ZIF-68 273 K 와 (a) Widom 을 착수. Zeo++ 와 RASPA 동시 금지(CLAUDE.md §5).
D=/home/mangwon/mof_project/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin
LOG=$D/magi5_e4b_chain_junseok.log
export RASPA_DIR=$HOME/RASPA/simulations; export PATH=$CZ:$PATH
echo "$(date '+%F %T') 사슬 시작 — Zeo++ 끝을 기다림" >> $LOG
while ps -eo args | grep -q "^$CZ/python -u /home/mangwon/.junseok_chain/e4b_zeo.py" || [ "$(pgrep -xc network)" != 0 ]; do sleep 20; done
if [ ! -e $D/magi5_e4b_runs/zeo_summary.json ]; then echo "$(date '+%F %T') !! zeo_summary.json 없음 — 멈춤(Widom 안 띄움)" >> $LOG; exit 1; fi
echo "$(date '+%F %T') Zeo++ 끝 확인(network 0) — RASPA 착수" >> $LOG
if [ -e $D/magi5_runs_e4zif68_273K ] || [ -e $D/results_magi5_e3_e4zif68_273K_widom_junseok.json ]; then
  echo "$(date '+%F %T') !! (b) 실행 폴더/결과 이미 있음 — (b) 착수 안 함" >> $LOG
else
  (cd $D && setsid nohup $CZ/python -u run_magi5_widom.py --cif charged_v3/e4zif68_DDEC6.cif --tag e4zif68_273K --workers 4 --temp 273 \
      >> $D/magi5_e4b_zif68_273K_junseok.log 2>&1 < /dev/null &)
  echo "$(date '+%F %T') (b) 착수 — run_magi5_widom.py --tag e4zif68_273K --workers 4 --temp 273 (ON·OFF)" >> $LOG
fi
sleep 20
if [ -e $D/results_magi5_e4b_blockpockets_junseok.json ] || ls -d $D/magi5_e4b_runs/e4zif*_r* > /dev/null 2>&1; then
  echo "$(date '+%F %T') !! (a) Widom 산출 이미 있음 — 착수 안 함" >> $LOG
else
  (cd $D && setsid nohup $CZ/python -u /home/mangwon/.junseok_chain/magi5_e4b.py >> $D/magi5_e4b_widom_junseok.log 2>&1 < /dev/null &)
  echo "$(date '+%F %T') (a) Widom 드라이버 착수" >> $LOG
fi
echo "$(date '+%F %T') 사슬 끝" >> $LOG
