import json
import math

P = '/home/mangwon1/mof_project/21_ZIF69_MTV'


def load(p):
    d = json.load(open(p, encoding='utf-8'))
    rows = d.get('rows', d) if isinstance(d, dict) else d
    return {x['name']: x for x in rows}


r2 = load(f'{P}/v2_wc/working_capacity.json')
r3 = load(f'{P}/v3_wc/working_capacity.json')
keys = list(list(r3.values())[0]['working_capacity'])
print('  working_capacity 항목:', keys)

for key in keys:
    print(f'\n  === {key} 작업 용량 [mol/kg] ===')
    print(f'  {"구조":<10} {"v2":>18} {"v3":>18} {"차이":>9}')
    for n in ['base', 'saIm025', 'saIm050', 'saIm075', 'mslm075', 'saIm100']:
        a, b = r2.get(n), r3.get(n)
        ka = a['working_capacity'].get(key) if a else None
        kb = b['working_capacity'].get(key) if b else None

        def fmt(v):
            if v is None:
                return '--'
            if isinstance(v, (list, tuple)):
                return f'{v[0]:8.4f} ± {v[1]:.4f}'
            if isinstance(v, dict):
                vv = v.get("value", v.get("wc"))
                ee = v.get("err", v.get("error", 0.0))
                return f"{vv:8.4f} +- {ee:.4f}" if vv is not None else str(v)[:24]
            return f"{v:8.4f}"

        s = ''
        def pair(v):
            if isinstance(v, dict):
                return v.get('value'), v.get('err', 0.0)
            if isinstance(v, (list, tuple)):
                return v[0], v[1]
            return None, None
        (va, ea), (vb, eb) = pair(ka), pair(kb)
        if va is not None and vb is not None:
            sd = math.sqrt(ea ** 2 + eb ** 2)
            if sd:
                s = f'{(vb-va)/sd:+7.1f}s'
        print(f'  {n:<10} {fmt(ka):>18} {fmt(kb):>18} {s:>9}')
