"""엔트로피 분해 + 대리모델용 특성 행렬 작성.

[핵심] 흡착 엔트로피는 별도로 계산해야 하는 '누락 항'이 아니다.
    Widom/GCMC는 삽입 분자의 위치와 '배향'을 모두 볼츠만 평균하므로
        K_H ∝ <exp(-βU)>_{위치, 배향}
    이 평균 자체가 배향 엔트로피를 이미 포함한다. 따라서 K_H(자유에너지)와
    Q_st(엔탈피)를 함께 쓰면 엔트로피 항을 역산할 수 있다:

        ΔΔG = -RT ln(K_H,A / K_H,B)      (A가 B보다 유리하면 음수)
        ΔΔH = -(Q_st,A - Q_st,B)          (Q_st는 양수로 정의된 흡착열)
        TΔΔS = ΔΔH - ΔΔG

    VTK 밀도맵으로는 이걸 할 수 없다 -- RASPA의 DensityProfile은 스칼라
    점유 밀도(위치)이고 배향 정보를 담지 않는다. 배향 분포를 보려면 궤적을
    덤프해 O=C=O 축의 각도 분포를 따로 계산해야 한다.
"""
import json
import os

R = 8.314462618e-3   # kJ/mol/K
T = 298.0

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


widom = {r['name']: r for r in load(os.path.join(ROOT, '07_Bracketed_MTV', 'widom_results.json'))}
gcmc = {r['name']: r for r in load(os.path.join(ROOT, '10_DensityMap',
                                                'electrostatic_decomposition.json'))}
brack = load(os.path.join(ROOT, '07_Bracketed_MTV', 'bracketed_index.json'))

# 조성 -> Zeo++ 기하 (닫힌/열린)
geom = {}
for e in brack:
    tag = '_'.join(f'{k}{int(v*100):03d}' for k, v in sorted(e['composition'].items()))
    for ph, d in e['phases'].items():
        geom[f'{tag}__{ph}'] = d


def charge_stats(cif):
    """CIF의 _atom_site_charge 컬럼에서 부분전하 통계를 뽑는다."""
    import statistics
    lines = open(cif, encoding='utf-8', errors='ignore').read().split('\n')
    tags = [i for i, l in enumerate(lines) if l.strip().startswith('_atom_site')]
    if not tags:
        return None
    names = [lines[i].strip() for i in tags]
    try:
        col = names.index('_atom_site_charge')
    except ValueError:
        return None
    q = []
    for l in lines[tags[-1] + 1:]:
        p = l.split()
        if len(p) <= col:
            continue
        try:
            q.append(float(p[col]))
        except ValueError:
            continue
    if len(q) < 2:
        return None
    return {'q_var': statistics.pvariance(q), 'q_std': statistics.pstdev(q),
            'q_absmax': max(abs(x) for x in q), 'q_sum': sum(q), 'n': len(q)}


print('=' * 100)
print('1. 엔트로피 분해 -- 순수 ZIF-8 기준, 같은 상(phase)끼리 비교')
print('=' * 100)
print(f'{"구조":<32} {"KH":>11} {"Qst":>7} {"ddG":>8} {"ddH":>8} {"TddS":>8}  해석')
print('-' * 100)

ent_rows = []
for ph in ('closed', 'open'):
    ref = widom.get(f'mIm100__{ph}')
    if not ref:
        continue
    for name, w in sorted(widom.items()):
        if not name.endswith('__' + ph):
            continue
        ddG = -R * T * __import__('math').log(w['KH_CO2'] / ref['KH_CO2'])
        ddH = -(w['Qst_CO2'] - ref['Qst_CO2'])
        TddS = ddH - ddG
        note = ''
        if name != f'mIm100__{ph}':
            note = ('엔트로피 유리' if TddS > 0.2 else
                    ('엔트로피 불리' if TddS < -0.2 else '엔트로피 중립'))
        print(f'{name:<32} {w["KH_CO2"]:>11.4e} {w["Qst_CO2"]:>7.2f} '
              f'{ddG:>8.3f} {ddH:>8.3f} {TddS:>8.3f}  {note}')
        ent_rows.append({'name': name, 'phase': ph, 'ddG': round(ddG, 4),
                         'ddH': round(ddH, 4), 'TddS': round(TddS, 4)})
    print()

# Cl vs NO2 직접 대결
print('-' * 100)
print('Cl vs NO2 직접 비교 (동일 치환율, 동일 상)')
print('-' * 100)
import math
for ph in ('closed', 'open'):
    for lvl, a, b in [('50%', f'clIm050_mIm050__{ph}', f'mIm050_nIm050__{ph}'),
                      ('25%', f'clIm025_mIm075__{ph}', f'mIm075_nIm025__{ph}')]:
        wa, wb = widom.get(a), widom.get(b)
        if not (wa and wb):
            continue
        ddG = -R * T * math.log(wa['KH_CO2'] / wb['KH_CO2'])
        ddH = -(wa['Qst_CO2'] - wb['Qst_CO2'])
        TddS = ddH - ddG
        print(f'  [{ph:<6} {lvl}] Cl 대비 NO2:  ddG={ddG:+.3f}  ddH={ddH:+.3f}  '
              f'TddS={TddS:+.3f} kJ/mol')
        print(f'{"":15} -> Cl이 자유에너지 {-ddG:+.3f} 유리, 그중 엔탈피 기여 {-ddH:+.3f}, '
              f'엔트로피 기여 {TddS:+.3f}')

# 특성 행렬
print()
print('=' * 100)
print('2. 대리모델 입력 특성 행렬')
print('=' * 100)
rows = []
for name in sorted(gcmc):
    g = gcmc[name]
    w = widom.get(name, {})
    z = geom.get(name, {})
    cif = os.path.join(ROOT, '07_Bracketed_MTV', name + '.cif')
    cs = charge_stats(cif) if os.path.exists(cif) else None
    rows.append({
        'name': name, 'phase': g['phase'],
        'q_var': round(cs['q_var'], 5) if cs else None,
        'q_absmax': round(cs['q_absmax'], 4) if cs else None,
        'VF': z.get('VF'), 'AV_A3': z.get('AV'), 'PLD': z.get('PLD'),
        'KH_CO2': w.get('KH_CO2'), 'Qst_CO2': w.get('Qst_CO2'),
        'selectivity': w.get('selectivity'),
        'loading_q_on': g['q_on'], 'loading_q_off': g['q_off'],
        'electrostatic_pct': g['electrostatic_pct'],
        'steric_pct': g['steric_pct'], 'net_pct': g['net_vs_pristine_pct'],
    })

hdr = f'{"구조":<32} {"q_var":>8} {"VF":>7} {"PLD":>6} {"정전기%":>8} {"KH":>11} {"sel":>7}'
print(hdr)
print('-' * 100)
for r in rows:
    print(f'{r["name"]:<32} {r["q_var"] if r["q_var"] is not None else 0:>8.5f} '
          f'{r["VF"] or 0:>7.4f} {r["PLD"] or 0:>6.3f} {r["electrostatic_pct"]:>7.1f}% '
          f'{r["KH_CO2"] or 0:>11.4e} {r["selectivity"] or 0:>7.2f}')

import csv
out = os.path.join(HERE, 'surrogate_feature_matrix.csv')
with open(out, 'w', newline='', encoding='utf-8-sig') as f:
    w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w_.writeheader()
    w_.writerows(rows)
with open(os.path.join(HERE, 'entropy_decomposition.json'), 'w', encoding='utf-8') as f:
    json.dump(ent_rows, f, indent=2, ensure_ascii=False)
print(f'\n[OK] 저장: {out}')

# 상관계수 (N=14이므로 탐색적 참고용)
print()
print('상관계수 (N=%d, 탐색적 참고용 -- 학습용 표본 수로는 크게 부족)' % len(rows))
print('-' * 60)
import statistics


def corr(xs, ys):
    xs = [x for x in xs]
    ys = [y for y in ys]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    return num / den if den else float('nan')


valid = [r for r in rows if r['q_var'] is not None and r['KH_CO2']]
for feat in ('q_var', 'q_absmax', 'VF', 'PLD', 'electrostatic_pct'):
    xs = [r[feat] or 0 for r in valid]
    print(f'  {feat:<20} vs KH_CO2      r = {corr(xs, [r["KH_CO2"] for r in valid]):+.3f}')
    print(f'  {"":<20} vs selectivity r = {corr(xs, [r["selectivity"] for r in valid]):+.3f}')
