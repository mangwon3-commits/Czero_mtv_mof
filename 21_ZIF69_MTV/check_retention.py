"""수분 경쟁 v2 에서 RH90 CO2 유지율을 다시 잰다 — saIm100 종료 판정의 재판정.

사전 등록 기준(run_working_capacity.py docstring): RH90 유지율 50% 미만이면 종료.
유지율 = CO2(RH90) / CO2(RH0).
"""
import json
import math

P = '/home/mangwon1/mof_project/21_ZIF69_MTV'
d = json.load(open(f'{P}/v2_water/water_results.json', encoding='utf-8'))
rows = d if isinstance(d, list) else d.get('rows', d)

by = {}
for r in rows:
    by.setdefault(r['name'], {})[round(float(r['RH']), 2)] = r

print(f'  {"구조":<10} {"CO2 RH0":>10} {"CO2 RH90":>10} {"유지율":>10} '
      f'{"H2O RH90":>10}  판정(50% 기준)')
print('  ' + '-' * 72)
for name in sorted(by):
    a = by[name].get(0.0) or by[name].get(0)
    b = by[name].get(0.9)
    if not (a and b):
        print(f'  {name:<10} 자료 부족: RH {sorted(by[name])}')
        continue
    c0, c9 = float(a['CO2_molkg']), float(b['CO2_molkg'])
    e0 = float(a.get('CO2_err', 0.0) or 0.0)
    e9 = float(b.get('CO2_err', 0.0) or 0.0)
    ret = c9 / c0 * 100
    # 비의 오차 전파
    err = ret * math.sqrt((e0 / c0) ** 2 + (e9 / c9) ** 2) if c0 and c9 else 0.0
    verdict = '통과' if ret >= 50 else '**종료 기준 해당**'
    # 오차를 감안해 50%와 구별되는지도 본다
    if abs(ret - 50) < 1.5 * err:
        verdict += ' (50%와 1.5시그마 안 — 구별 불가)'
    print(f'  {name:<10} {c0:10.4f} {c9:10.4f} {ret:8.1f}±{err:.1f}% '
          f'{float(b.get("H2O_molkg", 0)):10.4f}  {verdict}')

print()
print('  주: 유지율은 CO2(RH90)/CO2(RH0). 사전 등록 종료 기준은 50% 미만.')
