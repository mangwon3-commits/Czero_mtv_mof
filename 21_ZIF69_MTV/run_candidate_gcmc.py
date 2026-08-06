"""새 링커 후보(cf3Im025, cf3Im050, mslm025)만 대상으로 Widom CO2/N2 + 0.15 bar
GCMC를 돌린다. run_aryl_gcmc.py와 완전히 같은 조건(15000 사이클, UFF_MOF, DDEC6)을
쓰되, aryl_charged.json 전체(구 nbIm/mbIm/brbIm 9종 대기열 포함)를 건드리지
않도록 태그를 명시적으로 필터링한다 -- 그 9종은 이번 요청과 무관한 별도 작업이다.

[코어 공유 주의] 이 시점에 수분 경쟁 계산(run_water.py)이 8개 물리 코어를 이미
점유하고 있다. 그 계산이 이 프로젝트의 존폐 조건(ZIF-69 노선이 사는지 죽는지)이라
우선순위가 이쪽보다 높다. MAX_WORKERS를 낮춰 공존한다.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg  # noqa: E402

TARGET_TAGS = ['cf3Im025', 'cf3Im050', 'mslm025']
rg.MAX_WORKERS = 2
rg.RUNS = os.path.join(HERE, 'aryl_runs')


def main():
    import glob
    import json
    from concurrent.futures import ProcessPoolExecutor

    import numpy as np

    idx = {r['tag']: r for r in
           json.load(open(os.path.join(HERE, 'aryl_scan_index.json'), encoding='utf-8'))}

    cifs = []
    for t in TARGET_TAGS:
        p = os.path.join(rg.CHARGED, t + '_DDEC6.cif')
        if os.path.exists(p):
            cifs.append(p)
        else:
            print(f'  [전하파일 없음] {t}')
    if not cifs:
        return 1

    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'구조 {len(cifs)}종 x (Widom CO2 + Widom N2 + GCMC) = {len(jobs)}작업 '
          f'(MAX_WORKERS={rg.MAX_WORKERS}, 수분 경쟁과 코어 공유)', flush=True)

    os.makedirs(rg.RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=rg.MAX_WORKERS) as ex:
        for name, gas, mode, r, st in ex.map(rg._star, jobs):
            res.setdefault(name, {})[(mode, gas)] = r
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    rows = []
    for name in sorted(res):
        tag = name.replace('_DDEC6', '')
        kc = res[name].get(('widom', 'CO2'))
        kn = res[name].get(('widom', 'N2'))
        gc = res[name].get(('gcmc', 'CO2'))
        if not (kc and kn and gc) or kc[0] is None or kn[0] is None or gc[4] is None:
            print(f'{tag} 출력 부족')
            continue
        qst, eqst = -kc[2] - rg.R_GAS * rg.TEMP, kc[3]
        sel = kc[0] / kn[0]
        esel = sel * np.sqrt((kc[1] / kc[0]) ** 2 + (kn[1] / kn[0]) ** 2)
        g = idx.get(tag, {})
        rows.append({'name': tag, 'group': g.get('group'), 'frac': g.get('frac'),
                     'LCD': g.get('LCD'), 'PLD': g.get('PLD'), 'AV': g.get('AV'),
                     'KH_CO2': kc[0], 'KH_CO2_err': kc[1],
                     'KH_N2': kn[0], 'KH_N2_err': kn[1],
                     'selectivity': sel, 'selectivity_err': esel,
                     'Qst_CO2': qst, 'Qst_CO2_err': eqst,
                     'loading_015bar': gc[4], 'loading_015bar_err': gc[5]})
        print(f'{tag:<10} Qst={qst:.2f}+/-{eqst:.2f}  sel={sel:.2f}+/-{esel:.2f}  '
              f'loading={gc[4]:.4f}+/-{gc[5]:.4f}', flush=True)

    out_path = os.path.join(HERE, 'candidate_results.json')
    import json as _json
    with open(out_path, 'w', encoding='utf-8') as f:
        _json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {out_path}')
    print('비교 기준: ZIF-69 + SO3H 100% = Qst 31.07 +/- 0.72, 선택도 102.22 +/- 9.92, '
          '로딩 2.1556 +/- 0.0352 (미검증 -- 수분/안정성 계류중)')
    print('차이가 1.5시그마 미만이면 순위를 매기지 마세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
