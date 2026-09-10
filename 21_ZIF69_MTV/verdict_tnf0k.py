"""T-NF-0k 판정 — `TNF0K_REGISTRATION_20260911.md §6` 을 **그대로** 코드로 옮긴 것.

결과를 보고 규칙을 고치지 않기 위해 **친수 골격 결과가 나오기 전에** 씁니다
(ZIF-71 3건은 이미 봤습니다 — 분모 쪽이고, 규칙은 등록문에 고정돼 있습니다).

    R = min(K_H(zif90), K_H(zif93)) / K_H(zif71)     <- min 은 보수적 선택(둘 다 넘어야 함)
    R >= 10 그리고 차이 > 1.5 x 합성 ±   -> 갈래 B (교차항은 순위를 맞춤)
    R < 3                                -> 갈래 A (교차항 자체가 약함)
    그 사이, 또는 1.5x± 미달              -> **미결.** 씨앗 증설(자는 안 바꿈)

자: RASPA `±` 는 **95% 신뢰구간**입니다(t(0.975,4) x SEM). 문턱 1.5 는 그 단위입니다.
단일 링커 정렬 구조라 **배치 단위는 해당 없습니다**(등록문 §5).
"""
import json, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, 'v3w_water_kh_ext',
                 f"water_kh_extfw_{__import__('socket').gethostname().lower()}.json")


def agg(rows, name):
    r = [x for x in rows if x['name'] == name and x['ok']]
    if not r:
        return None
    k = [x['KH_water'] for x in r]
    e = [x['KH_water_err'] for x in r]
    # 반복 평균의 ± : 각 실행의 95% CI 를 독립으로 보고 합성 (1/n * sqrt(sum e^2))
    err = (sum(v * v for v in e) ** 0.5) / len(e)
    seeds = [x.get('raspa_seed') for x in r]
    return {'name': name, 'n': len(k), 'mean': sum(k) / len(k), 'pm': err,
            'sd': st.stdev(k) if len(k) > 1 else None, 'vals': k,
            'seeds': seeds, 'seeds_distinct': len(set(seeds)) == len(seeds),
            'cells': r[0]['unit_cells']}


def main():
    d = json.load(open(F, encoding='utf-8'))
    rows = d['rows']
    a = {n: agg(rows, n) for n in ('zif71', 'zif90', 'zif93')}
    print('  ═══ T-NF-0k · 외부 골격 물 K_H (무한희석) ═══\n')
    print(f"  {'골격':8s} {'n':>2s}  {'평균 K_H':>12s}  {'±(95%CI)':>11s}  "
          f"{'실행 SD':>10s}  복제     씨앗독립")
    for n in ('zif71', 'zif90', 'zif93'):
        x = a[n]
        if not x:
            print(f'  {n:8s} — 결과 없음'); continue
        sd = f"{x['sd']:.3e}" if x['sd'] else '—'
        print(f"  {n:8s} {x['n']:2d}  {x['mean']:12.4e}  {x['pm']:11.3e}  {sd:>10s}  "
              f"{str(x['cells']):9s} {'예' if x['seeds_distinct'] else '**아니오**'}")
    if not all(a.values()):
        print('\n  판정 보류 — 결과가 다 안 들어왔습니다.'); return 1
    if not all(x['seeds_distinct'] for x in a.values()):
        print('\n  ⚠️ **씨앗 충돌** — 해당 골격의 반복은 독립이 아닙니다. 산포를 인용하지 마십시오.')

    # 우리 32조성 축과 나란히
    ax = os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome_seedfixed.json')
    if os.path.exists(ax):
        ours = [r['KH_water'] for r in json.load(open(ax, encoding='utf-8'))['rows']
                if r.get('KH_water')]
        print(f"\n  우리 32조성 축: {min(ours):.3e} ~ {max(ours):.3e}  ({max(ours)/min(ours):.0f} 배)")
        for n in ('zif71', 'zif90', 'zif93'):
            v = a[n]['mean']
            pos = ('**최저보다 아래**' if v < min(ours) else
                   '**최고보다 위**' if v > max(ours) else '축 안')
            print(f"    {n:8s} {v:.3e}  -> {pos}"
                  + (f" (최저의 {min(ours)/v:.1f}분의 1)" if v < min(ours) else ''))

    lo = min(a['zif90'], a['zif93'], key=lambda x: x['mean'])
    R = lo['mean'] / a['zif71']['mean']
    diff = lo['mean'] - a['zif71']['mean']
    comb = (lo['pm'] ** 2 + a['zif71']['pm'] ** 2) ** 0.5
    units = diff / comb if comb else float('inf')
    print(f"\n  ── 판정 (등록문 §6) ──")
    print(f"  친수 둘 중 **낮은 쪽**: {lo['name']} {lo['mean']:.4e}")
    print(f"  ZIF-93 대 ZIF-90 비: {max(a['zif90']['mean'],a['zif93']['mean'])/min(a['zif90']['mean'],a['zif93']['mean']):.2f} 배"
          f"  ({'**친수 축이 한 덩어리가 아닙니다 — 별도 관찰로 기록**' if max(a['zif90']['mean'],a['zif93']['mean'])/min(a['zif90']['mean'],a['zif93']['mean'])>=10 else '같은 덩어리'})")
    print(f"  **R = {R:.2f}**   차이 {diff:.4e} = **{units:.2f} 단위** (문턱 1.5)")
    if R >= 10 and units > 1.5:
        v = '**갈래 B** — 교차항은 순위를 맞춘다. 결함은 물–물 협동성 쪽'
    elif R < 3:
        v = '**갈래 A** — 교차항 자체가 약하다. 우리 조성의 물 수 전체가 계통 편향'
    else:
        v = ('**미결** — 판정하지 않는다. 후속은 씨앗 증설(자는 안 바꿈)'
             + ('  [R>=10 이나 1.5x± 미달]' if R >= 10 else '  [3 <= R < 10]'))
    print(f"  -> {v}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
