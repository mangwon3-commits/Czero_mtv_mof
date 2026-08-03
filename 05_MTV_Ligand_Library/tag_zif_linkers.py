"""
1회성 유틸리티: 기존 mIm 전용 ZIF-8 P1 CIF에서 각 링커의
고리 원자(C2,N3,C4,C5,N1)와 C2에 달린 치환기 원자를 자동 식별해
site_map.json으로 저장한다.

핵심 아이디어:
    금속(Zn) 원자를 그래프에서 제외하고 C,N만으로 결합 그래프를 만들면
    각 이미다졸 고리가 다른 링커와 연결되지 않은 독립된 5-사이클로 남는다.
    (Zn을 포함시키면 N1-Zn-...-Zn-N3 같은 큰 고리가 섞여 들어와 오탐 발생)

전제 및 한계:
    - 링커의 5원자 고리가 단일 unit cell 안에 들어있다고 가정
      (일반적인 ZIF-8 슈퍼셀 크기에서는 성립. 아주 작은 셀이면 결과 검산 필요)
    - 명시적 H 원자가 CIF에 포함되어 있어야 함 (기존 파이프라인 산출물 기준)
    - 원소 구성이 C, N, H 뿐인 mIm 전용 베이스 구조에만 사용
      (nIm 등 O 포함 리간드는 애초에 이 스크립트 대상이 아님 -> mtv_cif_builder.py에서 새로 만듦)

pip install ase networkx --break-system-packages
"""
import json
import networkx as nx
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs


def build_bond_graph(atoms):
    cutoffs = natural_cutoffs(atoms, mult=1.15)
    # [버그 수정] 기본 skin=0.3이 고리 내 1,3-비결합 거리(~2.15 Å)까지 결합으로 오인해
    # 5원자 고리가 삼각형 위주 그래프로 깨지는 문제가 있어 skin=0.0으로 고정한다.
    nl = NeighborList(cutoffs, skin=0.0, self_interaction=False, bothways=True)
    nl.update(atoms)

    G = nx.Graph()
    G.add_nodes_from(range(len(atoms)))
    for i in range(len(atoms)):
        neighbors, _ = nl.get_neighbors(i)
        for j in neighbors:
            # [버그 수정] get_neighbors()가 numpy.int64를 반환해 이후 site_map.json
            # 직렬화가 실패하므로 파이썬 int로 캐스팅한다.
            G.add_edge(i, int(j))
    return G


def find_imidazole_rings(atoms, G):
    """C,N 서브그래프에서 5-사이클만 추출 (금속 제외로 링커별 독립 고리가 됨)"""
    symbols = atoms.get_chemical_symbols()
    heavy = [i for i in G.nodes if symbols[i] in ("C", "N")]
    subG = G.subgraph(heavy)
    return [c for c in nx.cycle_basis(subG) if len(c) == 5]


def order_ring(ring, c2, atoms, G):
    """C2를 시작점으로 [C2, N3, C4, C5, N1] 순서로 정렬.
    N3 = H가 안 붙은 질소, N1 = H가 붙은 질소.
    RDKit 쪽 SMARTS 'c1ncc[nH]1' 매칭 순서와 동일하게 맞추기 위한 정렬이며,
    이 순서가 어긋나면 Kabsch 정합이 틀어진 회전을 낸다."""
    symbols = atoms.get_chemical_symbols()

    def has_h_neighbor(idx):
        return any(symbols[n] == "H" for n in G.neighbors(idx))

    n_neighbors = [n for n in G.neighbors(c2) if n in ring and symbols[n] == "N"]
    if len(n_neighbors) != 2:
        return None
    n3 = next((n for n in n_neighbors if not has_h_neighbor(n)), None)
    n1 = next((n for n in n_neighbors if n != n3), None)
    if n3 is None or n1 is None:
        return None

    c4 = next((n for n in G.neighbors(n3) if n in ring and n != c2), None)
    c5 = next((n for n in G.neighbors(c4) if n in ring and n != n3), None) if c4 else None
    if c4 is None or c5 is None or not G.has_edge(c5, n1):
        return None  # 예상 위상과 다름 -> 이 사이트는 건너뜀

    return [c2, n3, c4, c5, n1]


def analyze_sites(atoms, G, raw_rings):
    symbols = atoms.get_chemical_symbols()
    sites = []
    for site_id, ring in enumerate(raw_rings):
        n_in_ring = [i for i in ring if symbols[i] == "N"]
        if len(n_in_ring) != 2:
            continue
        c2 = next(
            (i for i in ring if symbols[i] == "C"
             and sum(1 for n in n_in_ring if G.has_edge(i, n)) == 2),
            None,
        )
        if c2 is None:
            continue
        ordered_ring = order_ring(ring, c2, atoms, G)
        if ordered_ring is None:
            print(f"[경고] site {site_id}: 고리 순서 정렬 실패, 건너뜀")
            continue

        subst = set()
        frontier = [n for n in G.neighbors(c2) if n not in ring]
        while frontier:
            cur = frontier.pop()
            if cur in subst:
                continue
            subst.add(cur)
            frontier.extend(n for n in G.neighbors(cur) if n not in ring and n not in subst)

        sites.append({"site_id": site_id, "ring": ordered_ring, "substituent": sorted(subst)})
    return sites


def find_six_rings(atoms, G):
    """C,N 서브그래프에서 6-사이클만 추출 (벤조 고리 등 융합 방향족용)."""
    symbols = atoms.get_chemical_symbols()
    heavy = [i for i in G.nodes if symbols[i] in ("C", "N")]
    subG = G.subgraph(heavy)
    return [c for c in nx.cycle_basis(subG) if len(c) == 6]


def _substituent_bfs(anchor, ring_set, G):
    """anchor에서 ring_set 밖으로 뻗어나가는 원자들을 BFS로 모두 수집 (치환기 탐색 공통 로직)."""
    subst = set()
    frontier = [n for n in G.neighbors(anchor) if n not in ring_set]
    while frontier:
        cur = frontier.pop()
        if cur in subst:
            continue
        subst.add(cur)
        frontier.extend(n for n in G.neighbors(cur) if n not in ring_set and n not in subst)
    return sorted(subst)


def _walk_benzo_path(G, c4, c5, six_ring):
    """6원자 고리 안에서 c4->c5로 가는 경로 중, 두 고리가 공유하는 c4-c5 직접 결합
    (융합 결합)을 제외한 4개 원자짜리 우회 경로를 반환한다."""
    six_set = set(six_ring)
    H = G.subgraph(six_set).copy()
    if H.has_edge(c4, c5):
        H.remove_edge(c4, c5)
    path = nx.shortest_path(H, c4, c5)
    return path[1:-1]


def find_bicyclic_sites(atoms, G, mono_sites):
    """ZIF-69의 cbIm(5-클로로벤즈이미다졸레이트)처럼 이미다졸 고리에 벤젠 고리가
    융합된 자리를 찾는다. mono_sites 중 C2 치환기가 H 1개뿐인 자리를 벤조 융합
    후보로 보고, C4-C5가 공유하는 6원자 고리를 찾아 [C2,N3,C4,b1,b2,b3,b4,C5,N1]
    9원자 고리로 확장한 뒤, 벤조환 4자리 중 비-H 치환기(예: Cl)가 붙은 자리
    (아릴 치환 지점)를 식별한다.

    C2 자신은 건드리지 않고(H 그대로 유지) 벤조환 위의 치환기 자리만 교체 대상으로
    삼는다 -- PROJECT_HANDOVER.md가 권장하는 "cbIm:nIm 비율은 고정, 벤조환 치환기만
    SALE식으로 교체" 방향에 대응한다."""
    symbols = atoms.get_chemical_symbols()
    six_rings = find_six_rings(atoms, G)

    bicyclic_sites = []
    for site in mono_sites:
        if len(site["substituent"]) != 1 or symbols[site["substituent"][0]] != "H":
            continue
        c2, n3, c4, c5, n1 = site["ring"]
        fused6 = next((r for r in six_rings if c4 in r and c5 in r), None)
        if fused6 is None:
            continue

        benzo_path = _walk_benzo_path(G, c4, c5, fused6)
        if len(benzo_path) != 4:
            continue

        full_ring = [c2, n3, c4] + benzo_path + [c5, n1]
        full_ring_set = set(full_ring)

        aryl_candidates = []
        for b in benzo_path:
            subst = _substituent_bfs(b, full_ring_set, G)
            if not (len(subst) == 1 and symbols[subst[0]] == "H"):
                aryl_candidates.append((b, subst))

        if len(aryl_candidates) != 1:
            continue  # 아릴 치환기가 정확히 1개인 경우만 이 방식 적용 가능

        aryl_pos, aryl_subst = aryl_candidates[0]
        bicyclic_sites.append({
            "site_id": site["site_id"],
            "bicyclic_ring": full_ring,
            "aryl_position_index": full_ring.index(aryl_pos),
            "aryl_substituent": aryl_subst,
        })
    return bicyclic_sites


def main(base_cif, output_json):
    atoms = read(base_cif)
    G = build_bond_graph(atoms)
    raw_rings = find_imidazole_rings(atoms, G)
    sites = analyze_sites(atoms, G, raw_rings)

    with open(output_json, "w") as f:
        json.dump(sites, f, indent=2)

    print(f"[OK] 링커 {len(sites)}개 인식 완료 -> {output_json}")
    print("     예상 링커 개수와 다르면 natural_cutoffs의 mult 값을 조정하세요.")


def main_bicyclic(base_cif, output_json):
    """ZIF-69처럼 벤조 융합 고리(cbIm)가 섞여 있는 구조용. mono 사이트를 먼저 찾은 뒤
    그중 벤조 융합된 것만 골라 output_json에 저장한다 (nIm 등 단일고리 사이트는
    포함하지 않음 -- Priority 3 권장 방향은 cbIm:nIm 비율을 건드리지 않으므로)."""
    atoms = read(base_cif)
    G = build_bond_graph(atoms)
    raw_rings = find_imidazole_rings(atoms, G)
    mono_sites = analyze_sites(atoms, G, raw_rings)
    bicyclic_sites = find_bicyclic_sites(atoms, G, mono_sites)

    with open(output_json, "w") as f:
        json.dump(bicyclic_sites, f, indent=2)

    print(f"[OK] 벤조 융합(cbIm형) 사이트 {len(bicyclic_sites)}개 인식 완료 -> {output_json}")


if __name__ == "__main__":
    main("ZIF8_mIm_only_P1.cif", "site_map.json")
