"""건조 작업 용량 v3 — saIm0583 한 종 (제약 하 1위 판정용 보강).

DECISION_RULE_20260820.md 가 이 계산 전에 등록됐다. 규약은 v3_wc 와
한 글자도 다르지 않다 -- 같은 표에 놓아야 하므로. 결과 파일과 작업
폴더만 분리한다(이어받기 오염 방지, run_humid_wc_v3grid.py 와 같은 이유).
"""
import os
import sys

import run_working_capacity as wc

REAL = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REAL, 'v3_wc')
os.makedirs(V3, exist_ok=True)

wc.HERE = V3
wc.CHARGED = os.path.join(REAL, 'charged_v3')
wc.RUNS = os.path.join(REAL, 'wc_runs_v3g0583')
wc.RESULT = os.path.join(V3, 'working_capacity_g0583.json')
wc.TARGETS = ['saIm0583']
wc.MAX_WORKERS = int(os.environ.get('WC_G0583_WORKERS', '4'))

if __name__ == '__main__':
    print('건조 작업 용량 v3 — saIm0583 (경계 생존자 보강)', flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:<8} {getattr(wc, k)}', flush=True)
    assert wc.RUNS.endswith('g0583') and wc.RESULT.endswith('g0583.json')
    if not os.path.exists(os.path.join(wc.CHARGED, 'saIm0583_DDEC6.cif')):
        print('  !! 전하 파일 없음', flush=True); sys.exit(1)
    print(flush=True)
    sys.exit(wc.main())
