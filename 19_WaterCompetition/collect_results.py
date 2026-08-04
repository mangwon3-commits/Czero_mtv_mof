"""runs/ 디렉터리를 직접 훑어 CO2/H2O 경쟁 흡착 결과를 모은다.

run_water.py 는 20개 작업이 전부 끝나야 결과를 쓰는데, 실제로는 기기 이전이나
부하 때문에 중간에 끊는 일이 생긴다. 이 스크립트는 부모 프로세스 생존 여부와
무관하게 이미 끝난 RASPA 출력만 읽어 표를 만든다. 그래서 옮긴 기기에서도,
일부만 돌린 상태에서도 그대로 쓸 수 있다.

건조 기준값이 없는 구조는 18_PoreNarrowing 의 GCMC 결과를 대신 쓴다(프로토콜이
사이클 수만 다르고 나머지는 동일하다). 그 경우 출처를 표시한다.
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'runs')
FALLBACK = os.path.join(HERE, '..', '18_PoreNarrowing', 'narrow_results.json')

LABEL = {
    'mIm100__closed': '순수 ZIF-8 (소수성 대조군)',
    'clIm100__closed': 'Cl 100%',
    'mIm050_saIm050__closed': 'SO3H 50% (최고 로딩)',
    'clIm050_saIm050__closed': 'Cl 50% + SO3H 50% (최고 Qst)',
    'clIm050_mIm025_saIm025__closed': 'Cl 50% + SO3H 25%',
}


def parse(path):
    """성분별 흡착량. RASPA 출력은 Component 블록마다 같은 문구를 반복한다."""
    out, cur = {}, None
    for line in open(path, encoding='utf-8', errors='ignore'):
        m = re.search(r'Component\s+(\d+)\s+\[(\w+)\]', line)
        if m:
            cur = m.group(2)
        if cur and 'Average loading absolute [mol/kg framework]' in line:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if v and cur not in out:
                out[cur] = (float(v.group(1)), float(v.group(2)))
    return out


def main():
    res = {}
    for d in sorted(glob.glob(os.path.join(RUNS, 'rh*'))):
        m = re.match(r'rh(\d+)_(.+)$', os.path.basename(d))
        if not m:
            continue
        rh, name = int(m.group(1)) / 100.0, m.group(2)
        outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        if not outs:
            continue
        r = parse(outs[0])
        if 'CO2' not in r:          # 아직 안 끝난 작업
            continue
        res.setdefault(name, {})[rh] = r

    fb = {}
    if os.path.exists(FALLBACK):
        for x in json.load(open(FALLBACK, encoding='utf-8')):
            fb[x['name']] = x.get('loading_015bar')

    print(f'{"구조":<32} {"RH":>5} {"CO2":>10} {"H2O":>10} '
          f'{"건조대비 CO2":>13} {"H2O/CO2":>9}')
    print('-' * 88)
    rows = []
    for name in [k for k in LABEL if k in res] + [k for k in res if k not in LABEL]:
        lab = LABEL.get(name, name)
        dry = (res[name].get(0.0) or {}).get('CO2', (None,))[0]
        src = '측정'
        if dry is None:
            dry, src = fb.get(name), '18_ 기준'
        for rh in sorted(res[name]):
            c = res[name][rh]['CO2'][0]
            w = res[name][rh].get('water', (0.0,))[0]
            ret = c / dry * 100 if dry else float('nan')
            print(f'{lab:<32} {int(rh*100):>4}% {c:>10.4f} {w:>10.4f} '
                  f'{ret:>12.1f}% {(w/c if c else float("inf")):>9.2f}')
            rows.append({'name': name, 'label': lab, 'RH': rh,
                         'CO2_molkg': c, 'H2O_molkg': w,
                         'CO2_retention_pct': ret, 'dry_baseline': dry,
                         'dry_source': src})
        if src != '측정':
            print(f'{"":<32} (건조 기준값은 18_PoreNarrowing 결과 사용)')
        print()

    with open(os.path.join(HERE, 'water_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    n = len(rows)
    print(f'[OK] water_results.json  ({n}/20 작업)')
    if n < 20:
        print('미완료 작업은 데스크탑에서 run_water.py 재실행 시 이어서 계산됩니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
