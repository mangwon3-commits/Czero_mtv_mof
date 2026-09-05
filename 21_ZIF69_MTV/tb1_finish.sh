#!/usr/bin/env bash
# T-B1 완주 감시 + 자동 분석.  사용:  tb1_finish.sh <실행폴더> <simulate PID>
#
# ⚠️ **경로를 인자로 받습니다.** 09-05 에 `tb1_analyze.py` 를 인자 없이 부르던
#    감시가 있었는데, 그 글롭(`tb1_runs_n*`)이 옛 속도 시험까지 잡아 **mtime 으로
#    아무거나 집는** 구조였습니다. 지금은 실행이 넷이라 더 위험합니다.
D="$1"; P="$2"
PY="$HOME/miniconda3/envs/czeromof/bin/python"
DATA="$D/Output/System_0/output_Box_1.1.1_298.150000_100000.data"
echo "감시 시작 $(date '+%F %T')   폴더 $D   simulate PID $P"
while kill -0 "$P" 2>/dev/null; do sleep 120; done
echo "=== 종료 감지 $(date '+%F %T') ==="
echo; echo "=== ΔH_vap 분석 (경로 명시) ==="
nice -n 19 "$PY" tb1_analyze.py "$DATA" 2>&1
echo; echo "=== 점검 ② U/N 생산 블록 단조 추세 ==="
nice -n 19 "$PY" - "$DATA" <<'PYEOF' 2>&1
import re,sys
t=open(sys.argv[1],encoding='utf-8',errors='replace').read()
m=re.search(r'Average Adsorbate-Adsorbate energy:\s*\n=+\n(.*?)\n\s*\n',t,re.S)
if not m: print('  블록 못 찾음'); raise SystemExit
b=[float(x) for x in re.findall(r'Block\[\s*\d+\]\s+(-?[\d.eE+]+)',m.group(1))]
k=0.0083144626/1000
v=[x*k for x in b]
print('  블록별 U/N [kJ/mol]: ' + ' '.join(f'{x:.4f}' for x in v))
d=[v[i+1]-v[i] for i in range(len(v)-1)]
print('  연속 차분: ' + ' '.join(f'{x:+.4f}' for x in d))
mono = all(x>0 for x in d) or all(x<0 for x in d)
print(f'  단조 추세 {"**있음 — 평형화 미완 의심**" if mono else "없음 -> 통과"}')
PYEOF
echo; echo "=== 점검 ③ 밀도 (NVT — 부과값입니다) ==="
grep -aoE "density: [0-9.]+" "$DATA" | tail -1
echo; echo "=== 구조 (최종 Restart) ==="
nice -n 19 "$PY" tb1_struct.py "$D" 2>&1
