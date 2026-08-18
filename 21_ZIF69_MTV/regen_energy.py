"""재생 에너지 수지 — TSA·VSA·전처리 건조를 mol CO2 당 kJ 하나로 비교한다.

[이것은 시뮬레이션이 아닙니다]
    GCMC 로 얻은 작업 용량 위에 얹는 **공정 수준 에너지 수지**다. 가정이 결과를
    지배하므로, 숫자 하나를 내는 것이 목적이 아니라 **어느 가정에서 결론이
    뒤집히는지**를 내는 것이 목적이다. 감도분석 없이 이 숫자를 인용하면 안 된다.

[왜 필요한가]
    Q_st 만으로는 TSA 와 VSA 를 비교할 수 없다. TSA 는 흡착제를 통째로 데워야
    하고(현열), VSA 는 진공 일을 해야 한다. 단위가 다르므로 mol CO2 당 kJ 이라는
    공통 잣대에 올려야 "건조가 값싼가"를 물을 수 있다.

[항]
    1. 탈착 엔탈피    Q_st                        [kJ/mol CO2]
    2. 현열 (TSA)     Cp x dT / WC
       흡착제 1 kg 을 dT 만큼 데우는 비용을 **그 사이클에 실어 나른 CO2 로 나눈다.**
       그래서 작업 용량이 큰 조성이 여기서 유리해진다 -- 같은 난방비를 더 많은
       CO2 에 분산시키기 때문이다.
    3. 진공 일 (VSA)  RT ln(p1/p2)
       **등온 가역 하한이다.** 실제 진공펌프는 이보다 몇 배 크고, 무엇보다 이 식은
       기공 밖 불활성 기체(N2 85%)를 빼내는 일을 세지 않는다. 하한으로만 읽을 것.
    4. 건조 잠열      dH_vap x (n_H2O / n_CO2)
       배가스에서 물을 응축시키는 비용. 잡아내는 CO2 1 mol 당 처리해야 하는
       기체량이 회수율에 반비례하므로, **회수율이 낮으면 건조비가 폭증한다.**

[읽는 법]
    절대값보다 **순위와 뒤집힘 지점**이 결과다. 특히 골격 비열은 이 계열의 실측이
    없어 문헌 대푯값을 쓴다 -- 이 값 하나가 TSA 총액의 절반 이상을 좌우한다.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = 8.314462618e-3        # kJ/(mol K)

# ---- 가정 (전부 여기 모아 둔다. 흩어 두면 감도분석이 불가능해진다) ----
CP_FRAMEWORK = 0.9        # J/(g K). MOF 대푯값. 실측 없음 -> 감도분석 대상
CP_RANGE = (0.6, 1.2)
T_ADS, T_DES = 298.0, 373.0
DH_VAP = 44.0             # kJ/mol, 298 K 물
P_CO2_FEED = 0.15         # bar
P_H2O_FEED = 0.028521     # bar (RH 90% @ 298 K)
RECOVERY = 0.50           # 통과 CO2 중 잡아내는 비율. 감도분석 대상
RECOVERY_RANGE = (0.30, 0.90)
HEAT_RECOVERY = 0.0       # 열교환 회수율. 0 = 보수적 하한

QST = {'base': 21.08, 'saIm050': 25.17, 'saIm075': 26.63}


def sensible(wc, cp=CP_FRAMEWORK, dT=T_DES - T_ADS, recov=HEAT_RECOVERY):
    """흡착제를 데우는 비용을 mol CO2 당으로 환산. wc [mol/kg]."""
    if not wc:
        return float('inf')
    per_kg = cp * 1000.0 * dT / 1000.0        # J/(g K) x 1000 g x K -> kJ/kg
    return per_kg * (1.0 - recov) / wc


def vacuum_work(p_hi=P_CO2_FEED, p_lo=0.05, T=T_ADS):
    """등온 가역 압축 일. **하한이다.**"""
    return R * T * math.log(p_hi / p_lo)


def drying(recov=RECOVERY):
    """배가스를 말리는 잠열. 잡은 CO2 1 mol 당."""
    n_ratio = P_H2O_FEED / P_CO2_FEED         # 공급 기체의 물/CO2 몰비
    return DH_VAP * n_ratio / recov


def load_wc():
    dry = json.load(open(os.path.join(HERE, 'working_capacity.json'),
                         encoding='utf-8'))
    out = {r['name']: {'dry_tsa': r['working_capacity']['tsa']['value'],
                       'dry_vsa': r['working_capacity']['vsa05']['value']}
           for r in dry['rows']}
    p = os.path.join(HERE, 'humid_working_capacity.json')
    if os.path.exists(p):
        for r in json.load(open(p, encoding='utf-8'))['rows']:
            w = r.get('working_capacity', {})
            if 'tsa' in w:
                out.setdefault(r['name'], {})['wet_tsa'] = w['tsa']['value']
            if 'vsa' in w:
                out.setdefault(r['name'], {})['wet_vsa'] = w['vsa']['value']
    return out


def main():
    wc = load_wc()
    names = [n for n in ('base', 'saIm050', 'saIm075') if n in wc]

    print('=== 가정 ===')
    print(f'  골격 비열      {CP_FRAMEWORK} J/(g K)   [감도 {CP_RANGE[0]}~{CP_RANGE[1]}]')
    print(f'  승온           {T_ADS:.0f} -> {T_DES:.0f} K')
    print(f'  열교환 회수    {HEAT_RECOVERY*100:.0f}%  (보수적 하한)')
    print(f'  CO2 회수율     {RECOVERY*100:.0f}%       [감도 {RECOVERY_RANGE[0]*100:.0f}~{RECOVERY_RANGE[1]*100:.0f}%]')
    print(f'  물/CO2 몰비    {P_H2O_FEED/P_CO2_FEED:.4f}  (RH90 @ 298 K)')
    print(f'  물 증발엔탈피  {DH_VAP} kJ/mol')
    print()

    vw = vacuum_work()
    dry_cost = drying()
    print(f'  진공 일 (0.15 -> 0.05 bar, 등온 가역)  {vw:.2f} kJ/mol  ** 하한 **')
    print(f'  건조 잠열 (회수율 {RECOVERY*100:.0f}%)              {dry_cost:.2f} kJ/mol')
    print()

    print('=== mol CO2 당 재생 에너지 (kJ) ===')
    hdr = (f'{"조성":<9}{"WC":>8}{"Q_st":>8}{"현열":>8}{"진공":>8}'
           f'{"건조":>8}{"합계":>9}')
    for mode in ('tsa', 'vsa'):
        print(f'\n  [{mode.upper()}]')
        print('  ' + hdr)
        print('  ' + '-' * 58)
        for variant, label in (('wet', '젖은 채'), ('dry', '말려서')):
            key = f'{variant}_{mode}'
            for n in names:
                v = wc[n].get(key)
                if v is None:
                    continue
                q = QST[n]
                sh = sensible(v) if mode == 'tsa' else 0.0
                vac = vw if mode == 'vsa' else 0.0
                dc = dry_cost if variant == 'dry' else 0.0
                tot = q + sh + vac + dc
                print(f'  {n + "(" + label + ")":<9}{v:>8.4f}{q:>8.2f}'
                      f'{sh:>8.2f}{vac:>8.2f}{dc:>8.2f}{tot:>9.2f}')

    print('\n=== 감도: 골격 비열 (TSA 합계, 젖은 채) ===')
    print(f'  {"Cp":<8}' + ''.join(f'{n:>12}' for n in names))
    for cp in (CP_RANGE[0], CP_FRAMEWORK, CP_RANGE[1]):
        line = f'  {cp:<8.1f}'
        for n in names:
            v = wc[n].get('wet_tsa') or wc[n].get('dry_tsa')
            line += f'{QST[n] + sensible(v, cp=cp):>12.2f}'
        print(line)

    print('\n=== 감도: 회수율 (말려서 쓸 때의 건조 잠열) ===')
    for rc in (RECOVERY_RANGE[0], RECOVERY, RECOVERY_RANGE[1]):
        print(f'  회수율 {rc*100:>4.0f}%  ->  건조 {drying(rc):>6.2f} kJ/mol')

    out = {'assumptions': {
        'Cp_framework_J_gK': CP_FRAMEWORK, 'Cp_range': list(CP_RANGE),
        'T_ads_K': T_ADS, 'T_des_K': T_DES,
        'heat_recovery': HEAT_RECOVERY, 'recovery': RECOVERY,
        'recovery_range': list(RECOVERY_RANGE),
        'dH_vap_kJ_mol': DH_VAP, 'p_co2_bar': P_CO2_FEED,
        'p_h2o_bar': P_H2O_FEED},
        'vacuum_work_kJ_mol_lower_bound': round(vw, 3),
        'drying_kJ_mol': round(dry_cost, 3),
        'rows': []}
    for n in names:
        e = {'name': n, 'Q_st': QST[n], 'wc': wc[n]}
        for mode in ('tsa', 'vsa'):
            for variant in ('wet', 'dry'):
                v = wc[n].get(f'{variant}_{mode}')
                if v is None:
                    continue
                e[f'{variant}_{mode}_kJ_per_mol'] = round(
                    QST[n] + (sensible(v) if mode == 'tsa' else 0.0)
                    + (vw if mode == 'vsa' else 0.0)
                    + (dry_cost if variant == 'dry' else 0.0), 2)
        out['rows'].append(e)
    with open(os.path.join(HERE, 'regen_energy.json'), 'w',
              encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print('\n[OK] regen_energy.json')
    print('\n주: 진공 일은 등온 가역 하한이며 불활성 기체 배기를 세지 않습니다.')
    print('    골격 비열은 이 계열의 실측이 없는 문헌 대푯값입니다.')
    print('    **감도분석 없이 위 합계를 인용하지 마세요.**')
    return 0


if __name__ == '__main__':
    sys.exit(main())
