"""재계산 2단계 — structures_v2 의 Zeo++ + Widom K_H + 0.15 bar GCMC.

[왜 다시 하나 — STRUCTURE_DEFECT.md]
    기존 치환 구조가 전부 깨져 있었다(치환기가 이웃 고리 수소를 0.5~0.95 Å 관통).
    빌더를 고쳐 structures_v2/ 를 만들고 charged_v2/ 에 DDEC6 전하를 얹었다.
    이 스크립트가 그 위에서 Q_st·선택도·로딩을 다시 낸다.

[엔진은 재구현하지 않는다]
    run_aryl_gcmc.py 의 run_one/parse 를 그대로 쓰고 입출력 경로만 바꾼다.
    같은 규약(15000 사이클, UFF_MOF, DDEC6, 0.15 bar, 298 K)이어야 옛 결과와
    **무엇이 달라졌는지**를 말할 수 있다. 규약까지 같이 바꾸면 구조 때문인지
    설정 때문인지 구별할 수 없게 된다.

    ProcessPoolExecutor 는 리눅스에서 fork 라 여기서 덮어쓴 모듈 전역이
    자식에게 그대로 간다(run_candidate_gcmc.py 가 쓰는 것과 같은 방식).

[Zeo++ 를 여기서 같이 도는 이유]
    rebuild_index.json 에는 LCD/PLD/AV 가 없다. 옛 표와 나란히 놓으려면 필요하고,
    구조가 바뀌었으므로 옛 값을 재사용하면 안 된다.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg  # noqa: E402

# 입출력만 갈아 끼운다. 옛 aryl_runs/ 와 섞이면 어느 구조의 결과인지 알 수 없다.
rg.CHARGED = os.path.join(HERE, 'charged_v2')
rg.RUNS = os.path.join(HERE, 'runs_v2')
rg.MAX_WORKERS = int(os.environ.get('V2_WORKERS', '6'))

CHARGED = rg.CHARGED
RUNS = rg.RUNS
RESULT = os.path.join(HERE, 'results_v2.json')
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')
PROBE_R = 3.3 / 2      # CO2 운동직경의 절반. 기존 스캔과 같은 값


def zeo(cif):
    """LCD/PLD/AV. 실패하면 None 을 남긴다 — 0 으로 적으면 조용히 틀린 값이 된다."""
    out = {'LCD': None, 'PLD': None, 'AV': None}
    try:
        subprocess.run([NETWORK, '-ha', '-res', cif + '.res', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        v = open(cif + '.res').readline().split()
        out['LCD'], out['PLD'] = float(v[1]), float(v[2])
    except Exception as e:
        print(f'    [zeo res 실패] {os.path.basename(cif)}: {type(e).__name__}',
              flush=True)
    try:
        subprocess.run([NETWORK, '-ha', '-vol', f'{PROBE_R}', f'{PROBE_R}', '20000',
                        cif + '.vol', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       check=True, timeout=1800)
        m = re.search(r'(?<!N)AV_A\^3:\s*([0-9.eE+-]+)', open(cif + '.vol').read())
        if m:
            out['AV'] = float(m.group(1))
    except Exception as e:
        print(f'    [zeo vol 실패] {os.path.basename(cif)}: {type(e).__name__}',
              flush=True)
    return out


def main():
    ch = json.load(open(os.path.join(HERE, 'charged_v2.json'), encoding='utf-8'))
    tags = ch['charged']
    meta = {r['tag']: r for r in
            json.load(open(os.path.join(HERE, 'rebuild_index.json'),
                           encoding='utf-8'))}

    cifs = []
    for t in tags:
        p = os.path.join(CHARGED, t + '_DDEC6.cif')
        if os.path.exists(p):
            cifs.append(p)
        else:
            print(f'  [전하파일 없음] {t} — charge_v2.py 를 먼저 도세요')
    if not cifs:
        return 1

    print(f'구조 {len(cifs)}종. 먼저 Zeo++ (LCD/PLD/AV)\n', flush=True)
    geo = {}
    # Zeo++ 는 건당 수 GB 를 쓴다. 4워커 위로 올리면 빨라지는 게 아니라 죽는다
    # (risk_screen.py 67행: 8워커로 OOM, WSL 배포판이 통째로 먹통).
    with ProcessPoolExecutor(max_workers=4) as ex:
        for cif, g in zip(cifs, ex.map(zeo, cifs)):
            geo[os.path.basename(cif).replace('_DDEC6.cif', '')] = g

    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'\n{len(cifs)}종 x (Widom CO2 + Widom N2 + GCMC) = {len(jobs)}작업 '
          f'(워커 {rg.MAX_WORKERS})', flush=True)
    print(f'0.15 bar, 298 K, {rg.GCMC_CYCLES} 사이클, UFF_MOF, DDEC6 전하\n',
          flush=True)

    os.makedirs(RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=rg.MAX_WORKERS) as ex:
        for name, gas, mode, r, st in ex.map(rg._star, jobs):
            res.setdefault(name, {})[(mode, gas)] = r
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    print('\n' + '=' * 122)
    print(f'{"조성":<12} {"작용기":<8} {"LCD":>7} {"PLD":>7} {"AV":>8} '
          f'{"Qst (kJ/mol)":>17} {"CO2/N2":>16} {"0.15bar 로딩":>19}')
    print('-' * 122)
    rows = []
    for name in sorted(res):
        tag = name.replace('_DDEC6', '')
        kc = res[name].get(('widom', 'CO2'))
        kn = res[name].get(('widom', 'N2'))
        gc = res[name].get(('gcmc', 'CO2'))
        if not (kc and kn and gc) or kc[0] is None or kn[0] is None or gc[4] is None:
            print(f'{tag:<12} 출력 부족')
            rows.append({'name': tag, 'status': 'incomplete'})
            continue
        qst, eqst = -kc[2] - rg.R_GAS * rg.TEMP, kc[3]
        sel = kc[0] / kn[0]
        esel = sel * np.sqrt((kc[1] / kc[0]) ** 2 + (kn[1] / kn[0]) ** 2)
        g = geo.get(tag, {})
        m = meta.get(tag, {})
        print(f'{tag:<12} {m.get("group",""):<8} '
              f'{(g.get("LCD") or float("nan")):>7.3f} '
              f'{(g.get("PLD") or float("nan")):>7.3f} '
              f'{(g.get("AV") or float("nan")):>8.1f} '
              f'{qst:>10.2f} ± {eqst:<4.2f} {sel:>9.2f} ± {esel:<4.2f} '
              f'{gc[4]:>11.4f} ± {gc[5]:<6.4f}')
        rows.append({'name': tag, 'group': m.get('group'), 'frac': m.get('frac'),
                     'LCD': g.get('LCD'), 'PLD': g.get('PLD'), 'AV': g.get('AV'),
                     'KH_CO2': kc[0], 'KH_CO2_err': kc[1],
                     'KH_N2': kn[0], 'KH_N2_err': kn[1],
                     'selectivity': sel, 'selectivity_err': esel,
                     'Qst_CO2': qst, 'Qst_CO2_err': eqst,
                     'loading_015bar': gc[4], 'loading_015bar_err': gc[5],
                     'status': 'ok'})

    payload = {'source': 'structures_v2 + charged_v2 (STRUCTURE_DEFECT.md 이후)',
               'conditions': {'P_CO2_Pa': rg.PRESSURE, 'T_K': rg.TEMP,
                              'cycles': rg.GCMC_CYCLES, 'ff': 'UFF_MOF',
                              'charges': 'PACMAN DDEC6'},
               'rows': rows}
    # 전멸한 결과로 멀쩡한 결과를 덮지 않는다 (risk_screen.py 와 같은 방어).
    if not any(r.get('status') == 'ok' for r in rows) and os.path.exists(RESULT):
        alt = RESULT.replace('.json', '.allfail.json')
        json.dump(payload, open(alt, 'w', encoding='utf-8'), indent=2,
                  ensure_ascii=False)
        print(f'\n[중단] 전부 실패. 기존 결과를 지켰습니다 -> {os.path.basename(alt)}')
        return 1
    json.dump(payload, open(RESULT, 'w', encoding='utf-8'), indent=2,
              ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    print('\n주: 옛 결과(zif69_results.json / aryl_results.json)와 **직접 비교하지 '
          '마세요** — 저쪽은 깨진 구조에서 나왔습니다.')
    print('    차이가 1.5σ 미만이면 순위를 매기지 않습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
