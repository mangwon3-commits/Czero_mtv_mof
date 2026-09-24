# -*- coding: utf-8 -*-
"""습윤 밀도 격자 작업의 **적재 값을 출력에서 회수**합니다 (2026-09-24, Caspar 질문에서).

## 왜 필요한가 — 러너가 그 JSON 을 **안 씁니다**

`run_density_water_v3.py:127` 이 `rw.run_one()` 을 **직접** 부르는데, `water_results.json` 은
`rw.main()`(`run_water.py:403`)에서 쓰입니다. 그래서 **아무도 안 씁니다.**
`run_one` 이 돌려주는 `(name, rh, res, status)` 중 값이 든 `res` 는 **버려지고** `r[-1]`(상태)만 찍힙니다.

**그런데 118행이 `결과 …/water_results.json` 을 찍습니다** — 안 생기는 파일의 경로를요.
CLAUDE.md §0 의 *"실패가 결과처럼 보이는 것"* 입니다: 폴더는 만들어지고 경로는 찍히고
격자는 남아서, **적재 값만 조용히 없습니다.**

`density_water_v3w/loadings_from_output.json` 은 그래서 한 번 **손으로** 만든 것이고
스크립트가 안 남았습니다. 이 파일이 그 도구입니다.

    python extract_density_loadings.py                  # 완주분 전부 회수
    python extract_density_loadings.py --print          # 쓰지 않고 표만

⚠ **파서를 새로 쓰지 않습니다** — `run_water.parse_components` 를 그대로 import 합니다.
파서가 둘이면 서로 어긋납니다(오늘 §C 계열).
"""
import argparse, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_water import parse_components, finished        # 파서는 **하나**만

RUNS = os.path.join(HERE, 'water_runs_density_v3w')
OUT = os.path.join(HERE, 'density_water_v3w', 'loadings_from_output.json')


def seed_of(path):
    for ln in open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m:
            return int(m.group(1))
        if ln.startswith('Number of cycles'):
            break
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--print', dest='only_print', action='store_true')
    a = ap.parse_args()

    rows, skipped = {}, []
    for d in sorted(glob.glob(os.path.join(RUNS, 'rh90_*'))):
        name = os.path.basename(d)[len('rh90_'):]
        data = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
        if not data:
            skipped.append((name, '.data 없음')); continue
        f = data[0]
        if not finished(f):                    # ⚠ **표지를 요구합니다** — VTK 는 500사이클마다
            skipped.append((name, '미완주(표지 없음)'))   #   쓰여 끊긴 실행에도 남습니다(§0)
            continue
        comp = parse_components(f)
        if not comp:
            skipped.append((name, '성분 못 읽음')); continue
        rows[name] = {
            'CO2': list(comp.get('CO2', (None, None))),
            'water': list(comp.get('water', (None, None))),
            'seed': seed_of(f),
            'file': os.path.relpath(f, HERE),
        }

    w = max([len(n) for n in rows] + [8])
    print('완주 %d · 건너뜀 %d' % (len(rows), len(skipped)))
    print('  %-*s %12s %12s   %s' % (w, '조성', 'CO2', '물', '(mol/kg ± )'))
    for n, r in rows.items():
        c, h = r['CO2'], r['water']
        print('  %-*s %7.4f±%.4f %7.4f±%.4f' % (w, n, c[0], c[1], h[0], h[1]))
    for n, why in skipped:
        print('  %-*s  -- %s' % (w, n, why))

    if not a.only_print:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(rows, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print('\n-> %s' % os.path.relpath(OUT, HERE))
    return 0


if __name__ == '__main__':
    sys.exit(main())
