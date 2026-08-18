"""site_map_zif67.json 이 내 정리본과 실제로 맞는가.

[왜 세는가]
    자리 지도는 **원자 인덱스**를 저장합니다. 인덱스는 구조 파일의 원자 순서에
    의존하므로, 다른 경로로 만든 276원자 구조에서는 같은 번호가 전혀 다른 원자를
    가리킬 수 있습니다. 그리고 그렇게 어긋나도 빌더는 조용히 완주합니다 --
    2026-08-14 의 부착 위치 버그가 정확히 이 부류였습니다(STRUCTURE_DEFECT.md).

[무엇으로 판정하나 -- 번호가 아니라 화학으로]
    ring 은 이미다졸레이트 고리여야 합니다: 원자 5개, N 2개 + C 3개, 고리를 이룸.
    substituent 는 메틸이어야 합니다: 원자 4개, C 1개 + H 3개, C 가 고리에 결합.
    24개 자리가 서로 겹치지 않고, 전체가 링커 24개를 남김없이 덮어야 합니다.
"""
import collections
import itertools
import json
import sys

import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'Co': 1.26, 'Zn': 1.22}


def graph(atoms, scale=1.25):
    syms = sorted(set(atoms.get_chemical_symbols()))
    cut = {(a, b): scale * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j = neighbor_list('ij', atoms, cut)
    g = collections.defaultdict(set)
    for a, b in zip(i, j):
        g[int(a)].add(int(b)); g[int(b)].add(int(a))
    return g


def main(cif, smj):
    atoms = read(cif)
    sym = atoms.get_chemical_symbols()
    g = graph(atoms)
    sites = json.load(open(smj))
    print(f'  구조 {cif}')
    print(f'    원자 {len(atoms)}  {dict(sorted(collections.Counter(sym).items()))}')
    print(f'  자리 지도 {smj}\n    자리 {len(sites)}개\n')

    bad, used = 0, []
    for s in sites:
        sid, ring, sub = s['site_id'], s['ring'], s['substituent']
        msg = []
        # --- 고리 ---
        rs = collections.Counter(sym[k] for k in ring)
        if len(ring) != 5 or rs.get('N', 0) != 2 or rs.get('C', 0) != 3:
            msg.append(f'고리 조성 {dict(rs)} (N2C3 여야 함)')
        else:
            # 5원 고리를 이루는가 -- 각 원자가 고리 안에서 이웃 2개를 가져야 한다
            deg = [len(g[k] & set(ring)) for k in ring]
            if sorted(deg) != [2, 2, 2, 2, 2]:
                msg.append(f'고리 결합 차수 {sorted(deg)} (전부 2 여야 함)')
        # --- 치환기 ---
        ss = collections.Counter(sym[k] for k in sub)
        if len(sub) != 4 or ss.get('C', 0) != 1 or ss.get('H', 0) != 3:
            msg.append(f'치환기 조성 {dict(ss)} (CH3 여야 함)')
        else:
            mc = [k for k in sub if sym[k] == 'C'][0]
            hs = [k for k in sub if sym[k] == 'H']
            if not all(h in g[mc] for h in hs):
                msg.append('메틸 H 가 메틸 C 에 결합돼 있지 않음')
            anchor = g[mc] & set(ring)
            if len(anchor) != 1:
                msg.append(f'메틸 C 가 고리에 붙은 자리 {len(anchor)}개 (1개여야 함)')
            else:
                a = next(iter(anchor))
                if sym[a] != 'C':
                    msg.append(f'메틸이 {sym[a]} 에 붙어 있음 (C2 여야 함)')
                elif len(g[a] & set(ring)) == 2 and \
                        sum(1 for n in g[a] & set(ring) if sym[n] == 'N') != 2:
                    msg.append('메틸이 붙은 탄소가 두 질소 사이(C2)가 아님')
        used += ring + sub
        if msg:
            bad += 1
            print(f'    자리 {sid:>2}  ✗  ' + ' / '.join(msg))

    print(f'\n  자리별 검사: 불합격 {bad} / {len(sites)}')
    dup = [k for k, v in collections.Counter(used).items() if v > 1]
    print(f'  중복 사용된 원자: {len(dup)}개' + (f' {dup[:8]}' if dup else ' (없음)'))
    # 지도는 링커 원자를 전부 담지 않습니다 -- 고리 H 2개는 치환 조작과 무관해서
    # 넣지 않는 설계입니다(ZIF-8 의 정상 지도도 자리당 9원자, 24x9=216).
    # 처음에 '전부 덮어야 한다'로 검사했더니 **정상인 ZIF-8 지도까지 불합격**으로
    # 신고했습니다. 기준은 자리당 9원자, 중복 없음입니다.
    ncov = len(set(used))
    exp = 9 * len(sites)
    print(f'  덮은 원자 {ncov} / 기대 {exp} (자리당 고리5 + 치환기4)'
          + ('  ✓' if ncov == exp else '  <<< 불일치'))
    ok = (bad == 0 and not dup and ncov == exp)
    print(f'\n  판정: {"이 구조에 그대로 쓸 수 있습니다" if ok else "다시 만들어야 합니다"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
