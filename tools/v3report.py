"""v2 -> v3 비교. 규약이 같으므로 차이는 '이완 때문' 이라고 말할 수 있다."""
import json
import math

P = '/home/mangwon1/mof_project/21_ZIF69_MTV'
v2 = {r['name']: r for r in json.load(open(f'{P}/results_v2.json'))['rows']
      if r.get('status') == 'ok'}
v3 = {r['name']: r for r in json.load(open(f'{P}/results_v3.json'))['rows']
      if r.get('status') == 'ok'}

# 2026-09-24 — `status == 'ok'` 는 **GCMC 완주 표지이지 구조 표지가 아닙니다**(CLAUDE.md §2).
# 아래 다섯 중 셋(saIm075 20.26 % · saIm100 22.50 % · mslm075 21.67 %)이 **관문 ⑤ 탈락**입니다.
# 값을 지우지 않고 **표지를 붙입니다** — 표지가 없으면 읽는 사람이 우리 물질로 읽습니다.
gate = {}
for f in ('risk_results_v3.json', 'risk_results_v3grid.json'):
    try:
        for r in json.load(open(f'{P}/{f}'))['rows']:
            gate[r['name']] = (r.get('pass'), r.get('LCD_drop_pct'))
    except OSError:
        pass


def gmark(n):
    p_, d = gate.get(n, (None, None))
    if p_ is None:
        return '  관문?'
    return '  통과' if p_ else f'  탈락{d:.1f}%'


def sig(a, ea, b, eb):
    s = math.sqrt(ea ** 2 + eb ** 2)
    return (b - a) / s if s else 0.0


print('=== GCMC: v2 -> v3 (이완이 얼마나 바꿨나) ===')
print(f'  {"구조":<10} {"Q_st v2":>9} {"Q_st v3":>9} {"차이":>8} '
      f'{"로딩 v2":>9} {"로딩 v3":>9} {"차이":>8} {"관문⑤":>8}')
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
          f'{a["loading_015bar"]:9.4f} {b["loading_015bar"]:9.4f} {sl:+7.1f}s'
          f'{gmark(n):>9}{mark}')
    if abs(sq) >= 1.5 or abs(sl) >= 1.5:
        big.append(n)

print(f'\n  1.5시그마 넘게 움직인 구조: {" ".join(big) if big else "없음"}')
_f = [n for n in v3 if gate.get(n, (True,))[0] is False]
print(f'  ⚠ 관문 ⑤ 탈락(우리 물질로 인용 금지 — GATE_SAIM100_20260924.md): {" ".join(sorted(_f)) or "없음"}')
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
