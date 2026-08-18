"""C2 치환형 이미다졸레이트 ZIF 의 자리 지도를 **기하로** 만든다.

[왜 새로 만드나]
    기존 site_map_zif67.json 은 내 정리본과 맞지 않습니다 -- 24개 자리 전부에서
    고리 자리에 H 나 Co 가 들어 있습니다. 다른 원자 순서로 만든 지도입니다.
    자리 지도는 **원자 인덱스**를 저장하므로 구조 파일이 바뀌면 통째로 무효입니다.

[규약은 동작하는 파일에서 읽었다]
    ZIF-8 의 site_map.json 을 24개 자리 전수 확인한 결과:
        ring        길이 5, **C2 가 0번**, 고리를 따라 이어진 순서 [C2,N,C,C,N]
        substituent 길이 4, **메틸 C 가 0번**, 나머지 H 3개
    문서가 아니라 실제로 도는 파일에서 읽었습니다. 24/24 에서 성립합니다.

[왜 인덱스를 하드코딩하지 않고 기하로 찾나]
    2026-08-14 의 부착 위치 버그가 "인덱스를 상수로 가정" 이었습니다
    (STRUCTURE_DEFECT.md). 같은 실수를 반복하지 않으려면 원자를 **번호가 아니라
    화학적 역할로** 찾아야 합니다. C2 는 "고리 안에서 두 질소와 결합한 탄소" 이고,
    이 정의는 원자 순서와 무관합니다.
"""
import collections
import json
import sys

from ase.io import read
from ase.neighborlist import neighbor_list

COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'Zn': 1.22, 'Co': 1.26,
       'Cl': 1.02, 'F': 0.57, 'S': 1.05, 'Br': 1.20}
METALS = {'Zn', 'Co', 'Cd', 'Fe', 'Mn', 'Ni', 'Cu'}


def graph(atoms, scale=1.25):
    syms = sorted(set(atoms.get_chemical_symbols()))
    cut = {(a, b): scale * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j = neighbor_list('ij', atoms, cut)
    g = collections.defaultdict(set)
    for a, b in zip(i, j):
        g[int(a)].add(int(b)); g[int(b)].add(int(a))
    return g


def main(cif, out):
    atoms = read(cif)
    sym = atoms.get_chemical_symbols()
    g = graph(atoms)

    sites = []
    for c2 in range(len(atoms)):
        if sym[c2] != 'C':
            continue
        ns = [n for n in g[c2] if sym[n] == 'N']
        # C2 는 두 질소 사이에 있고, 그 질소들은 금속에 배위한다.
        if len(ns) != 2:
            continue
        if not all(any(sym[m] in METALS for m in g[n]) for n in ns):
            continue

        # 고리를 따라 걷는다: C2 -> N -> C -> C -> N -> (C2)
        ring = [c2, ns[0]]
        prev, cur = c2, ns[0]
        ok = True
        for _ in range(3):
            nxt = [n for n in g[cur]
                   if n != prev and sym[n] in ('C', 'N') and sym[n] not in METALS]
            # 금속으로 새지 않도록, 그리고 고리 밖 탄소로 새지 않도록
            nxt = [n for n in nxt if n == c2 or n not in ring]
            if not nxt:
                ok = False
                break
            # 다음 고리 원자는 결국 C2 로 돌아와야 한다. 후보가 여럿이면
            # 고리를 닫는 쪽을 고른다.
            pick = None
            for n in nxt:
                if len(ring) == 4 and c2 in g[n]:
                    pick = n
                    break
            if pick is None:
                cand = [n for n in nxt if n != c2]
                if not cand:
                    ok = False
                    break
                pick = cand[0]
            ring.append(pick)
            prev, cur = cur, pick
        if not ok or len(ring) != 5:
            continue
        if c2 not in g[ring[4]]:
            continue                                    # 고리가 닫히지 않음
        if [sym[k] for k in ring] != ['C', 'N', 'C', 'C', 'N']:
            continue

        # 치환기: C2 에 붙은 고리 밖 원자
        outs = [n for n in g[c2] if n not in ring]
        if len(outs) != 1:
            continue
        head = outs[0]
        sub = [head] + sorted(n for n in g[head] if sym[n] == 'H')
        sites.append({'site_id': len(sites), 'ring': ring, 'substituent': sub})

    print(f'  구조 {cif}')
    print(f'    원자 {len(atoms)}  '
          f'{dict(sorted(collections.Counter(sym).items()))}')
    print(f'  찾은 자리 {len(sites)}개')
    if sites:
        lens = collections.Counter((len(s['ring']), len(s['substituent']))
                                   for s in sites)
        print(f'    (ring, substituent) 길이 분포: {dict(lens)}')
        el = collections.Counter(tuple(sym[k] for k in s['substituent'])
                                 for s in sites)
        for k, v in el.items():
            print(f'    치환기 원소 {k}: {v}개')
    with open(out, 'w') as f:
        json.dump(sites, f, indent=1)
    print(f'  기록 {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
