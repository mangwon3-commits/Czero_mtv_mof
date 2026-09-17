"""v3 2단계 — 이완된 구조의 Zeo++ + Widom K_H + 0.15 bar GCMC.

[v2 와 무엇이 같고 무엇이 다른가]
    **엔진과 규약은 한 글자도 바꾸지 않습니다.** 15000 사이클, UFF_MOF, DDEC6,
    0.15 bar, 298 K. 바뀐 것은 입력 구조뿐입니다 -- 그래야 v2 와 v3 의 차이를
    **"이완 때문"** 이라고 말할 수 있습니다. 규약까지 같이 바꾸면 구조 때문인지
    설정 때문인지 구별할 수 없게 됩니다. run_gcmc_v2.py 가 v1 대비 지켰던
    원칙 그대로입니다.

    Zeo++ 도 다시 돕니다. 기하가 바뀌었으므로 v2 의 LCD/PLD/AV 를 재사용하면
    안 됩니다.

[전역 덮어쓰기 순서에 주의]
    run_gcmc_v2 를 import 하는 순간 그 모듈이 rg.CHARGED 를 charged_v2 로
    설정합니다. **그러므로 import 뒤에 다시 덮어써야 합니다.** 순서가 뒤집히면
    v3 실행이 조용히 v2 구조를 읽습니다 -- 이 프로젝트에서 가장 무서운 종류의
    실패(실패가 결과처럼 보이는 것)입니다. 그래서 아래에서 실제 경로를 찍습니다.

    ProcessPoolExecutor 는 리눅스에서 fork 라 여기서 덮어쓴 전역이 자식에게
    그대로 갑니다.

사용:
    python run_gcmc_v3.py                     전체
    python run_gcmc_v3.py --only base --out results_v3_smoke.json
                                              한 종만 -- 밤샘 전 연기 시험용
"""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg          # noqa: E402
import run_gcmc_v2 as v2            # noqa: E402  (zeo() 를 그대로 쓴다)

# ---- import 이후에 덮어쓴다. 위 주석 참조. ----
rg.CHARGED = os.path.join(HERE, 'charged_v3')
rg.RUNS = os.path.join(HERE, 'runs_v3')
rg.MAX_WORKERS = int(os.environ.get('V3_WORKERS', '6'))
CHARGED = rg.CHARGED
RUNS = rg.RUNS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*', default=None,
                    help='태그 몇 개만 (연기 시험)')
    ap.add_argument('--out', default='results_v3.json')
    a = ap.parse_args()
    RESULT = os.path.join(HERE, a.out)

    ch = json.load(open(os.path.join(HERE, 'charged_v3.json'), encoding='utf-8'))
    tags = ch['charged']
    if a.only:
        tags = [t for t in tags if t in a.only]
        if not tags:
            print(f'  --only {a.only} 에 해당하는 태그가 없습니다. 있는 것: {ch["charged"][:5]}...')
            return 1
    meta = {r['tag']: r for r in
            json.load(open(os.path.join(HERE, 'rebuild_index.json'),
                           encoding='utf-8'))}

    cifs = []
    for t in tags:
        p = os.path.join(CHARGED, t + '_DDEC6.cif')
        if os.path.exists(p):
            cifs.append(p)
        else:
            print(f'  [전하파일 없음] {t} — charge_v3.py 를 먼저 도세요')
    if not cifs:
        return 1

    # 조용한 경로 오염을 막는 확인. 눈으로 볼 수 있게 찍습니다.
    print(f'  구조 폴더 {rg.CHARGED}')
    print(f'  실행 폴더 {rg.RUNS}')
    print(f'  결과 파일 {RESULT}')
    assert rg.CHARGED.endswith('charged_v3'), 'v3 경로가 덮어써지지 않았습니다'
    assert rg.RUNS.endswith('runs_v3'), 'v3 경로가 덮어써지지 않았습니다'

    # [08-12 먹통 조합을 여기서 막는다]
    #   Zeo++ 는 v3 구조에서 건당 **9.5 GB** 입니다(08-19 실측). 아래 계산도
    #   그 값을 씁니다. [2026-08-22 정정] 이 주석은 08-12 사고 당시의 v1 값
    #   3.2 GB 를 적고 있었는데, 바로 아래 코드는 이미 9.5 로 고쳐진 상태였습니다
    #   -- 코드와 주석이 서로 다른 것을 가르치고 있었습니다.
    #   8워커가 OOM 을 냈고 dbus-daemon 까지 죽어
    #   WSL 배포판이 통째로 먹통이 됐습니다(밖에서 wsl --shutdown 해야 복구).
    #   boost.sh 의 규칙 1 은 아예 **"RASPA 가 돌 때 Zeo++ 를 띄우지 말라"** 입니다.
    #
    #   그런데 이 스크립트는 무인으로 돕니다. v3 GCMC 가 시작될 때 수분 v2 의
    #   마지막 RASPA 작업이 아직 20시간쯤 남아 있을 수 있고, 그러면 정확히
    #   그 금지된 조합이 됩니다. 사람이 볼 수 없으니 코드가 재고 정합니다.
    #   메모리는 /proc/meminfo 를 직접 읽습니다. `free | awk '{print $7}'` 를
    #   subprocess 로 부르면 셸 계층이 하나 더 끼고, 거기서 $7 이 먹히면 awk 가
    #   행 전체를 뱉어 int() 가 터집니다. 무인 실행 중에 그러면 90작업이 통째로
    #   죽습니다. 파싱 실패가 계산을 못 죽이게 예외까지 막아 둡니다.
    try:
        n_raspa = len(subprocess.run(['pgrep', '-x', 'simulate'],
                                     capture_output=True, text=True).stdout.split())
    except Exception:                                        # noqa: BLE001
        n_raspa = 1          # 모르면 RASPA 가 도는 쪽으로 가정(안전한 방향)
    free_gb = 0
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                free_gb = int(line.split()[1]) // (1024 * 1024)
                break
    except Exception:                                        # noqa: BLE001
        free_gb = 8
    # [2026-08-22] 건당 4 GB 가정을 실측 9.5 GB 로 바꿉니다.
    #
    #   이 줄의 4 는 v1 구조에서 잰 3.2 GB 시절 상수를 올림한 값입니다.
    #   v3 는 이완으로 셀이 34% 수축해 슈퍼셀 원자 수가 늘었고 실측이
    #   9.5 GB/건이었습니다(CLAUDE.md 5절, 08-19 랩탑). 4 를 믿으면 가용
    #   15 GB 에서 워커 2 가 나오고 2 x 9.5 = 19 GB 를 요구합니다 --
    #   08-12 에 OOM 이 dbus 까지 죽여 WSL 을 통째로 먹통으로 만든 그
    #   조합입니다. risk_screen_v3 는 이미 ZEO_GB_PER_JOB 으로 덮게
    #   돼 있었는데 이 러너만 빠져 있었습니다.
    ZEO_GB = float(os.environ.get('ZEO_GB_PER_JOB', '9.5'))
    zw = 4 if n_raspa == 0 else 2
    zw = min(zw, max(1, int((free_gb - 4) // ZEO_GB)))   # 여유에서 4 GB 는 남긴다
    print(f'\n구조 {len(cifs)}종. 먼저 Zeo++ (LCD/PLD/AV)')
    print(f'  RASPA {n_raspa}건 가동 중, 메모리 여유 {free_gb} GB '
          f'-> Zeo++ 워커 {zw}\n', flush=True)
    geo = {}
    with ProcessPoolExecutor(max_workers=zw) as ex:
        for cif, g in zip(cifs, ex.map(v2.zeo, cifs)):
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
        qst, eqst = -kc[2] + rg.R_GAS * rg.TEMP, kc[3]  # Q_st = −ΔU + RT (RASPA dH 정의; 09-18 부호 정정, 21_ZIF69_MTV/QST_RT_SIGN_20260911.md)
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

    payload = {'source': 'relax_v3 + charged_v3 (GFN-FF 셀 고정 이완 이후)',
               'conditions': {'P_CO2_Pa': rg.PRESSURE, 'T_K': rg.TEMP,
                              'cycles': rg.GCMC_CYCLES, 'ff': 'UFF_MOF',
                              'charges': 'PACMAN DDEC6',
                              'geometry': 'GFN-FF relaxed, cell fixed'},
               'rows': rows}
    # 전멸한 결과로 멀쩡한 결과를 덮지 않습니다.
    if not any(r.get('status') == 'ok' for r in rows) and os.path.exists(RESULT):
        alt = RESULT.replace('.json', '.allfail.json')
        json.dump(payload, open(alt, 'w', encoding='utf-8'), indent=2,
                  ensure_ascii=False)
        print(f'\n[중단] 전부 실패. 기존 결과를 지켰습니다 -> {os.path.basename(alt)}')
        return 1
    json.dump(payload, open(RESULT, 'w', encoding='utf-8'), indent=2,
              ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    print('\n주: v2 와의 차이는 **이완 때문**입니다 — 규약은 동일합니다.')
    print('    차이가 1.5σ 미만이면 순위를 매기지 않습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
