"""지금까지의 모든 흡착 측정을 하나의 기계가독 데이터셋으로 모은다.

새 링커를 제안하려면 '무엇을 이미 시도했고 어떤 결과였는가'가 한자리에 있어야
한다. 결과가 디렉터리마다 흩어져 있고 일부는 주기경계 버그의 영향을 받았으므로,
여기서 **유효성 표시와 함께** 통합한다.

출력: evidence.json  (사람이 읽는 요약은 DESIGN_BRIEF.md)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')

# 주기경계 버그(커밋 7ce1d35 이전)의 영향을 받은 구조는 수치를 신뢰할 수 없다.
# 07_Bracketed 전체, 14_Strategies/StratB, 17_NestEffect 중 2종이 해당한다.
BUGGY_17 = {'amIm050_nIm050', 'mIm075_saIm025'}


def load(rel):
    p = os.path.join(ROOT, rel)
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def main():
    out = {
        'conditions': {
            'temperature_K': 298.0,
            'CO2_partial_pressure_bar': 0.15,
            'forcefield': 'UFF_MOF (DREIDING organics + UFF metals)',
            'charges': 'DDEC6 via PACMAN',
            'cutoff_A': 12.0,
            'note': 'Qst 는 Widom 삽입, 흡착량은 GCMC. 선택도는 K_H(CO2)/K_H(N2).',
        },
        'target': {
            'Qst_kJ_per_mol': [30, 40],
            'basis': '작업용량 모형 2종 독립 검증 (15_Target/optimal_qst.py). '
                     'TSA 최적 36, VSA 기준 27~29. 배가스 0.15 bar 기준.',
        },
        'measurements': [],
        'water_competition': [],
    }

    # --- 18_PoreNarrowing : 버그 수정 후 첫 정상 계산, 최우선 신뢰 ---
    for x in (load('18_PoreNarrowing/narrow_results.json') or []):
        out['measurements'].append({
            'source': '18_PoreNarrowing',
            'valid': True,
            'name': x['name'],
            'composition': x.get('label'),
            'phase': x.get('phase'),
            'Qst': x.get('Qst_CO2'),
            'selectivity_CO2_N2': x.get('selectivity'),
            'loading_015bar_molkg': x.get('loading_015bar'),
            'LCD_A': x.get('LCD'),
            'PLD_A': x.get('PLD'),
            'AV_per_cell_A3': x.get('AV_per_cell'),
        })

    # --- 17_NestEffect : 2종은 버그 영향 ---
    for x in (load('17_NestEffect/ddec6_results.json') or []):
        out['measurements'].append({
            'source': '17_NestEffect',
            'valid': x['name'] not in BUGGY_17,
            'invalid_reason': ('주기경계 버그 구조' if x['name'] in BUGGY_17 else None),
            'name': x['name'],
            'phase': 'closed',
            'Qst': x.get('Qst_CO2'),
            'selectivity_CO2_N2': x.get('selectivity'),
            'loading_015bar_molkg': x.get('loading_015bar'),
        })

    # --- 19_WaterCompetition ---
    for x in (load('19_WaterCompetition/water_results.json') or []):
        out['water_competition'].append({
            'name': x['name'], 'RH': x['RH'],
            'CO2_molkg': x.get('CO2_molkg'), 'H2O_molkg': x.get('H2O_molkg'),
            'CO2_retention_pct': x.get('CO2_retention_pct'),
        })

    # --- 공동 크기 모형 ---
    out['cavity_model'] = {
        'script': '20_ParentScan/cavity_model.py',
        'method': '골격 원자를 반지름 R 구면에 두고 LJ 12-6 을 구면적분. '
                  '무한 평면 벽 대비 배율이라 표면밀도와 eps 가 소거된다.',
        'optimum_LCD_A': [4.0, 4.5],
        'enhancement_at_optimum_vs_ZIF8': 2.47,
        'predicted_Qst_pure_framework': 34.6,
        'ZIF8_LCD_A': 11.39,
        'caveat': 'CO2 는 길이 5.4 A 선형 분자라 좁은 공동에서 배향이 제한된다. '
                  '엔트로피 손실을 모형이 못 보므로 엔탈피 상한으로 읽어야 한다.',
    }

    # --- 라이브러리에 이미 있는 리간드 ---
    lib = os.path.join(ROOT, '05_MTV_Ligand_Library', 'mtv_cif_builder.py')
    smiles = {}
    try:
        src = open(lib, encoding='utf-8').read()
        block = re.search(r'LIGAND_LIBRARY\s*=\s*\{(.*?)\}', src, re.S)
        if block:
            for k, v in re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', block.group(1)):
                smiles[k] = v
    except Exception:
        pass
    out['existing_ligands'] = smiles

    with open(os.path.join(HERE, 'evidence.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    n_ok = sum(1 for m in out['measurements'] if m['valid'])
    print(f'측정 {len(out["measurements"])}건 (유효 {n_ok})')
    print(f'수분 경쟁 {len(out["water_competition"])}건')
    print(f'기존 리간드 {len(smiles)}종: {", ".join(sorted(smiles))}')
    print(f'-> {os.path.join(HERE, "evidence.json")}')

    print('\n=== 유효 측정, Qst 순 ===')
    for m in sorted([m for m in out['measurements'] if m['valid'] and m.get('Qst')],
                    key=lambda r: -r['Qst']):
        print(f'  {m["name"]:<34} {m.get("phase") or "":<7} '
              f'Qst {m["Qst"]:>6.2f}  sel {m["selectivity_CO2_N2"]:>6.2f}  '
              f'load {m["loading_015bar_molkg"]:>7.4f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
