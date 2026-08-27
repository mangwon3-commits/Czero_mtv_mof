"""**이종 쌍** 치환기 충돌 그래프 — 한 번도 계산된 적이 없는 빈칸.

[왜 필요한가 — 08-26 에 열린 빈칸]
    `mtv_cif_builder.substituent_conflict_graph` 는 `fragment` 를 **하나만**
    받아 양쪽에 같은 `sym` 을 씁니다. 즉 **동종 쌍만** 봅니다. 그리고
    `mtv_cif_builder.py:798` 이 `if conflict_aware and len(subs) == 1` 이라
    혼합 조성에서는 그래프가 **아예 만들어지지 않습니다.**

        확인된 것   치환기 8종 각각의 **동종** 쌍에 배타 관계 없음 (전부 0)
        빈칸        −SO₃H 옆 −NO₂ 같은 **이종** 쌍은 아무도 잰 적이 없음

    그런데 우리 혼합 조성 셋(`sa50nb50` `ms50nb50` `sa25nb75`)은 **전부
    이종 쌍을 갖습니다.** 그리고 `plan_substitution` 주석(`:216`)이 하필
    **−NO₂ 쌍이 ZIF-67 에서 정면충돌**했다고 적어 뒀습니다.

[무엇을 하는가]
    같은 판정 기준(**최적 회전 조합에서의 vdW 여유가 음수면 배타**)을 두
    **다른** 조각에 적용합니다. `_vdw_margin` 이 이미 양쪽 `sym` 을 따로
    받으므로 호출부만 고치면 됩니다.

[왜 빌더를 안 고치고 따로 쓰는가]
    `mtv_cif_builder.py` 는 **전 계열이 공유하는 파일**입니다. 45개 구조가
    그것으로 만들어졌고, 손대면 회귀 위험이 전 계열에 퍼집니다.
    **이것은 진단이지 생성이 아니므로** 읽기만 하는 별도 파일로 둡니다.
    이종 배타가 실제로 나오면 그때 빌더 확장을 별도로 등록합니다.

[판정 — 수를 보기 전에]
    배타 쌍 0        -> 혼합 조성에 기하 제약이 없다. 무작위 배치가
                        구조적으로 문제없음이 확인된다
    배타 쌍 > 0      -> 혼합 셋이 **배타 쌍을 포함한 채 만들어졌을 수 있다.**
                        각 구조에서 실제로 그 쌍이 동시 치환됐는지 확인해야
                        하고, 됐다면 그 구조는 재빌드 대상이다

사용:
    python3 hetero_conflict_graph.py
"""
import itertools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, "05_MTV_Ligand_Library")
sys.path.insert(0, LIGLIB)

BASE_CIF = os.path.join(LIGLIB, "ZIF69_base.cif")
SITE_MAP = os.path.join(LIGLIB, "site_map_zif69_bicyclic.json")

# 혼합 조성에 실제로 쓰인 치환기. 여기에 모체 clIm_aryl 도 넣습니다 —
# 24/24 가 아닌 조성에서는 치환기가 모체 옆에 앉기 때문입니다.
LIGANDS = ["saIm_aryl", "nbIm_aryl", "mslm_aryl", "clIm_aryl"]

N_ANGLES = 12          # 빌더와 동일
PREFILTER = 14.0       # 빌더와 동일


def main():
    import json

    from mtv_cif_builder import (CBIM_ARYL_ATTACHMENT_INDEX, _mic_min_distance,
                                 _substituent_positions_at_angles, _unwrap,
                                 _vdw_margin, attachment_index,
                                 build_fragment_cbim_aryl)
    from ase.io import read

    atoms = read(BASE_CIF)
    # 빌더(mtv_cif_builder.py:791)와 **같은 변환**을 씁니다. 원본 site_map 은
    # bicyclic_ring / aryl_substituent 라는 이름이고 하류 함수는 ring /
    # substituent 를 기대합니다.
    sites = [{"ring": s["bicyclic_ring"], "substituent": s["aryl_substituent"]}
             for s in json.load(open(SITE_MAP, encoding="utf-8"))]
    cell = np.asarray(atoms.get_cell())
    angles = np.linspace(0, 2 * np.pi, N_ANGLES, endpoint=False)

    print(f"  자리 {len(sites)}개 · 치환기 {len(LIGANDS)}종 · 회전 {N_ANGLES}각")
    print(f"  판정: 모든 회전 조합에서 vdW 여유가 음수면 **배타**")
    print(f"  (빌더 substituent_conflict_graph 와 같은 기준. 조각만 둘로 나눔)\n")

    frags, place, syms = {}, {}, {}
    for lig in LIGANDS:
        f = build_fragment_cbim_aryl(lig)
        frags[lig] = f
        syms[lig] = [f["symbols"][i] for i in f["subst_idx"]]
        place[lig] = [_substituent_positions_at_angles(
            atoms, s, f, CBIM_ARYL_ATTACHMENT_INDEX, angles) for s in sites]

    anchors = np.array([_unwrap(atoms, s["ring"])[
        attachment_index(atoms, s, CBIM_ARYL_ATTACHMENT_INDEX)] for s in sites])

    near = [(i, j) for i in range(len(sites)) for j in range(i + 1, len(sites))
            if _mic_min_distance(anchors[i:i + 1], anchors[j:j + 1],
                                 cell) <= PREFILTER]
    print(f"  전치기 통과 자리쌍 {len(near)} / {len(sites)*(len(sites)-1)//2}\n")

    print(f'  {"조각 A":<12}{"조각 B":<12}{"배타 쌍":>8}{"최악 여유":>11}'
          f'{"최악 쌍":>10}')
    print("  " + "-" * 55)
    out = {}
    for a, b in itertools.combinations_with_replacement(LIGANDS, 2):
        edges, worst, worst_ij = [], np.inf, None
        for i, j in near:
            best = -np.inf
            for pi in place[a][i]:
                for pj in place[b][j]:
                    m = _vdw_margin(syms[a], pi, syms[b], pj, cell)
                    if m > best:
                        best = m
                    if best >= 0.0:
                        break
                if best >= 0.0:
                    break
            if best < worst:
                worst, worst_ij = best, (i, j)
            if best < 0.0:
                edges.append((i, j, round(best, 4)))
        tag = "동종" if a == b else "**이종**"
        print(f"  {a:<12}{b:<12}{len(edges):>8}{worst:>11.4f}"
              f"{str(worst_ij):>10}   {tag}")
        out[f"{a}|{b}"] = {"n_exclusive": len(edges),
                           "worst_margin": round(float(worst), 4),
                           "worst_pair": list(worst_ij) if worst_ij else None,
                           "edges": edges}

    tot = sum(v["n_exclusive"] for k, v in out.items()
              if k.split("|")[0] != k.split("|")[1])
    print()
    if tot == 0:
        print("  판정: **이종 배타 쌍 0** — 혼합 조성에 기하 제약이 없습니다.")
        print("        무작위 배치가 구조적으로 문제없음이 확인됩니다.")
    else:
        print(f"  판정: **이종 배타 쌍 {tot}개** — 혼합 셋이 배타 쌍을 포함한 채")
        print("        만들어졌을 수 있습니다. 각 구조에서 그 쌍이 실제로 동시")
        print("        치환됐는지 확인해야 하고, 됐다면 재빌드 대상입니다.")

    dst = os.path.join(HERE, "hetero_conflict_graph.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  [OK] {os.path.basename(dst)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
