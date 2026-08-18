"""v2 -> v3 비교. 규약이 같으므로 차이는 '이완 때문' 이라고 말할 수 있다."""
import json
import math

P = '/home/mangwon1/mof_project/21_ZIF69_MTV'
v2 = {r['name']: r for r in json.load(open(f'{P}/results_v2.json'))['rows']
      if r.get('status') == 'ok'}
v3 = {r['name']: r for r in json.load(open(f'{P}/results_v3.json'))['rows']
      if r.get('status') == 'ok'}


def sig(a, ea, b, eb):
    s = math.sqrt(ea ** 2 + eb ** 2)
    return (b - a) / s if s else 0.0


print('=== GCMC: v2 -> v3 (이완이 얼마나 바꿨나) ===')
print(f'  {"구조":<10} {"Q_st v2":>9} {"Q_st v3":>9} {"차이":>8} '
      f'{"로딩 v2":>9} {"로딩 v3":>9} {"차이":>8}')
big = []
for n in ['saIm025', 'saIm050', 'saIm075', 'saIm100', 'mslm075']:
    a, b = v2.get(n), v3.get(n)
    if not (a and b):
        continue
    sq = sig(a['Qst_CO2'], a['Qst_CO2_err'], b['Qst_CO2'], b['Qst_CO2_err'])
    sl = sig(a['loading_015bar'], a['loading_015bar_err'],
             b['loading_015bar'], b['loading_015bar_err'])
    mark = ' *' if abs(sq) >= 1.5 or abs(sl) >= 1.5 else ''
    print(f'  {n:<10} {a["Qst_CO2"]:9.2f} {b["Qst_CO2"]:9.2f} {sq:+7.1f}s '
          f'{a["loading_015bar"]:9.4f} {b["loading_015bar"]:9.4f} {sl:+7.1f}s{mark}')
    if abs(sq) >= 1.5 or abs(sl) >= 1.5:
        big.append(n)

print(f'\n  1.5시그마 넘게 움직인 구조: {" ".join(big) if big else "없음"}')
print(f'  v3 에만 있는 대조군 base: '
      f'Q_st {v3["base"]["Qst_CO2"]:.2f} ± {v3["base"]["Qst_CO2_err"]:.2f}, '
      f'로딩 {v3["base"]["loading_015bar"]:.4f}' if 'base' in v3 else '')

print('\n=== 건조 작업 용량 v3 (랩탑) ===')
w = json.load(open(f'{P}/v3_wc/working_capacity.json'))
rows = w.get('rows', w) if isinstance(w, dict) else w
if isinstance(rows, dict):
    rows = [dict(name=k, **v) for k, v in rows.items()]
for r in rows:
    keys = [k for k in r if 'wc' in k.lower() or 'tsa' in k.lower()]
    print(f'  {str(r.get("name","?")):<10} ' +
          '  '.join(f'{k}={r[k]:.4f}' for k in keys
                    if isinstance(r.get(k), (int, float)))[:96])
