"""T-NF-0v 판정 — `TNF0V_REGISTRATION_20260911.md §5` 를 **그대로** 코드로 옮긴 것.

비교는 **딱 둘**입니다(등록문 §5). 표는 기록이고 판정이 아닙니다 —
9구조를 늘어놓고 사후에 눈에 띄는 쌍에 문턱을 걸면 결과 보고 기준 고치기입니다.

    K_H^vol  ∝  K_H(질량당) x rho / phi
    문턱: 1.5 x 합성 ±   (± 는 RASPA 95% CI. 단일 배열 구조라 배치 단위 해당 없음)
"""
import json, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = __import__('socket').gethostname().lower()
HEV = os.path.join(HERE, 'v3w_helium_void', f'helium_void_{HOST}.json')
KEXT = os.path.join(HERE, 'v3w_water_kh_ext', f'water_kh_extfw_{HOST}.json')
KOUR = os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome_seedfixed.json')


def agg(rows, name, key, ekey):
    r = [x for x in rows if x['name'] == name and x.get('ok', True) and x.get(key) is not None]
    if not r:
        return None
    v = [x[key] for x in r]; e = [x[ekey] for x in r if x.get(ekey) is not None]
    return {'mean': sum(v) / len(v), 'n': len(v),
            'pm': (sum(q * q for q in e) ** 0.5) / len(e) if e else None,
            'sd': st.stdev(v) if len(v) > 1 else None,
            'seeds_ok': len({x.get('raspa_seed') for x in r}) == len(r)}


def main():
    for f in (HEV, KEXT, KOUR):
        if not os.path.exists(f):
            print(f'  결과 없음: {f}'); return 1
    hev = json.load(open(HEV, encoding='utf-8'))
    kext = {r['name']: r for r in json.load(open(KEXT, encoding='utf-8'))['rows']}
    kour = {r['name']: r for r in json.load(open(KOUR, encoding='utf-8'))['rows']}
    hrows = hev['rows']
    names = sorted({r['name'] for r in hrows})

    D = {}
    for n in names:
        phi = agg(hrows, n, 'phi', 'phi_err')
        if not phi:
            continue
        rho = next(r['density_g_cm3'] for r in hrows if r['name'] == n)
        if n in kext:
            kk = agg(json.load(open(KEXT, encoding='utf-8'))['rows'], n,
                     'KH_water', 'KH_water_err')
            k, ke = kk['mean'], kk['pm']
        elif n in kour:
            k, ke = kour[n]['KH_water'], kour[n].get('KH_water_err')
        else:
            continue
        kv = k * rho / phi['mean']
        rel = ((ke / k) ** 2 + (phi['pm'] / phi['mean']) ** 2) ** 0.5 if ke else None
        D[n] = {'phi': phi['mean'], 'phi_pm': phi['pm'], 'rho': rho, 'KH': k,
                'KH_pm': ke, 'KHvol': kv, 'rel': rel, 'seeds_ok': phi['seeds_ok']}

    print('  ═══ T-NF-0v · 헬륨 공극률 정규화 ═══\n')
    print(f"  {'구조':10s} {'phi':>7s} {'rho':>7s} {'K_H(질량당)':>12s} {'K_H^vol':>11s} "
          f"{'상대±':>7s}  씨앗")
    for n, v in sorted(D.items(), key=lambda x: x[1]['KHvol']):
        rel = f"{v['rel']*100:5.1f}%" if v['rel'] else '  —  '
        print(f"  {n:10s} {v['phi']:7.4f} {v['rho']:7.4f} {v['KH']:12.4e} "
              f"{v['KHvol']:11.4e} {rel:>7s}  {'예' if v['seeds_ok'] else '**아니오**'}")
    print('\n  ↑ 표는 **기록**입니다. 판정은 등록문 §5 의 두 비교뿐입니다.')

    def judge(a, b, label, mass_note, resolved, real):
        if a not in D or b not in D:
            print(f'\n  {label}: 결과 부족'); return
        x, y = D[a], D[b]
        ratio = x['KHvol'] / y['KHvol']
        rel = ((x['rel'] or 0) ** 2 + (y['rel'] or 0) ** 2) ** 0.5
        # 비의 1 로부터의 거리를 합성 상대오차 단위로
        units = abs(ratio - 1) / (ratio * rel) if rel else float('inf')
        print(f"\n  ── {label} ──")
        print(f"  질량당: {mass_note}")
        print(f"  정규화 후 {a}/{b} = **{ratio:.3f}**   (1 로부터 **{units:.2f} 단위**, 문턱 1.5)")
        if units <= 1.5:
            print('  -> **미결** — 차이가 1.5 x 합성 ± 안입니다.')
        elif ratio > 1:
            print(f'  -> {resolved}')
        else:
            print(f'  -> {real}')

    judge('zif93', 'mbIm025', '(가) ㉡ — ZIF-93 대 mbIm025',
          f"ZIF-93 이 {D['zif93']['KH']/D['mbIm025']['KH']:.3f}배 (3.9배 아래)"
          if 'zif93' in D and 'mbIm025' in D else '—',
          '**㉡ 해소** — 부피 교란이었습니다. 물 수확 소재가 제자리로 옵니다',
          '**㉡ 실재** — 부피를 걷어내도 모델은 mbIm025 를 위에 둡니다 '
          '(등록문 §7: 이것이 "정말 더 친수" 라는 뜻은 **아닙니다**)')

    judge('zif90', 'zif93', '(나) ㉠ — ZIF-90 대 ZIF-93',
          f"ZIF-93 이 {D['zif93']['KH']/D['zif90']['KH']:.2f}배 위 (문헌과 반대)"
          if 'zif93' in D and 'zif90' in D else '—',
          '**㉠ 해소** — 뒤집힘은 부피였습니다. 교차항 순위가 §5-1 보다 낫습니다',
          '**㉠ 실재** — 뒤집힘이 상호작용 항에 있습니다')
    return 0


if __name__ == '__main__':
    sys.exit(main())
