# -*- coding: utf-8 -*-
"""§AV — 세 갈래 결과를 한 모집단으로 합친다. **프로토콜이 같은지 먼저 따진다.**

    core_pop_results_laptop2.json   308종  (laptop2)
    core_pop_results_laptop.json    204종  (laptop)
    bridge_core_results.json         12종  (desktop — T-BR-1 이 이미 돌린 것, **다시 돌리지 않음**)
                                   ------
                                     524종

[왜 12종을 다시 안 도나]
    T-BR-1 이 쓴 러너가 `run_aryl_gcmc.run_one` 으로 **§AV 와 같은 함수**이고,
    프로토콜 블록이 공통 키 전부에서 **값까지 같습니다**(§AV 에만 설명용 `co2` 키가 더 있음).
    같은 규약으로 이미 나온 값을 버리고 다시 도는 것은 계산 낭비일 뿐 정확도를 올리지 않습니다.
    이 스크립트가 그 동일성을 **실행 시점에 검사**하고, 어긋나면 멈춥니다.

[기기가 섞이는 것에 대하여]
    524종은 세 기기에서 나옵니다. 이 저장소는 이미 기기를 섞어 써 왔고 그 타당성 검토가
    `V3_WC_LAPTOP_VALIDATION.md` 에 있습니다. Widom 평균은 기기가 아니라 규약이 정합니다.
    그래도 `host` 를 행마다 남겨 사후에 기기별로 갈라 볼 수 있게 합니다.

실행: ~/miniconda3/envs/czeromof/bin/python merge_core_pop.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PICK = os.path.join(HERE, 'core_pop_pick.json')
OUT = os.path.join(HERE, 'core_pop_merged.json')

SOURCES = [
    ('laptop2', 'core_pop_results_laptop2.json'),
    ('laptop', 'core_pop_results_laptop.json'),
    ('desktop', 'bridge_core_results.json'),
]
# 프로토콜 비교에서 뺄 키: 설명 문자열이라 값이 아니다.
DESCRIPTIVE = {'co2'}


def main():
    pick = {p['file']: p for p in json.load(open(PICK, encoding='utf-8'))}
    ref, rows, missing = None, {}, []

    for host, fname in SOURCES:
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            missing.append((host, fname))
            continue
        d = json.load(open(path, encoding='utf-8'))
        proto = {k: v for k, v in d['protocol'].items() if k not in DESCRIPTIVE}
        if ref is None:
            ref, ref_host = proto, host
        elif proto != ref:
            diff = {k: (ref.get(k), proto.get(k)) for k in set(ref) | set(proto)
                    if ref.get(k) != proto.get(k)}
            print(f'!! 프로토콜 불일치 {ref_host} 대 {host}: {diff}', flush=True)
            print('   합치지 않습니다. 사람이 볼 것.', flush=True)
            return 3
        n = 0
        for r in d['rows']:
            if r.get('status') != 'ok':
                continue
            f = r.get('file') or (r.get('key', '') + '.cif')
            p = pick.get(f)
            if p is None:                     # 풀 밖의 행은 넣지 않는다
                continue
            rows[f] = dict(r, host=host, assign=p['assign'],
                           VF=p.get('VF'), GPV=p.get('GPV'),
                           core_KH_N2=p.get('KH_N2'), core_KH_CO2=p.get('KH_CO2'),
                           core_selectivity=p.get('sel'))
            n += 1
        print(f'  {host:8} {fname:34} 성공 {n:4} / 기록 {len(d["rows"]):4}', flush=True)

    if missing:
        print('\n아직 없는 갈래:', ', '.join(f'{h}({f})' for h, f in missing), flush=True)

    got = len(rows)
    want = len(pick)
    print(f'\n합계 {got} / {want}  ({got / want * 100:.1f} %)', flush=True)
    per = {}
    for r in rows.values():
        per[r['assign']] = per.get(r['assign'], 0) + 1
    print('  배정별:', {k: f"{per.get(k, 0)}/{sum(1 for p in pick.values() if p['assign'] == k)}"
                    for k in ('laptop2', 'laptop', 'desktop')}, flush=True)

    json.dump({
        'test': '§AV core-pop (병합)',
        'registration': 'COREPOP_REGISTRATION_20260921.md',
        'note': ('외부 계열(CoRE) 구조를 우리 프로토콜로 돌린 것. 우리 물질 결과가 아니며 '
                 'results_v3.json 과 섞지 말 것. desktop 12종은 T-BR-1 결과를 그대로 가져온 것이고 '
                 '프로토콜 동일성을 이 스크립트가 검사했다.'),
        'protocol': ref,
        'n': got, 'n_pool': want,
        'sources': {h: f for h, f in SOURCES},
        'rows': sorted(rows.values(), key=lambda r: r['file']),
    }, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'저장 {OUT}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
