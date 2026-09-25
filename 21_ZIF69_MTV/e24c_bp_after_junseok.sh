#!/bin/bash
# E-24c 막음 Widom 대기 기동(Junseok): 사슬(①②③)이 "③ rc 0" 으로 끝나고 simulate · network · lmp_serial 0 일 때만(Zeo++ 와 RASPA 동시 금지).
# 대상 = OCH₃ + (① 결과에서 주머니가 있으면) C₂H₅.
D=/home/mangwon/mof_project/21_ZIF69_MTV; CZ=/home/mangwon/miniconda3/envs/czeromof/bin
cd "$D" || exit 1
echo "대기 시작 $(date +%T)"
for i in $(seq 1 480); do grep -q '③ rc\|!!' e24c_chain_junseok.log && break; sleep 30; done
grep -q '③ rc 0' e24c_chain_junseok.log || { echo "!! 사슬이 ③ rc 0 으로 안 끝남 — 막음 Widom 안 띄움 $(date +%T)"; exit 1; }
sleep 10
[ "$(pgrep -xc simulate)" = 0 ] && [ "$(pgrep -xc network)" = 0 ] && [ "$(pgrep -c lmp_serial)" = 0 ] || { echo "!! 도는 것 있음 — 안 띄움"; exit 1; }
TAGS=$($CZ/python -c "
import json
d = json.load(open('results_e24c_access_junseok.json'))
t = ['e24c_och3_100']
r = {x['tag']: x for x in d['rows']}['e24c_c2h5_100']
if (r['r1.65']['block']['pockets'] or 0) > 0 or (r['r1.82']['block']['pockets'] or 0) > 0: t.append('e24c_c2h5_100')
print(','.join(t))")
echo "막음 Widom 착수 $(date +%T) · 대상 $TAGS"
export RASPA_DIR=$HOME/RASPA/simulations; export PATH=$CZ:$PATH
$CZ/python -u magi5_e24c_bp_junseok.py --tags "$TAGS" >> e24c_bp_junseok.log 2>&1
echo "BP rc $? $(date +%T)"
