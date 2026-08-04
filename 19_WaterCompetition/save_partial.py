"""진행 로그에서 완료된 작업만 뽑아 water_partial.json 으로 저장한다.

run_water.py 는 20개 작업이 전부 끝난 뒤에야 결과 json 을 쓴다. 그런데 이원
GCMC 는 작업 하나가 길어서 중간에 기기를 옮기거나 중단하는 일이 생긴다.
이 스크립트로 지금까지 끝난 것만 건져두면, 옮긴 기기에서 run_water.py 를
그대로 실행했을 때 남은 작업만 계산한다.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'water.log')
OUT = os.path.join(HERE, 'water_partial.json')

PAT = re.compile(
    r'\[\s*ok\s*\]\s*RH\s*(\d+)%\s+(\S+)\s+CO2\s+([\d.eE+-]+)\s+H2O\s+([\d.eE+-]+)')


def main():
    if not os.path.exists(LOG):
        print(f'로그 없음: {LOG}')
        return 1
    rows, seen = [], set()
    for line in open(LOG, encoding='utf-8', errors='ignore'):
        m = PAT.search(line)
        if not m:
            continue
        rh = int(m.group(1)) / 100.0
        name = m.group(2)
        if (name, rh) in seen:
            continue
        seen.add((name, rh))
        rows.append({'name': name, 'RH': rh,
                     'CO2_molkg': float(m.group(3)),
                     'H2O_molkg': float(m.group(4))})
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f'완료 작업 {len(rows)}개 저장 -> {os.path.basename(OUT)}')
    by = {}
    for r in rows:
        by.setdefault(r['name'], []).append(r)
    for n, rs in by.items():
        rhs = ', '.join(f'{int(r["RH"]*100)}%' for r in sorted(rs, key=lambda x: x['RH']))
        print(f'  {n:<34} RH {rhs}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
