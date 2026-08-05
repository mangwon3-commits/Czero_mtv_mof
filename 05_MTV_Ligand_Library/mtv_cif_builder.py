"""
tag_zif_linkers.py가 만든 site_map.json을 이용해 목표 조성비대로
리간드를 치환하고 RASPA 입력용 CIF를 생성한다.

pip install ase rdkit numpy --break-system-packages
conda install -c conda-forge openbabel   # EQeq 부분전하 계산용 (obabel CLI)
"""
import json
import os
import subprocess
import tempfile

import numpy as np
from ase import Atoms
from ase.io import read, write
from rdkit import Chem
from rdkit.Chem import AllChem

LIGAND_LIBRARY = {
    "mIm":  "Cc1ncc[nH]1",
    "nIm":  "O=[N+]([O-])c1ncc[nH]1",
    "clIm": "Clc1ncc[nH]1",
    "cnIm": "N#Cc1ncc[nH]1",
    "tfIm": "FC(F)(F)c1ncc[nH]1",
    "etIm": "CCc1ncc[nH]1",
    "amIm": "Nc1ncc[nH]1",
    # [팀 문헌조사 반영] MIL-101(Cr)을 동일 몰농도로 개질해 비교한 연구에서 CO2 흡착
    # 성능이 지방족 -NH2 > -SO3H > 방향족 -NH2 > -NO2 순으로 보고됐다. 메커니즘이
    # 다르기 때문이다 -- 지방족 아민은 카바메이트를 만드는 화학흡착, -SO3H와 방향족
    # 아민은 루이스 산-염기 + 수소결합 병행, -NO2는 순수 루이스 산-염기.
    # 기존 amIm은 NH2가 고리에 직접 붙은 '방향족' 아민이라 이 순위에서 3등이다.
    # 아래 두 개는 그보다 위에 있는 두 종류를 시험하기 위해 추가했다.
    "amrIm": "NCc1ncc[nH]1",          # 지방족 아민 (-CH2NH2). 문헌 순위 1위
    "saIm":  "OS(=O)(=O)c1ncc[nH]1",  # 술폰산 (-SO3H). 문헌 순위 2위
}
# 이 SMARTS의 원자 순서가 c1(=C2) - n(=N3) - c(=C4) - c(=C5) - [nH](=N1) 이므로
# tag_zif_linkers.py의 order_ring()과 동일한 순서 규약을 공유한다.
RING_SMARTS = Chem.MolFromSmarts("c1ncc[nH]1")

# [Priority 3] ZIF-69의 cbIm(5-클로로벤즈이미다졸레이트) 벤조환 치환기(SALE 자리)용
# 라이브러리. 원자 순서 [C2,N3,C4,b1,b2,b3,b4,C5,N1] 9개가
# tag_zif_linkers.py의 find_bicyclic_sites()가 만드는 bicyclic_ring과 동일 규약을
# 공유하며, 아릴 치환기는 b2(인덱스 4)에 붙인다 — 실제 ZIF-69-crystal.cif로 직접
# 검증한 위치(atom 248, C4 기준 두 번째 벤조 탄소)와 일치시킨 것.
LIGAND_LIBRARY_CBIM_ARYL = {
    "clIm_aryl": "c1nc2cc(Cl)ccc2[nH]1",
    "cf3Im_aryl": "c1nc2cc(C(F)(F)F)ccc2[nH]1",
    # [2026-08-05 추가] 술폰산. 단환식 라이브러리의 saIm과 같은 작용기다.
    #
    # 왜 이환식에도 필요한가 — Part 4의 결론은 "분산력과 정전기가 같은 부피를 놓고
    # 경쟁한다"였다. ZIF-7(공동 4.3 A)은 Q_st 34가 예측되지만 -SO3H(2.8 A)를 붙일
    # 자리가 없고, ZIF-8(11.4 A)은 자리는 있지만 치환해도 공동이 안 줄어든다
    # (sod에서 C2 치환기는 창구를 향한다 -- Part 2에서 실측으로 반증).
    #
    # ZIF-69는 그 사이에 있다. 실측으로 아릴 치환이 LCD를 8.76 -> 7.35 A (-16.1%)
    # 까지 줄이면서 PLD는 4.24 A로 열어 둔다(CO2 운동직경 3.3 A보다 여유). 즉
    # 공동을 좁히면서도 작용기를 붙일 자리가 남는 유일한 모체다. 두 메커니즘을
    # 동시에 시험하려면 이환식 라이브러리에 -SO3H가 있어야 한다.
    "saIm_aryl": "c1nc2cc(S(=O)(=O)O)ccc2[nH]1",
}
RING_SMARTS_BICYCLIC = Chem.MolFromSmarts("c1nc2ccccc2[nH]1")
CBIM_ARYL_ATTACHMENT_INDEX = 4

# [Priority 5] 완전한 결정구조 예측(CSP)은 하지 않고, 문헌에 보고된 알려진 위상 드리프트
# 경향만 조성비 임계값 형태로 태깅한다. PROJECT_HANDOVER.md 4-5절 근거.
TOPOLOGY_BIAS_NOTES = {
    "nIm": {"note": "혼합 리간드 반응에서 SOD가 아닌 GME 쪽으로 편향된다는 문헌 보고 있음", "risk_above": 0.5},
}


def check_topology_drift_risk(composition):
    """조성비를 TOPOLOGY_BIAS_NOTES와 대조해 위상 드리프트 위험 플래그 목록을 반환한다."""
    risks = []
    for lig, frac in composition.items():
        info = TOPOLOGY_BIAS_NOTES.get(lig)
        if info and frac > info["risk_above"]:
            risks.append({"ligand": lig, "fraction": frac, "note": info["note"]})
    return risks


def build_fragment_generic(smiles, ring_smarts, attachment_ring_index, label):
    """SMILES에서 3D 프래그먼트를 만들고, ring_smarts에 매칭되는 고리 원자와
    ring_match[attachment_ring_index]에서 고리 바깥쪽으로 뻗은 진짜 치환기만 골라낸다.

    [버그 수정] "ring_match에 없는 원자 = 전부 치환기"로 잡으면 AddHs()가 고리
    탄소(예: C4,C5 또는 벤조환 CH 위치)에 새로 붙인 명시적 수소까지 치환기로
    오인해, 결정구조에 원래 있던 고리 수소와 같은 자리에 중복으로 추가되어
    원자간 거리가 0.157 Å까지 겹쳤다. attachment_ring_index 위치에서 고리
    바깥쪽으로만 BFS를 돌려 진짜 치환기만 골라낸다 (tag_zif_linkers.py의 치환기
    탐색과 동일한 원칙 — 두 스크립트가 "치환기"를 같은 기준으로 정의해야 한다)."""
    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(mol, randomSeed=42, useRandomCoords=True)
    AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)

    ring_match = mol.GetSubstructMatch(ring_smarts)
    if not ring_match:
        raise ValueError(f"{label}: 고리 매칭 실패")
    ring_set = set(ring_match)

    conf = mol.GetConformer()
    symbols = [a.GetSymbol() for a in mol.GetAtoms()]
    coords = np.array([list(conf.GetAtomPosition(i)) for i in range(mol.GetNumAtoms())])

    anchor = ring_match[attachment_ring_index]
    subst_idx = set()
    frontier = [n.GetIdx() for n in mol.GetAtomWithIdx(anchor).GetNeighbors() if n.GetIdx() not in ring_set]
    while frontier:
        cur = frontier.pop()
        if cur in subst_idx:
            continue
        subst_idx.add(cur)
        frontier.extend(
            n.GetIdx() for n in mol.GetAtomWithIdx(cur).GetNeighbors()
            if n.GetIdx() not in ring_set and n.GetIdx() not in subst_idx
        )
    subst_idx = sorted(subst_idx)

    return {"symbols": symbols, "coords": coords, "ring_idx": list(ring_match), "subst_idx": subst_idx}


def build_fragment(name):
    return build_fragment_generic(LIGAND_LIBRARY[name], RING_SMARTS, 0, name)


def build_fragment_cbim_aryl(name):
    return build_fragment_generic(LIGAND_LIBRARY_CBIM_ARYL[name], RING_SMARTS_BICYCLIC,
                                   CBIM_ARYL_ATTACHMENT_INDEX, name)


def kabsch(P, Q):
    """Q(프래그먼트 고리) -> P(결정구조 고리) 정합 회전행렬과 두 중심 반환"""
    Pc, Qc = P.mean(0), Q.mean(0)
    H = (Q - Qc).T @ (P - Pc)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1, 1, d]) @ U.T
    return R, Pc, Qc


def _min_pairwise_distance(atoms):
    """주기경계(mic)를 감안한 전체 원자쌍 최소 거리. 구조 파손(원자 겹침) 여부 최종 확인용."""
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    return d.min()


def _rotation_about_axis(axis, theta):
    """Rodrigues 공식으로 axis(단위벡터) 기준 theta(rad) 회전행렬 생성."""
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def _unwrap(atoms, idx):
    """주기 경계를 걸친 원자 묶음을 첫 원자 기준으로 펼친 좌표를 돌려준다.

    [버그 수정] ZIF-8 P1 단위셀 24개 고리 중 **12개가 셀 경계를 걸쳐** 있다.
    그런 고리의 원시 좌표는 x가 0.1과 16.9로 흩어져 좌표 스팬이 16.32 A까지
    벌어진다(정상 고리는 2.2 A). 이 좌표를 그대로 Kabsch에 넣으면 고리 중심 Pc가
    셀 한가운데로 잡히고 회전행렬도 무의미해져서, 치환기가 링커에 붙지 못하고
    공동 중심(분율좌표 ~0.5,0.5,0.5)에 버려진다.

    실제로 치환 구조마다 치환기 4묶음이 골격에서 분리된 채 기공 안에 떠 있었고,
    빌더의 '최소 원자간 거리' 검사는 이걸 못 잡았다 -- 구조에 항상 존재하는
    메틸 C-H(0.929 A)가 전역 최솟값을 차지해 1.37 A짜리 치환기끼리의 충돌도,
    4.7 A짜리 고아 원자도 가려버렸기 때문이다.
    """
    cell = np.asarray(atoms.get_cell())
    pos = atoms.get_positions()[idx]
    ref = pos[0]
    frac = np.linalg.solve(cell.T, (pos - ref).T).T
    frac -= np.round(frac)                      # 최소 이미지로 펼치기
    return ref + frac @ cell


def _mic_min_distance(ref_positions, trial_positions, cell):
    """주기 경계를 감안한 두 좌표 집합 사이의 최소 거리."""
    diff = ref_positions[:, None, :] - trial_positions[None, :, :]
    frac = np.linalg.solve(cell.T, diff.reshape(-1, 3).T).T
    frac -= np.round(frac)
    return np.linalg.norm(frac @ cell, axis=-1).min()


def plan_substitution(atoms, site, fragment, avoid_positions=None, n_trial_angles=12, attachment_ring_index=0):
    """site의 ring 좌표(원본 atoms 기준)에 fragment를 Kabsch 정합시키고,
    삭제할 치환기 인덱스와 새로 추가할 원자(symbol, position)를 반환한다.
    atoms 자체는 건드리지 않는다 (다른 사이트의 인덱스를 깨뜨리지 않기 위함).

    attachment_ring_index: site["ring"]/fragment["ring_idx"] 중 실제 치환기가 붙는
    자리의 인덱스. 단일 고리(mIm 등)는 C2=인덱스0, ZIF-69 cbIm 벤조환 치환은
    [C2,N3,C4,b1,b2,b3,b4,C5,N1] 중 b2=인덱스4 (CBIM_ARYL_ATTACHMENT_INDEX).

    [완화 조치] Kabsch는 고리만 정합할 뿐 치환기 방향(고리 바깥쪽 결합축 기준 회전)은
    프래그먼트 임베딩이 우연히 정해준 값 그대로라, 인접한 두 사이트가 동시에 부피가 큰
    치환기(nIm의 NO2 등)로 바뀌면 서로 정면충돌하는 경우가 실측으로 확인됐다(원자간
    거리 0.2~0.5 Å, ZIF-67 50%mIm/50%nIm 조성에서 seed 무관하게 재현). 완전한 힘장
    이완 없이도, 고리 바깥쪽 결합축을 회전축 삼아 치환기를 n_trial_angles개 각도로
    돌려보고 이미 배치된 원자들과의 최소 거리가 가장 큰 각도를 선택하는 것만으로
    상당수의 충돌을 피할 수 있다 (완전한 해결책은 아님 -> RASPA 투입 전 UFF 등 힘장
    이완을 권장)."""
    # 셀 경계를 걸친 고리를 펼쳐서 정합한다. 원시 좌표를 그대로 쓰면 12/24 고리가
    # 깨져 치환기가 공동 중심에 버려진다 (_unwrap 참고).
    cell = np.asarray(atoms.get_cell())
    ring_pos = _unwrap(atoms, site["ring"])
    frag_ring_pos = fragment["coords"][fragment["ring_idx"]]
    R, Pc, Qc = kabsch(ring_pos, frag_ring_pos)

    subst_coords = fragment["coords"][fragment["subst_idx"]] - Qc
    axis = ring_pos[attachment_ring_index] - Pc  # 고리 중심 -> 치환 지점, 고리 정합을 깨지 않는 유일한 회전축

    if avoid_positions is not None and len(avoid_positions) > 0 and np.linalg.norm(axis) > 1e-6:
        best_theta, best_score = 0.0, -1.0
        for theta in np.linspace(0, 2 * np.pi, n_trial_angles, endpoint=False):
            Rz = _rotation_about_axis(axis, theta)
            trial_pos = (R @ subst_coords.T).T @ Rz.T + Pc
            # 충돌 판정도 주기경계를 감안해야 한다. 원시 거리로 재면 셀 경계
            # 건너편 원자와의 충돌을 통째로 놓친다.
            score = _mic_min_distance(np.asarray(avoid_positions), trial_pos, cell)
            if score > best_score:
                best_score, best_theta = score, theta
        Rz = _rotation_about_axis(axis, best_theta)
        final_pos = (R @ subst_coords.T).T @ Rz.T + Pc
    else:
        final_pos = (R @ subst_coords.T).T + Pc

    new_atoms = list(zip((fragment["symbols"][i] for i in fragment["subst_idx"]), final_pos))
    return site["substituent"], new_atoms


def add_eqeq_charges(cif_path):
    """OpenBabel에 내장된 EQeq(Wilmer et al. extended charge equilibration)로
    부분전하를 계산해 CIF의 _atom_site_charge 컬럼에 기록한다.
    RASPA는 simulation.input에 UseChargesFromCIFFile yes를 주면 이 컬럼을 그대로 읽는다.

    이게 없으면(UseChargesFromCIFFile no) RASPA가 EWG 리간드 후보들 간 정전기적
    차이를 전혀 못 보므로, 이 프로젝트의 핵심 가설(EWG-CO2 정전기 상호작용)을 검증할
    수 없다 -> PROJECT_HANDOVER.md가 "최우선/치명적"으로 지정한 단계.
    """
    with open(cif_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with tempfile.NamedTemporaryFile(suffix=".pqr", delete=False) as tmp:
        pqr_path = tmp.name
    try:
        proc = subprocess.run(
            ["obabel", cif_path, "-O", pqr_path, "--partialcharge", "eqeq"],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not os.path.exists(pqr_path):
            raise RuntimeError(f"obabel EQeq 실행 실패:\n{proc.stderr}")

        # PQR의 원자 순서는 obabel이 입력 CIF를 읽은 순서를 그대로 보존하므로
        # (원소 심볼 시퀀스로 검증 완료) 위치 기준으로 그대로 매칭한다.
        charges = []
        with open(pqr_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(("HETATM", "ATOM")):
                    charges.append(float(line.split()[-3]))
    finally:
        if os.path.exists(pqr_path):
            os.remove(pqr_path)

    # ASE가 쓰는 _atom_site_occupancy 다음 줄부터가 원자 데이터 행이므로,
    # 태그 목록에 _atom_site_charge를 추가하고 각 데이터 행 끝에 전하 값을 붙인다.
    tag_line_idx = next(i for i, l in enumerate(lines) if "_atom_site_occupancy" in l)
    data_start = tag_line_idx + 1
    n_atoms = sum(1 for l in lines[data_start:] if l.strip())
    if n_atoms != len(charges):
        raise RuntimeError(f"원자 수 불일치: CIF {n_atoms}개 vs EQeq 전하 {len(charges)}개")

    lines[tag_line_idx] = lines[tag_line_idx].rstrip("\n") + "\n  _atom_site_charge\n"
    for offset, charge in enumerate(charges):
        li = data_start + offset
        lines[li] = lines[li].rstrip("\n") + f"  {charge: .6f}\n"

    with open(cif_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"     EQeq 부분전하 기록 완료 (원자 {len(charges)}개, 전하 합 {sum(charges):+.4f})")


def _finalize_and_write(atoms, output_cif, base_cif, composition, seed, n_sites):
    """치환 완료된 atoms를 CIF로 기록하고 공통 후처리(레거시 대칭 태그, EQeq 전하,
    위상 드리프트 플래그, 충돌 최종 확인, meta.json)를 수행한다.
    generate_mtv_cif()와 generate_mtv_cif_zif69_aryl() 둘 다 이 공통 마무리 단계를 쓴다."""
    min_dist = _min_pairwise_distance(atoms)
    if min_dist < 0.7:
        print(f"     [경고] 최소 원자간 거리 {min_dist:.3f} Å — 치환기 회전으로도 못 피한 충돌이 남아있음. "
              "RASPA/Zeo++ 투입 전 UFF 등 힘장 이완을 강력히 권장.")
    else:
        print(f"     최소 원자간 거리 {min_dist:.3f} Å (충돌 회피 회전 적용 후)")

    write(output_cif, atoms)

    # ASE가 기록하는 신형(mmCIF) 대칭군 태그는 RASPA/Zeo++의 CIF 파서가 인식하지 못해
    # 조용히 실패하므로, 두 도구가 요구하는 구형 태그로 변환한다.
    with open(output_cif, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("_space_group_name_H-M_alt", "_symmetry_space_group_name_H-M")
    content = content.replace("_space_group_IT_number", "_symmetry_Int_Tables_number")
    content = content.replace("_space_group_symop_operation_xyz", "_symmetry_equiv_pos_as_xyz")
    with open(output_cif, "w", encoding="utf-8") as f:
        f.write(content)

    add_eqeq_charges(output_cif)

    topology_risks = check_topology_drift_risk(composition)
    for risk in topology_risks:
        print(f"     [위상 드리프트 주의] {risk['ligand']} 비율 {risk['fraction']:.2f} — {risk['note']}")

    meta_path = output_cif.rsplit(".", 1)[0] + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "base_cif": base_cif,
            "composition": composition,
            "seed": seed,
            "min_pairwise_distance": round(float(min_dist), 4),
            "topology_drift_risks": topology_risks,
        }, f, indent=2, ensure_ascii=False)

    print(f"[OK] {output_cif} 생성 완료 (링커 {n_sites}개, 조성 {composition})")


def generate_mtv_cif(base_cif, site_map_json, composition, output_cif, seed=0):
    assert abs(sum(composition.values()) - 1.0) < 1e-6, "조성비 합은 1이어야 함"

    atoms = read(base_cif)
    with open(site_map_json) as f:
        sites = json.load(f)

    rng = np.random.default_rng(seed)
    names, probs = list(composition.keys()), list(composition.values())
    assignment = rng.choice(names, size=len(sites), p=probs)

    fragments = {n: build_fragment(n) for n in set(assignment) if n != "mIm"}

    # [버그 수정] 원래 코드는 사이트를 하나씩 삭제+삽입하며 순차적으로 atoms를 갱신했는데,
    # 이 CIF는 같은 링커의 고리 원자들이 서로 아주 먼 인덱스에 흩어져 저장돼 있어서
    # (예: 한 링커의 N3/N1이 인덱스 4번과 140번), 한 사이트를 삭제하는 순간 다른 사이트의
    # ring/substituent 인덱스가 조용히 밀려 엉뚱한 원자를 골라버렸다. 그 결과 Zn이 12->10개로
    # 줄고 원자간 최소 거리가 0.157 Å까지 겹치는 심각한 구조 파손이 발생했다.
    # 모든 사이트의 Kabsch 정합/삭제 대상 인덱스는 반드시 원본 atoms(불변)를 기준으로 먼저
    # 전부 계산해두고, 실제 삭제·삽입은 마지막에 한 번만 수행해 인덱스 밀림을 원천 차단한다.
    remove_indices = set()
    new_symbols, new_positions = [], []
    # 충돌 회피용 "이미 배치된 원자" 목록을 원본 프레임워크로 시작해 사이트를 처리할
    # 때마다 새로 놓인 치환기 원자로 계속 누적한다 -> 뒤에 처리되는 사이트가 앞서 배치된
    # 치환기와의 충돌도 감안해서 회전 각도를 고를 수 있다.
    avoid_positions = atoms.get_positions().copy()
    for site, lig in zip(sites, assignment):
        if lig == "mIm":
            continue
        subst_idx, new_atoms = plan_substitution(atoms, site, fragments[lig], avoid_positions=avoid_positions)
        remove_indices.update(subst_idx)
        for sym, pos in new_atoms:
            new_symbols.append(sym)
            new_positions.append(pos)
            avoid_positions = np.vstack([avoid_positions, pos])

    keep_mask = np.ones(len(atoms), dtype=bool)
    keep_mask[sorted(remove_indices)] = False
    atoms = atoms[keep_mask]
    if new_symbols:
        atoms += Atoms(symbols=new_symbols, positions=new_positions)

    _finalize_and_write(atoms, output_cif, base_cif, composition, seed, len(sites))


def generate_mtv_cif_zif69_aryl(base_cif, bicyclic_site_map_json, aryl_composition, output_cif, seed=0):
    """[Priority 3, 문서 권장 방향] ZIF-69의 cbIm:nIm 1:1 비율은 그대로 두고,
    cbIm 벤조환의 아릴 치환기(기본 Cl)만 LIGAND_LIBRARY_CBIM_ARYL 조성대로 SALE식
    교체한다. nIm 자리는 site_map에 아예 포함되지 않으므로 손대지 않는다."""
    assert abs(sum(aryl_composition.values()) - 1.0) < 1e-6, "조성비 합은 1이어야 함"

    atoms = read(base_cif)
    with open(bicyclic_site_map_json) as f:
        sites = json.load(f)

    rng = np.random.default_rng(seed)
    names, probs = list(aryl_composition.keys()), list(aryl_composition.values())
    assignment = rng.choice(names, size=len(sites), p=probs)

    fragments = {n: build_fragment_cbim_aryl(n) for n in set(assignment) if n != "clIm_aryl"}

    remove_indices = set()
    new_symbols, new_positions = [], []
    avoid_positions = atoms.get_positions().copy()
    for site, lig in zip(sites, assignment):
        if lig == "clIm_aryl":
            continue  # 원래 결정구조의 Cl을 그대로 유지 (교체 없음)
        # plan_substitution은 site["ring"]/site["substituent"]를 기대하므로
        # bicyclic 사이트의 필드명을 맞춰 재구성한다.
        remapped_site = {"ring": site["bicyclic_ring"], "substituent": site["aryl_substituent"]}
        subst_idx, new_atoms = plan_substitution(
            atoms, remapped_site, fragments[lig], avoid_positions=avoid_positions,
            attachment_ring_index=CBIM_ARYL_ATTACHMENT_INDEX,
        )
        remove_indices.update(subst_idx)
        for sym, pos in new_atoms:
            new_symbols.append(sym)
            new_positions.append(pos)
            avoid_positions = np.vstack([avoid_positions, pos])

    keep_mask = np.ones(len(atoms), dtype=bool)
    keep_mask[sorted(remove_indices)] = False
    atoms = atoms[keep_mask]
    if new_symbols:
        atoms += Atoms(symbols=new_symbols, positions=new_positions)

    _finalize_and_write(atoms, output_cif, base_cif, aryl_composition, seed, len(sites))


if __name__ == "__main__":
    generate_mtv_cif(
        base_cif="ZIF8_mIm_only_P1.cif",
        site_map_json="site_map.json",
        composition={"mIm": 0.5, "clIm": 0.5},
        output_cif="ZIF8_mIm50_clIm50.cif",
    )
