#!/bin/bash
# E-15b 사슬 — ③(magi5_tj1c.py) 가 끝나고 simulate 0 이면: ② Zeo++ -ha -res 1건(RASPA 0 일 때) → ① run_magi5_widom.py(ON·OFF, 워커 4).
D=/home/mangwon/mof_project/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin; Z=$CZ/network
LOG=$D/magi5_e15b_chain_junseok.log
CIF=core_pop_cifs/2017_Cd__hcb_2_ASR_1.cif
export RASPA_DIR=$HOME/RASPA/simulations; export PATH=$CZ:$PATH
echo "$(date '+%F %T') 사슬 시작 — ③ 끝을 기다림" >> $LOG
while ps -eo args | grep -q "^$CZ/python -u /home/mangwon/.junseok_chain/magi5_tj1c.py" || [ "$(pgrep -xc simulate)" != 0 ]; do sleep 30; done
cd $D || exit 1
[ -e $CIF ] || { echo "$(date '+%F %T') !! $CIF 없음 — 멈춤" >> $LOG; exit 1; }
W=$D/magi5_e15b_zeo
if [ ! -e $W ]; then
  mkdir -p $W && cp $CIF $W/
  (cd $W && timeout 600 $Z -ha -res 2017_Cd__hcb_2_ASR_1.res 2017_Cd__hcb_2_ASR_1.cif > zeo_res.out 2>&1)
  echo "$(date '+%F %T') ② -ha -res: $(cat $W/2017_Cd__hcb_2_ASR_1.res 2>/dev/null) (annotated LCD 6.93233 · PLD 4.45124)" >> $LOG
fi
[ "$(pgrep -xc network)" = 0 ] || { echo "$(date '+%F %T') !! network 가 아직 돎 — ① 안 띄움" >> $LOG; exit 1; }
if [ -e $D/magi5_runs_e15b_cdhcb ] || [ -e $D/results_magi5_e3_e15b_cdhcb_widom_junseok.json ]; then
  echo "$(date '+%F %T') !! ① 산출 이미 있음 — 착수 안 함" >> $LOG; exit 1
fi
(setsid nohup $CZ/python -u run_magi5_widom.py --cif $CIF --tag e15b_cdhcb --workers 4 --temp 298 >> $D/magi5_e15b_junseok.log 2>&1 < /dev/null &)
echo "$(date '+%F %T') ① 착수 — run_magi5_widom.py --tag e15b_cdhcb --workers 4 --temp 298 (ON·OFF)" >> $LOG
echo "$(date '+%F %T') 사슬 끝" >> $LOG
