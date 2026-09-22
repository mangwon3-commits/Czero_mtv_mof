# -*- coding: utf-8 -*-
"""§AW — CoRE 72종의 **CO₂ 등온 2점(0.15 / 0.01 bar)** 을 우리 프로토콜로. 작업 용량 축을 연다.

등록: `COREWC_REGISTRATION_20260923.md` (자료 0건)

[왜]
    D8(`23_SCREENING/D8_GEMC_IS_WATER_20260921.md §5`)이 **"작업 용량 축만은 닫혀 있다"** 로 끝났습니다 —
    CoRE 에 **CO₂ 등온선이 아예 없기 때문**입니다(노트북이 쓰던 것은 물 등온선이었습니다).
    §AV 가 K_H·선택도 축을 우리 자로 열었으니, 남은 것은 **우리가 CO₂ 등온선을 직접 계산하는 것**뿐입니다.

[압력 둘]
    0.15 bar  배가스 CO₂ 분압 — **우리 31조성의 `loading_015bar` 와 같은 조건**이라 바로 견줍니다
    0.01 bar  진공 탈착 — 둘의 차가 VSA 작업 용량

[★ 실행 폴더가 압력별로 갈라져야 합니다]
    `run_aryl_gcmc.run_one` 의 실행 폴더 이름은 `{mode}_{gas}_{name}` 이라 **압력이 안 들어갑니다.**
    두 압력을 같은 뿌리에서 돌리면 **이어받기가 서로를 완주분으로 회수합니다**(CLAUDE.md §3 의 함정).
    그래서 압력마다 `core_wc_runs_p<압력>` 로 뿌리를 가릅니다.

[환경 변수]  COREWC_ASSIGN(필수) · COREWC_MACHINE(기본=ASSIGN) · COREWC_WORKERS · COREWC_PICK · COREWC_OUT
[이어받기]   실행폴더 + 결과 JSON 양쪽. 프로토콜이 다르면 거부합니다.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg  # noqa: E402

ASSIGN = os.environ.get('COREWC_ASSIGN', '').strip()
MACHINE = os.environ.get('COREWC_MACHINE', '').strip() or ASSIGN
WORKERS = int(os.environ.get('COREWC_WORKERS', '8'))
CIFS = os.path.join(HERE, 'core_pop_cifs')
PICK = os.environ.get('COREWC_PICK') or os.path.join(HERE, 'core_wc_pick.json')
OUT = os.environ.get('COREWC_OUT') or os.path.join(HERE, f'core_wc_results_{ASSIGN}.json')
PRESSURES = [0.15, 0.01]          # bar — 등록 §1. 바꾸지 마십시오.

rg.MAX_WORKERS = WORKERS
PROTOCOL = {
    'gcmc_cycles': rg.GCMC_CYCLES, 'gcmc_init': rg.GCMC_INIT,
    'forcefield': 'UFF_MOF', 'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP,
    'pressures_bar': PRESSURES,
    'charges': 'UseChargesFromCIFFile (CoRE CIF 의 PACMAN DDEC6)',
    'supercell': '숫자 고정이 아니라 unit_cells() 규칙',
    'co2': 'García-Sánchez 2009 (경로는 TraPPE/CO2.def 지만 TraPPE 가 아님 — CLAUDE.md §1)',
}


def load_prior():
    if not os.path.exists(OUT):
        return {}
    d = json.load(open(OUT, encoding='utf-8'))
    if d.get('protocol') != PROTOCOL:
        print('!! 기존 결과의 프로토콜이 다릅니다 — 이어받지 않습니다.', flush=True)
        sys.exit(4)
    return {r['file']: r for r in d.get('rows', [])}


def write(rows):
    json.dump({'test': '§AW core-wc', 'registration': 'COREWC_REGISTRATION_20260923.md',
               'assign': ASSIGN, 'machine': MACHINE, 'workers': WORKERS,
               'note': ('외부 계열(CoRE) 구조를 우리 프로토콜로 돌린 것. '
                        '우리 물질 결과가 아니며 results_v3.json 과 섞지 말 것.'),
               'protocol': PROTOCOL,
               'rows': sorted(rows.values(), key=lambda r: r['file'])},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main():
    if not ASSIGN:
        print('!! COREWC_ASSIGN 필요', flush=True)
        return 2
    pick = [p for p in json.load(open(PICK, encoding='utf-8')) if p.get('assign') == ASSIGN]
    if not pick:
        print(f'!! assign={ASSIGN} 몫이 없습니다', flush=True)
        return 2
    rows = load_prior()
    bykey = {os.path.splitext(p['file'])[0]: p for p in pick}

    # (랩탑 09-23 01:1x) CIF 가 없는 대상을 **말없이 건너뛰지 않습니다.** 아래 todo 는
    # `os.path.exists` 로 거르는데, 그러면 n 이 조용히 줄어 "36종 배정" 과 "35종 완주" 가
    # 아무 데도 안 적힙니다 — 실패가 결과처럼 보이는 것(CLAUDE.md §0)의 조용한 쪽입니다.
    # 실제로 §AW 72종 중 **3종이 T-BR-1 의 12종 출신**이라 `core_pop_cifs.zip`(512 = 524−12)에
    # CIF 가 애초에 없습니다(laptop 1 · laptop2 2).
    nocif = [p['file'] for p in pick if not os.path.exists(os.path.join(CIFS, p['file']))]
    if nocif:
        print(f'!! CIF 없음 {len(nocif)}종 — 이번 실행에서 빠집니다(n 이 {len(pick)} 이 아니라 '
              f'{len(pick) - len(nocif)} 입니다): {", ".join(nocif)}', flush=True)
        print('   CIF 를 받으면 같은 명령을 다시 치십시오 — 나머지는 이어받고 이것만 돕니다.', flush=True)

    from concurrent.futures import ProcessPoolExecutor, as_completed
    for P in PRESSURES:
        rg.PRESSURE = P * 1e5                      # RASPA 는 Pa
        rg.RUNS = os.path.join(HERE, f'core_wc_runs_p{P:g}')   # ★ 압력별로 뿌리를 가른다
        os.makedirs(rg.RUNS, exist_ok=True)
        key = f'n_{P:g}bar'
        todo = [p for p in pick
                if os.path.exists(os.path.join(CIFS, p['file']))
                and rows.get(p['file'], {}).get(key) is None]
        todo.sort(key=lambda p: -int(p.get('N_super') or 0))    # LPT — 자는 N_super
        print(f'\n=== {P:g} bar · 남은 {len(todo)}/{len(pick)}종 · 워커 {WORKERS} · 뿌리 {os.path.basename(rg.RUNS)}',
              flush=True)
        if not todo:
            continue
        jobs = [(os.path.join(CIFS, p['file']), 'CO2', 'gcmc') for p in todo]
        n = 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            futs = [ex.submit(rg._star, j) for j in jobs]
            for fu in as_completed(futs):
                name, gas, mode, r, stt = fu.result()
                n += 1
                p = bykey.get(name, {})
                row = rows.setdefault(p.get('file', name + '.cif'), {
                    'file': p.get('file', name + '.cif'), 'key': p.get('key'),
                    'set': p.get('set'), 'topo': p.get('topo'), 'metal': p.get('metal'),
                    'PLD': p.get('PLD'), 'LCD': p.get('LCD'), 'N_super': p.get('N_super'),
                    'our_KH_CO2': p.get('our_KH_CO2'), 'our_selectivity': p.get('our_selectivity'),
                    'machine': MACHINE, 'run_status': {}})
                row['run_status'][f'{P:g}bar'] = stt
                if r and r[4] is not None:
                    row[key], row[key + '_err'] = r[4], r[5]
                write(rows)
                print(f'  [{stt:>9}] {P:g}bar {name}  ({n}/{len(jobs)})', flush=True)

    for r in rows.values():
        a, d = r.get('n_0.15bar'), r.get('n_0.01bar')
        if a is not None and d is not None:
            r['wc_vsa'] = a - d
            ea, ed = r.get('n_0.15bar_err') or 0, r.get('n_0.01bar_err') or 0
            r['wc_vsa_err'] = (ea ** 2 + ed ** 2) ** 0.5      # σ_wc = √(σ_ads²+σ_des²), CLAUDE.md §2
    write(rows)
    ok = sum(1 for r in rows.values() if r.get('wc_vsa') is not None)
    print(f'\n저장 {OUT} — 작업 용량 {ok}/{len(pick)}종', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
