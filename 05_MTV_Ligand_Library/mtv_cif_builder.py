"""
tag_zif_linkers.py가 만든 site_map.json을 이용해 목표 조성비대로
리간드를 치환하고 RASPA 입력용 CIF를 생성한다.

pip install ase rdkit numpy --break-system-packages
conda install -c conda-forge openbabel   # EQeq 부분전하 계산용 (obabel CLI)
"""
import json
import os
import shutil
import subprocess
import sys
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
    # [2026-08-06 추가] 실제로 보고된 gme ZIF 4종에 대응하는 벤조환 치환기.
    # 100% 치환이 각각 그 물질이다. 실험 CIF 는 결정학적으로 무질서해서
    # (두 링커가 자리를 나눠 갖고 치환기가 두 위치에 반씩 흩어져 있다) 그대로는
    # 못 쓴다. 정렬된 ZIF-69 골격에 치환기만 바꿔 넣으면 위상·금속·nIm 비율·
    # 사이트맵·시드가 전부 고정되므로 -SO3H 결과와 apples-to-apples 로 비교된다.
    # 실험 CIF 는 격자상수 대조용으로만 쓴다(기공값은 게스트 제거 후에야 유효).
    "nbIm_aryl":  "c1nc2cc([N+](=O)[O-])ccc2[nH]1",   # 5-nitro   -> ZIF-78
    "mbIm_aryl":  "c1nc2cc(C)ccc2[nH]1",              # 5-methyl  -> ZIF-79
    "brbIm_aryl": "c1nc2cc(Br)ccc2[nH]1",             # 5-bromo   -> ZIF-81
    "cnbIm_aryl": "c1nc2cc(C#N)ccc2[nH]1",            # 5-cyano   -> ZIF-82 (빌더로 생성 불가, C-아릴 축과 공선)
    # [2026-08-06 추가] CCUS 링커 검토 보고서(외부 문서) 교차검증 후 등록.
    # 그 보고서가 1순위로 제안한 mslm(2-메틸설포닐이미다졸레이트)은 SMILES 상
    # 이미다졸 C2(sod, 창구 방향)에 붙는 자리였다 -- ZIF-8에서 -SO3H로 이미 반증된
    # 실패 패턴(Q_st 25에서 정체)과 같은 자리다. 같은 화학(설폰 EWG, H-bond donor
    # 없음)을 벤조 b2(gme, 공동 방향)로 옮긴 버전이 이 mslm_aryl이다.
    "mslm_aryl":  "c1nc2cc(S(=O)(=O)C)ccc2[nH]1",     # 5-메틸설포닐 (-SO2CH3)
    # -SO3H보다 훨씬 작아 인접 자리 겹침(0.57 A, 5-6절 saIm 문제)을 회피할 목적의
    # 저부피 EWG 후보. 100% 치환을 피하면서 목표대에 드는지가 질문이다(브리핑 8-3).
    "fbIm_aryl":  "c1nc2cc(F)ccc2[nH]1",              # 5-플루오로 (-F)
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


def _substituent_positions_at_angles(atoms, site, fragment, attachment_ring_index,
                                     angles):
    """한 사이트의 치환기를 여러 회전각으로 배치했을 때의 좌표를 전부 돌려준다.

    plan_substitution 과 같은 정합·회전을 쓰되, '이미 배치된 원자'를 보지 않는다.
    자리쌍의 **원리적** 충돌 여부(어떤 회전으로도 못 피하는가)를 보려면 배치 순서와
    무관한 값이 필요하기 때문이다.
    """
    ring_pos = _unwrap(atoms, site["ring"])
    frag_ring_pos = fragment["coords"][fragment["ring_idx"]]
    R, Pc, Qc = kabsch(ring_pos, frag_ring_pos)
    subst_coords = fragment["coords"][fragment["subst_idx"]] - Qc
    axis = ring_pos[attachment_ring_index] - Pc
    base = (R @ subst_coords.T).T
    if np.linalg.norm(axis) < 1e-6:
        return [base + Pc for _ in angles]
    return [base @ _rotation_about_axis(axis, t).T + Pc for t in angles]


def optimize_substituent_rotations(atoms, chosen, sites, fragments, ligs,
                                   attachment_ring_index=0, n_angles=24, sweeps=6):
    """치환기 회전각을 **좌표 상승법으로 함께** 최적화한다.

    [왜 순차 배치로는 안 되는가 — 2026-08-14]
        기존 코드는 사이트를 순서대로 돌면서, 그 시점까지 배치된 원자만 보고 각도를
        골랐다. 그러면 먼저 놓인 치환기는 **아직 존재하지 않는 이웃을 고려하지 못하고**,
        나중에 놓이는 치환기는 이미 굳어 버린 이웃에 맞춰 최선을 다할 뿐이다.

        실측 결과가 그것이다. −NO₂ 자리쌍의 쌍별 최적 분리는 2.90 Å 인데, 실제로
        만들어진 구조에서는 O–O 가 **1.142 Å** 이었다. 기하학이 불가능해서가 아니라
        배치 순서 때문에 도달하지 못한 것이다. −SO₃H 는 0.924 Å 까지 갔다.

        한 바퀴 더 돌면서 각 치환기를 '나머지 전부'에 대해 다시 고르면 이 격차가
        메워진다. 각도는 이산(n_angles)이고 목적함수는 최소거리라 단조 증가하므로
        몇 번의 스윕이면 수렴한다.

    반환: {site_index: 최종 좌표 배열}, 달성한 최소 원자간 거리
    """
    cell = np.asarray(atoms.get_cell())
    all_sym = atoms.get_chemical_symbols()
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    cand = {k: _substituent_positions_at_angles(atoms, sites[k], fragments[ligs[k]],
                                                attachment_ring_index, angles)
            for k in chosen}
    fsym = {k: [fragments[ligs[k]]["symbols"][i]
                for i in fragments[ligs[k]]["subst_idx"]] for k in chosen}

    # 골격 = 치환으로 제거될 원자를 뺀 나머지. 제거될 Cl 을 장애물로 세면 안 된다.
    removed = set()
    for k in chosen:
        removed.update(sites[k]["substituent"])

    # [함정] 목적함수를 '최소 거리' 로 두면 안 된다.
    #
    # 치환기의 뿌리 원자는 자기 고리의 부착 탄소와 **결합**해 있다(S–C 1.83 Å).
    # 그 거리는 회전과 무관하게 고정이라, 최소 거리를 최대화하려 하면 모든 각도가
    # 1.83 에서 동점이 되고 목적함수가 각도를 구별하지 못한다. 그러면 최적화가
    # 아무 각도나 고르고, 실제로 그래서 이웃 Cl 과 1.955 Å 까지 붙은 배치가 나왔다.
    #
    # 그래서 (1) 자기 고리 원자는 장애물에서 빼고 (2) 거리 대신 vdW 여유를 쓴다.
    def obstacles_for(k, others_pos, others_sym):
        own = set(sites[k]["ring"]) | set(sites[k]["substituent"])
        keep = [i for i in range(len(atoms)) if i not in removed and i not in own]
        p = [atoms.get_positions()[keep]] + others_pos
        s = [[all_sym[i] for i in keep]] + others_sym
        return np.vstack(p), [x for sub in s for x in sub]

    cur = {k: 0 for k in chosen}
    for sweep in range(sweeps):
        moved = False
        for k in chosen:
            op = [cand[m][cur[m]] for m in chosen if m != k]
            os_ = [fsym[m] for m in chosen if m != k]
            pos_o, sym_o = obstacles_for(k, op, os_)
            best_t = max(range(n_angles),
                         key=lambda t: _vdw_margin(fsym[k], cand[k][t],
                                                   sym_o, pos_o, cell))
            if best_t != cur[k]:
                cur[k] = best_t
                moved = True
        if not moved:
            break

    final = {k: cand[k][cur[k]] for k in chosen}
    worst = np.inf
    for k in chosen:
        op = [final[m] for m in chosen if m != k]
        os_ = [fsym[m] for m in chosen if m != k]
        pos_o, sym_o = obstacles_for(k, op, os_)
        worst = min(worst, _vdw_margin(fsym[k], final[k], sym_o, pos_o, cell))
    return final, float(worst)


# 충돌 판정용 vdW 반지름 (Å). ase.data.vdw_radii 는 일부 원소가 NaN 이라 직접 둔다.
VDW_R = {"H": 1.20, "C": 1.70, "N": 1.55, "O": 1.52, "F": 1.47,
         "S": 1.80, "Cl": 1.75, "Br": 1.85, "I": 1.98}
# 최적 회전에서도 vdW 접촉의 이 배수보다 가까우면 그 자리쌍은 배타적이다.
#
# 고정 거리로 자르면 안 된다 -- −CH₃ 의 최선값 2.49 Å 은 H···H 라 정상 접촉(vdW 합
# 2.40)이고, −SO₃H 의 최선값 2.49 Å 은 중원자라 심각한 겹침(vdW 합 3.32)이다.
# 같은 숫자가 한쪽은 정상, 한쪽은 결함이다. 원소를 봐야 갈린다.
VDW_FRAC = 0.85


def _vdw_margin(sym_a, pos_a, sym_b, pos_b, cell):
    """두 원자 집합 사이의 vdW 여유. 음수면 겹친 것이다."""
    diff = pos_a[:, None, :] - pos_b[None, :, :]
    frac = np.linalg.solve(cell.T, diff.reshape(-1, 3).T).T
    frac -= np.round(frac)
    d = np.linalg.norm(frac @ cell, axis=-1).reshape(len(pos_a), len(pos_b))
    floor = VDW_FRAC * np.array([[VDW_R.get(a, 1.7) + VDW_R.get(b, 1.7)
                                  for b in sym_b] for a in sym_a])
    return float((d - floor).min())


def substituent_conflict_graph(atoms, sites, fragment, attachment_ring_index=0,
                               n_angles=12, prefilter=14.0):
    """동시에 치환기를 달 수 없는 자리쌍의 목록을 반환한다.

    [왜 필요한가 — 2026-08-14]
        기존 빌더는 자리를 rng.choice 로 고르고, 충돌은 plan_substitution 의 회전
        탐색으로만 완화했다. 그런데 회전축이 '고리중심 -> 치환 지점' 이라 치환기의
        **뿌리 원자는 그 축 위에 있어 회전해도 거의 안 움직인다.** −SO₃H 의 황이
        그렇다. 그래서 인접한 두 자리를 동시에 고르면 S–S 2.642 Å 이 되고, 회전으로는
        절대 못 푼다. 실제로 saIm 050/075/100 이 전부 그렇게 만들어졌다
        (21_ZIF69_MTV/STRUCTURE_DEFECT.md).

        고칠 자리는 회전이 아니라 **자리 선택**이다. 어떤 회전 조합으로도 떨어지지
        않는 자리쌍을 미리 찾아 두고, 그 쌍은 동시에 고르지 않는다.

    판정은 **최적 회전 조합에서의 vdW 여유**로 한다. 회전으로 풀 수 있는 것은
    회전이 풀게 두고, 어떤 회전으로도 안 되는 쌍만 배타적이라고 부른다.
    """
    cell = np.asarray(atoms.get_cell())
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    placements = [_substituent_positions_at_angles(atoms, s, fragment,
                                                   attachment_ring_index, angles)
                  for s in sites]
    sym = [fragment["symbols"][i] for i in fragment["subst_idx"]]
    # 자리별 대표 위치(치환 지점)로 먼 쌍을 먼저 걸러낸다.
    anchors = np.array([_unwrap(atoms, s["ring"])[attachment_ring_index] for s in sites])

    edges = []
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            if _mic_min_distance(anchors[i:i + 1], anchors[j:j + 1], cell) > prefilter:
                continue
            best = -np.inf
            for pi in placements[i]:
                for pj in placements[j]:
                    m = _vdw_margin(sym, pi, sym, pj, cell)
                    if m > best:
                        best = m
                    if best >= 0.0:
                        break
                if best >= 0.0:
                    break
            if best < 0.0:
                edges.append((i, j, round(float(best), 3)))
    return edges


def forcing_pairs(atoms, sites, fragment, attachment_ring_index=0, n_angles=12,
                  prefilter=14.0):
    """자리 i 를 치환하면 자리 j 도 **반드시** 치환해야 하는 쌍.

    [왜 이게 따로 필요한가]
        배타 관계(둘 다 치환하면 충돌)만 보면 절반의 제약을 놓친다. 치환하지 않은
        자리에는 원래 치환기(ZIF-69 는 Cl)가 **그대로 남아 있고**, 새로 단 −SO₃H 가
        그 Cl 과 부딪칠 수 있다. 그 경우 해법은 두 가지뿐이다 —
        i 를 치환하지 않거나, j 도 치환해서 Cl 을 없애거나.

        i 와 j 가 배타적이면서 동시에 강제 관계이면 **i 는 아예 쓸 수 없는 자리**다.
    """
    cell = np.asarray(atoms.get_cell())
    all_sym = atoms.get_chemical_symbols()
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)
    placements = [_substituent_positions_at_angles(atoms, s, fragment,
                                                   attachment_ring_index, angles)
                  for s in sites]
    fsym = [fragment["symbols"][i] for i in fragment["subst_idx"]]
    anchors = np.array([_unwrap(atoms, s["ring"])[attachment_ring_index] for s in sites])
    pos = atoms.get_positions()

    out = []
    for i in range(len(sites)):
        for j in range(len(sites)):
            if i == j:
                continue
            if _mic_min_distance(anchors[i:i + 1], anchors[j:j + 1], cell) > prefilter:
                continue
            dsym = [all_sym[k] for k in sites[j]["substituent"]]
            dpos = pos[sites[j]["substituent"]]
            best = max(_vdw_margin(fsym, p, dsym, dpos, cell) for p in placements[i])
            if best < 0.0:
                out.append((i, j, round(float(best), 3)))
    return out


def choose_conflict_free_sites(n_target, n_sites, exclusive, forcing=(), seed=0,
                               tries=2000):
    """배타 관계와 강제 관계를 **동시에** 만족하는 크기 n_target 의 자리 집합.

    무작위 탐욕법을 여러 번 돌려 가장 큰 유효 집합을 찾는다. 자리 수가 24개
    수준이라 이걸로 충분하다. 실패하면 **달성 가능한 최대치를 알려주고 예외를
    던진다** -- 조성을 조용히 바꾸면 나중에 무엇을 계산했는지 알 수 없게 된다.
    """
    exc = {k: set() for k in range(n_sites)}
    for i, j, _ in exclusive:
        exc[i].add(j)
        exc[j].add(i)
    frc = {k: set() for k in range(n_sites)}
    for i, j, _ in forcing:
        frc[i].add(j)

    def closure(S):
        S = set(S)
        stack = list(S)
        while stack:
            i = stack.pop()
            for j in frc[i]:
                if j not in S:
                    S.add(j)
                    stack.append(j)
        return S

    rng = np.random.default_rng(seed)
    best = set()
    for _ in range(tries):
        S = set()
        for k in rng.permutation(n_sites):
            T = closure(S | {int(k)})
            if len(T) > n_target:
                continue
            if all(not (exc[i] & T) for i in T):
                S = T
            if len(S) == n_target:
                break
        if len(S) > len(best):
            best = S
        if len(best) == n_target:
            return sorted(best), len(best)

    # 상한을 따로 구해 메시지에 담는다(목표치 제한 없이 최대로 키워 본다).
    cap = set()
    for _ in range(tries):
        S = set()
        for k in rng.permutation(n_sites):
            T = closure(S | {int(k)})
            if all(not (exc[i] & T) for i in T):
                S = T
        if len(S) > len(cap):
            cap = S
    raise ValueError(
        f'자리 {n_target}개를 충돌 없이 고를 수 없습니다. 이 치환기의 최대 '
        f'무충돌 자리 수는 {len(cap)}개({len(cap) / n_sites:.0%})입니다. '
        f'배타쌍 {len(exclusive)}개, 강제쌍 {len(forcing)}개.')


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
        # obabel 을 PATH 에만 의존해 부르면, 환경을 activate 하지 않고 인터프리터를
        # 절대경로로 실행했을 때 FileNotFoundError 로 죽는다. 같은 환경의 bin/ 을
        # 먼저 본다.
        obabel = shutil.which("obabel") or os.path.join(
            os.path.dirname(sys.executable), "obabel")
        proc = subprocess.run(
            [obabel, cif_path, "-O", pqr_path, "--partialcharge", "eqeq"],
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


def _finalize_and_write(atoms, output_cif, base_cif, composition, seed, n_sites,
                        extra_meta=None):
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
    meta = {
        "base_cif": base_cif,
        "composition": composition,
        "seed": seed,
        "min_pairwise_distance": round(float(min_dist), 4),
        "topology_drift_risks": topology_risks,
    }
    meta.update(extra_meta or {})
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

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


def generate_mtv_cif_zif69_aryl(base_cif, bicyclic_site_map_json, aryl_composition,
                                output_cif, seed=0, conflict_aware=True):
    """[Priority 3, 문서 권장 방향] ZIF-69의 cbIm:nIm 1:1 비율은 그대로 두고,
    cbIm 벤조환의 아릴 치환기(기본 Cl)만 LIGAND_LIBRARY_CBIM_ARYL 조성대로 SALE식
    교체한다. nIm 자리는 site_map에 아예 포함되지 않으므로 손대지 않는다.

    conflict_aware: 자리를 무작위로 고르지 않고, **동시에 달 수 없는 자리쌍을 먼저
        찾아 피해서** 고른다. 기본값 True. 2026-08-14 이전 구조는 전부 False 상태로
        만들어졌고 그래서 치환기끼리 관통했다(STRUCTURE_DEFECT.md).
        요청한 치환율이 무충돌로 달성 불가능하면 **예외를 던진다** -- 조성을 조용히
        낮추면 무엇을 계산했는지 알 수 없게 된다.
    """
    assert abs(sum(aryl_composition.values()) - 1.0) < 1e-6, "조성비 합은 1이어야 함"

    atoms = read(base_cif)
    with open(bicyclic_site_map_json) as f:
        sites = json.load(f)
    # plan_substitution / 충돌 그래프는 site["ring"], site["substituent"] 를 기대한다.
    # bicyclic 사이트맵의 필드명을 한 번만 맞춰 두고 아래에서 계속 쓴다.
    sites = [{"ring": s["bicyclic_ring"], "substituent": s["aryl_substituent"]}
             for s in sites]

    rng = np.random.default_rng(seed)
    names, probs = list(aryl_composition.keys()), list(aryl_composition.values())

    subs = [n for n, p in zip(names, probs) if n != "clIm_aryl" and p > 0]
    conflict_info = None
    if conflict_aware and len(subs) == 1:
        lig = subs[0]
        frac = dict(zip(names, probs))[lig]
        n_target = int(round(frac * len(sites)))
        frag = build_fragment_cbim_aryl(lig)
        edges = substituent_conflict_graph(
            atoms, sites, frag, attachment_ring_index=CBIM_ARYL_ATTACHMENT_INDEX)
        forced = forcing_pairs(
            atoms, sites, frag, attachment_ring_index=CBIM_ARYL_ATTACHMENT_INDEX)
        chosen, max_found = choose_conflict_free_sites(n_target, len(sites), edges,
                                                       forcing=forced, seed=seed)
        assignment = np.array(["clIm_aryl"] * len(sites), dtype=object)
        for k in chosen:
            assignment[k] = lig
        conflict_info = {"conflict_aware": True, "n_conflict_pairs": len(edges),
                         "n_forcing_pairs": len(forced),
                         "n_sites": len(sites), "n_substituted": len(chosen),
                         "requested_fraction": frac,
                         "achieved_fraction": round(len(chosen) / len(sites), 6),
                         "chosen_sites": sorted(int(k) for k in chosen)}
        print(f"     충돌 회피 배치: 배타적 자리쌍 {len(edges)}쌍, "
              f"강제쌍 {len(forced)}쌍, {len(chosen)}/{len(sites)} 자리 치환")
    else:
        if conflict_aware and len(subs) > 1:
            print("     [주의] 치환기가 2종 이상이라 충돌 회피 배치를 건너뜁니다 — "
                  "무작위 배치입니다.")
        assignment = rng.choice(names, size=len(sites), p=probs)
        conflict_info = {"conflict_aware": False}

    fragments = {n: build_fragment_cbim_aryl(n) for n in set(assignment) if n != "clIm_aryl"}

    chosen = [k for k, lig in enumerate(assignment) if lig != "clIm_aryl"]
    ligs = {k: assignment[k] for k in chosen}

    remove_indices = set()
    new_symbols, new_positions = [], []
    if chosen:
        # 순차 배치가 아니라 **함께** 최적화한다. 순차로 하면 먼저 놓인 치환기가
        # 아직 없는 이웃을 고려하지 못해, 기하학적으로 가능한 분리에 도달하지 못한다
        # (−NO₂ 쌍별 최적 2.90 Å 인데 실제 구조는 1.142 Å 이었다).
        final, worst = optimize_substituent_rotations(
            atoms, chosen, sites, fragments, ligs,
            attachment_ring_index=CBIM_ARYL_ATTACHMENT_INDEX)
        print(f"     회전 동시 최적화 후 최악 vdW 여유 {worst:+.3f} Å")
        conflict_info["worst_vdw_margin_after_rotation"] = round(worst, 4)
        for k in chosen:
            remove_indices.update(sites[k]["substituent"])
            syms = [fragments[ligs[k]]["symbols"][i]
                    for i in fragments[ligs[k]]["subst_idx"]]
            for sym, pos in zip(syms, final[k]):
                new_symbols.append(sym)
                new_positions.append(pos)

    keep_mask = np.ones(len(atoms), dtype=bool)
    keep_mask[sorted(remove_indices)] = False
    atoms = atoms[keep_mask]
    if new_symbols:
        atoms += Atoms(symbols=new_symbols, positions=new_positions)

    _finalize_and_write(atoms, output_cif, base_cif, aryl_composition, seed, len(sites),
                        extra_meta=conflict_info)


if __name__ == "__main__":
    generate_mtv_cif(
        base_cif="ZIF8_mIm_only_P1.cif",
        site_map_json="site_map.json",
        composition={"mIm": 0.5, "clIm": 0.5},
        output_cif="ZIF8_mIm50_clIm50.cif",
    )
