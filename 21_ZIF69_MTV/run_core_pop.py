# -*- coding: utf-8 -*-
"""§AV — CoRE 관문 통과 풀 524종을 **우리 프로토콜로** Widom 재계산한다.

등록: `COREPOP_REGISTRATION_20260921.md` (자료 0건, 2026-09-21)

[왜]
    T-BR-1(`BRIDGE_CORE_RESULT_20260921.md`)이 CoRE 눈금과 우리 눈금 사이의 **단일 배율 환산을 기각**했다.
    그러면 남은 정직한 길은 하나뿐이다 — **CoRE 구조를 우리 자로 직접 재는 것.**
    그러면 이전(transfer) 가정이 **아예 필요 없어진다.**

[우리 결과가 아니다]
    외부 계열 구조다. `results_v3.json` · `v3*` 어디에도 섞지 않는다.
    결과는 `core_pop_results_<host>.json` 한 곳에만 쓴다.

[고정값을 바꾸지 않는다]
    사이클·힘장·CO2/N2 정의·전하·Ewald·컷오프 전부 `run_aryl_gcmc` 의 것 그대로(CLAUDE.md §1).
    슈퍼셀만 숫자가 아니라 **규칙**(`unit_cells()`, 최소거리규약 >= 2x컷오프) — T-BR-1 과 같은 예외.

[환경 변수]
    COREPOP_ASSIGN   'laptop' | 'laptop2' | 'desktop'   (pick 의 assign 과 대조. 필수)
    COREPOP_WORKERS  동시 RASPA 개수 (기본 = 물리 코어 수 - 0; 기기가 비어 있을 때만 크게)
    COREPOP_OUT      결과 경로 (기본 core_pop_results_<assign>.json)

[이어받기]
    `run_one` 의 실행폴더 이어받기(완주한 `.data` 재사용)를 그대로 쓴다. 결과 JSON 도 매 작업마다
    갱신하므로 13시간짜리 묶음이 중간에 끊겨도 **끝난 만큼은 남는다.** 죽으면 같은 명령을 다시 치면 된다.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg  # noqa: E402

ASSIGN = os.environ.get('COREPOP_ASSIGN', '').strip()
WORKERS = int(os.environ.get('COREPOP_WORKERS', '8'))
CIFS = os.path.join(HERE, 'core_pop_cifs')
PICK = os.path.join(HERE, 'core_pop_pick.json')
OUT = os.environ.get('COREPOP_OUT') or os.path.join(HERE, f'core_pop_results_{ASSIGN}.json')

rg.MAX_WORKERS = WORKERS
rg.RUNS = os.path.join(HERE, 'core_pop_runs')

PROTOCOL = {
    'widom_cycles': rg.WIDOM_CYCLES, 'widom_init': rg.WIDOM_INIT,
    'forcefield': 'UFF_MOF', 'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP,
    'charges': 'UseChargesFromCIFFile (CoRE CIF 의 PACMAN DDEC6)',
    'supercell': '숫자 고정이 아니라 unit_cells() 규칙 — 등록 §1',
    'co2': 'García-Sánchez 2009 (경로는 TraPPE/CO2.def 지만 TraPPE 가 아님 — CLAUDE.md §1)',
}


def load_prior():
    """이전 결과를 회수한다. **프로토콜이 다르면 거부한다**(CLAUDE.md §3 의 함정)."""
    if not os.path.exists(OUT):
        return {}
    d = json.load(open(OUT, encoding='utf-8'))
    if d.get('protocol') != PROTOCOL:
        print('!! 기존 결과의 프로토콜이 다릅니다 — 이어받지 않습니다. 파일을 치우고 처음부터 도십시오.',
              flush=True)
        sys.exit(4)
    return {r['file']: r for r in d.get('rows', [])}


def write(rows, note=''):
    json.dump({
        'test': '§AV core-pop',
        'registration': 'COREPOP_REGISTRATION_20260921.md',
        'assign': ASSIGN, 'workers': WORKERS,
        'note': ('외부 계열(CoRE) 구조를 우리 프로토콜로 돌린 것. '
                 '우리 물질 결과가 아니며 results_v3.json 과 섞지 말 것. ' + note),
        'protocol': PROTOCOL,
        'rows': sorted(rows.values(), key=lambda r: r['file']),
    }, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main():
    if ASSIGN not in ('laptop', 'laptop2', 'desktop'):
        print('!! COREPOP_ASSIGN 을 laptop / laptop2 / desktop 중 하나로 주십시오.', flush=True)
        return 2

    pick = [p for p in json.load(open(PICK, encoding='utf-8')) if p.get('assign') == ASSIGN]
    if not pick:
        print(f'!! assign={ASSIGN} 에 배정된 구조가 없습니다.', flush=True)
        return 2

    rows = load_prior()
    todo = []
    for p in pick:
        f = os.path.join(CIFS, p['file'])          # 위생 이름(대괄호 -> 밑줄), T-BR-1 과 같은 규칙
        if not os.path.exists(f):
            print(f"  [CIF 없음] {p['file']}", flush=True)
            continue
        if p['file'] in rows and rows[p['file']].get('status') == 'ok':
            continue
        todo.append((p, f))

    # LPT — 비싼 것부터. 미리 덩어리로 안 나눈다(CLAUDE.md §5).
    #
    # 자는 **NAtoms 가 아니라 N_super = NAtoms x 셀수** 다. 셀수는 `unit_cells()` 의 최소거리규약이
    # 정하므로 작은 셀일수록 많이 복제된다 — 같은 396원자라도 ftw(1x1x1)=396 과 tfz(2x2x2)=3168 이
    # **8배** 차이다. NAtoms 로 정렬하면 원자 적고 셀 많은 구조가 대기열 뒤로 밀리고,
    # 그것이 최장 단일 작업이 되어 꼬리를 혼자 늘린다(§AU 의 27.79 h 와 같은 형태).
    # 2026-09-21 laptop2(Balthasar) 발견. 실측: laptop2 최대 N_super 5670 짜리가 NAtoms 정렬에서
    # **118/308 번째**에 있었다.
    todo.sort(key=lambda t: -int(t[0].get('N_super') or (int(t[0].get('NAtoms') or 0) * 8)))
    jobs = [(f, g, 'widom') for _, f in todo for g in ('CO2', 'N2')]
    bykey = {os.path.splitext(p['file'])[0]: p for p, _ in todo}   # run_one 이 돌려주는 name 기준

    print(f'§AV {ASSIGN}  배정 {len(pick)}종 · 회수 {len(pick) - len(todo)}종 · 남은 {len(todo)}종 '
          f'x (Widom CO2 + N2) = {len(jobs)}작업  (워커 {WORKERS})', flush=True)
    if not jobs:
        write(rows, '전부 회수 — 새 계산 없음')
        print('할 일 없음(전부 이어받음).', flush=True)
        return 0

    os.makedirs(rg.RUNS, exist_ok=True)
    part, n = {}, 0
    # `ex.map` 은 **순서대로만** 내줍니다 — 첫 작업이 느리면 뒤의 결과가 다 끝나고도
    # 안 나와서 "작업마다 저장" 이 거짓말이 됩니다. 24시간짜리 묶음이라 그러면 안 됩니다.
    # `submit` + `as_completed` 로 **끝나는 대로** 받습니다(CLAUDE.md §5 의 imap_unordered 취지).
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(rg._star, j) for j in jobs]
        for fu in as_completed(futs):
            name, gas, mode, r, stt = fu.result()
            n += 1
            part.setdefault(name, {})[gas] = (r, stt)     # 실패 사유(stt)까지 들고 간다
            print(f'  [{stt:>9}] {gas:<3} {name}   ({n}/{len(jobs)})', flush=True)
            if len(part[name]) < 2:
                continue                                  # 두 기체가 다 와야 행을 만든다

            p = bykey.get(name, {})
            (kc, sc), (kn, sn) = part[name]['CO2'], part[name]['N2']
            row = {'file': name + '.cif', 'key': p.get('key'), 'set': p.get('set'), 'topo': p.get('topo'), 'metal': p.get('metal'),
                   'PLD': p.get('PLD'), 'LCD': p.get('LCD'), 'VF': p.get('VF'), 'GPV': p.get('GPV'),
                   'NAtoms': p.get('NAtoms'),
                   'core_KH_CO2': p.get('KH_CO2'), 'core_KH_N2': p.get('KH_N2'),
                   'core_selectivity': p.get('sel'),
                   'run_status': {'CO2': sc, 'N2': sn},   # 'ok' | 'cached' | '미완주' | 'timeout' | ...
                   'status': 'ok'}
            # `run_one` 은 실패하면 r 자체를 None 으로 돌려준다('미완주'·'timeout'·'no-output'·
            # '값없음'·'다른세션실행중'). 옛 판의 `elif kc is not None` 은 그 경우를 **놓쳐서**
            # 값 없는 행이 status='ok' 로 남았다. `else` 여야 한다.
            if kc and kc[0] is not None:
                row['KH_CO2'], row['KH_CO2_err'] = kc[0], kc[1]
                row['dU_CO2'], row['dU_CO2_err'] = kc[2], kc[3]
            else:
                row['status'] = f'CO2 실패({sc})'
            if kn and kn[0] is not None:
                row['KH_N2'], row['KH_N2_err'] = kn[0], kn[1]
            else:
                row['status'] = (f'둘 다 실패({sc}/{sn})' if row['status'] != 'ok' else f'N2 실패({sn})')
            if row.get('KH_CO2') and row.get('KH_N2'):
                row['selectivity'] = row['KH_CO2'] / row['KH_N2']
            rows[name + '.cif'] = row
            write(rows)

    write(rows)
    ok = sum(1 for r in rows.values() if r['status'] == 'ok')
    print(f'\n저장 {OUT}  —  {ok}/{len(pick)} 성공', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
