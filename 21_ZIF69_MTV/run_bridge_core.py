"""T-BR-1 — CoRE 구조 12개를 **우리 프로토콜로** 다시 돌려 눈금 차이를 잰다.

등록: `BRIDGE_CORE_REGISTRATION_20260920.md` (자료 0건, 2026-09-20 21:34)

[무엇을 재나]
    같은 구조에 대한 CoRE 의 Widom K_H 와 우리 Widom K_H. 구조가 같으므로 차이는 **프로토콜 차이뿐**이다.
    이것이 `23_SCREENING/GATES23_20260920.md §3` 의 이전(transfer) 논증이 서 있는 가정을 직접 시험한다.

[우리 결과가 아니다]
    외부 계열 구조다. `results_v3.json` · `v3*` 어디에도 섞지 않는다. 태그는 전부 `bridge_`,
    결과는 `bridge_core_results.json` 한 곳에만 쓴다.

[코어 양보]
    지금 §AS Q_st(n) 사슬이 물리 8코어를 전부 쓰고 있다. 그쪽이 **등록된 우선 작업**이므로
    MAX_WORKERS=2 로 양보한다 (`run_candidate_gcmc.py` 머리말과 같은 판단). 기동은 `nice -n 19`.

[고정값을 바꾸지 않는다]
    사이클·힘장·CO2/N2 정의·전하·Ewald·컷오프 전부 `run_aryl_gcmc` 의 것 그대로.
    슈퍼셀만 **숫자가 아니라 규칙**(`unit_cells()`, 최소거리규약 >= 2x컷오프)을 쓴다 — 등록 §1 에 기록.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg  # noqa: E402

rg.MAX_WORKERS = 2
rg.RUNS = os.path.join(HERE, 'bridge_core_runs')

CIFS = os.path.join(HERE, 'bridge_core_cifs')
PICK = os.path.join(HERE, 'bridge_core_pick.json')
OUT = os.path.join(HERE, 'bridge_core_results.json')


def main():
    from concurrent.futures import ProcessPoolExecutor

    pick = json.load(open(PICK, encoding='utf-8'))
    cifs = []
    for p in pick:
        f = os.path.join(CIFS, p['file'])
        if os.path.exists(f):
            cifs.append(f)
        else:
            print(f"  [CIF 없음] {p['key']}", flush=True)
    if not cifs:
        return 1

    # Widom 만. GCMC 는 이 시험에 필요 없다(K_H 만 견준다).
    jobs = [(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
    print(f'T-BR-1  구조 {len(cifs)}종 x (Widom CO2 + Widom N2) = {len(jobs)}작업 '
          f'(MAX_WORKERS={rg.MAX_WORKERS}, nice 19, §AS 사슬과 코어 공유)', flush=True)

    os.makedirs(rg.RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=rg.MAX_WORKERS) as ex:
        for name, gas, mode, r, st in ex.map(rg._star, jobs):
            res.setdefault(name, {})[gas] = r
            print(f'  [{st:>9}] {gas:<3} {name}', flush=True)

    bykey = {os.path.splitext(p['file'])[0]: p for p in pick}
    rows = []
    for name in sorted(res):
        p = bykey.get(name, {})
        kc, kn = res[name].get('CO2'), res[name].get('N2')
        row = {
            'file': name + '.cif',
            'key': p.get('key'), 'set': p.get('set'), 'topo': p.get('topo'),
            'metal': p.get('metal'), 'PLD': p.get('PLD'), 'LCD': p.get('LCD'),
            'NAtoms': p.get('NAtoms'), 'N_super': p.get('N_super'), 'uc': p.get('uc'),
            'core_KH_CO2': p.get('KH_CO2'), 'core_selectivity': p.get('sel'),
            'status': 'ok',
        }
        # kc/kn = (kh, kh_err, dU, dU_err, load, load_err)
        if kc and kc[0] is not None:
            row['KH_CO2'], row['KH_CO2_err'] = kc[0], kc[1]
            row['dU_CO2'], row['dU_CO2_err'] = kc[2], kc[3]
        else:
            row['status'] = 'CO2 실패'
        if kn and kn[0] is not None:
            row['KH_N2'], row['KH_N2_err'] = kn[0], kn[1]
        else:
            row['status'] = ('둘 다 실패' if row['status'] != 'ok' else 'N2 실패')
        if row.get('KH_CO2') and row.get('KH_N2'):
            row['selectivity'] = row['KH_CO2'] / row['KH_N2']
        rows.append(row)

    json.dump({
        'test': 'T-BR-1',
        'registration': 'BRIDGE_CORE_REGISTRATION_20260920.md',
        'note': ('외부 계열(CoRE) 구조를 우리 프로토콜로 돌린 것. '
                 '우리 물질 결과가 아니며 results_v3.json 과 섞지 말 것.'),
        'protocol': {
            'widom_cycles': rg.WIDOM_CYCLES, 'widom_init': rg.WIDOM_INIT,
            'forcefield': 'UFF_MOF', 'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP,
            'charges': 'UseChargesFromCIFFile (CoRE CIF 의 PACMAN DDEC6)',
            'supercell': '숫자 고정이 아니라 unit_cells() 규칙 — 등록 §1',
        },
        'rows': rows,
    }, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ok = sum(1 for r in rows if r['status'] == 'ok')
    print(f'\n저장 {OUT}  —  {ok}/{len(rows)} 성공', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
