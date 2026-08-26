"""삼원 MTV — SO3H 14자리 고정 + 소수성 공-링커(-CH3 / -F)를 잔여 자리에.

[무엇을 시험하는가]
    지금까지의 물 축 결과가 하나를 말합니다 — **CO2 를 세게 잡는 자리가 물도
    세게 잡습니다.** 그래서 치환율을 올리면 용량은 오르는데 유지율이 내려가고
    (91.7% 73.4 -> 95.8% 66.0 -> 100% 60.6), 안정성 관문까지 겹쳐 위로도
    막혀 있습니다.

    v4 혼합이 다른 문을 열었습니다: **치환 종류를 바꾸면 물 축이 실제로
    움직입니다**(유지율 75.19 -> 84.77 -> 91.91). 그런데 v4 는 SO3H 를
    **빼고** 다른 것을 넣은 것이라 작업 용량이 25% 떨어졌습니다.

    이 계열은 그 대가를 피하려는 시도입니다. **SO3H 를 14자리로 고정**하고
    (현 승자와 같은 수), 남은 10자리의 Cl 을 소수성 -CH3 로 바꿉니다.
    극성 자리는 그대로 두고 물만 막자는 것입니다.

    문헌 근거: BUT-155 가 열린 금속 자리 **주변에** 부피 큰 소수성기를
    배치해 극성 자리를 보존하면서 물을 막았습니다. Zhao 2024 (메틸화 구리
    MOF) 가 같은 계열입니다.

[왜 -CH3 와 -F 만인가]
    Åhlén 계열이 경고합니다 — 부피 큰 제3 링커는 LCD 를 더 깎아 안정성
    관문을 악화시킵니다. saIm0583 은 이미 LCD 감소 15.71% 로 문턱 20% 에
    가깝고, 바로 위 두 조성(saIm075 20.26%, saIm0625 20.87%)이 그 문턱에서
    탈락했습니다. **소형 치환기만 가능합니다.**

    -CH3 는 Cl 대비 부피가 비슷하고 소수성이 크며, -F 는 더 작고 소수성이
    약합니다. 둘을 같이 넣어 "부피 때문인가 소수성 때문인가" 를 가릅니다.

[조성 축 — 자리 수로 이름 붙입니다]
    기존 4자리 태그(saIm0583 = 58.3%)는 이원용입니다. 삼원은 백분율이 둘이라
    그 규칙으로는 이름이 안 나옵니다. **자리 수를 그대로 씁니다** — 24자리
    중 몇 자리인지가 정확하고 반올림이 없습니다.

        sa14me4   SO3H 14 + CH3  4 + Cl 6    CH3 를 조금
        sa14me7   SO3H 14 + CH3  7 + Cl 3
        sa14me10  SO3H 14 + CH3 10 + Cl 0    잔여 자리 전부
        sa14f7    SO3H 14 + F    7 + Cl 3    me7 의 대조군

    SO3H 14 를 전부 고정했으므로 **CO2 쪽 자리 수는 네 종이 동일**합니다.
    달라지는 것은 소수성기의 양과 종류뿐이라, 물 축의 변화를 그것에
    귀속시킬 수 있습니다.

[원자 수 — 손으로 유도하지 않습니다]
    saIm0583 실측(656원자: Zn 24 C 240 N 120 O 90 Cl 10 S 14 H 158)에서
    출발해 치환 하나당 증분만 더합니다.

        -CH3 한 자리: Cl(1) 빠지고 C(1)+H(3) 들어옴  -> +3원자
        -F   한 자리: Cl(1) 빠지고 F(1) 들어옴        -> +0원자

    빌드 후 `EXPECT_EL` 과 정확히 대조하고 어긋나면 기각합니다. 08-21 에
    시드에 따라 빌더가 원자 수를 조용히 바꾼 전력이 있습니다.

[검사]
    build_grid_v3 / build_ensemble_* 와 같은 셋을 그대로 돕니다 —
    조성 자리 수 정확 일치, audit(고아·분리 원자), 치환기 관통.
    하나라도 어긋나면 그 구조는 파일을 지우고 기각합니다.
    `relax_series_v3.py` 가 structures_v2 를 전량 스캔하므로, 기각한 것을
    남겨 두면 그대로 이완에 태워집니다.

사용:
    python3 build_ternary_me.py --dry-run
    python3 build_ternary_me.py
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, "05_MTV_Ligand_Library")
sys.path.insert(0, LIGLIB)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, "structures_v2")
BASE_CIF = os.path.join(LIGLIB, "ZIF69_base.cif")
SITE_MAP = os.path.join(LIGLIB, "site_map_zif69_bicyclic.json")
INDEX = os.path.join(HERE, "rebuild_index.json")

N_SITES = 24
SA = 14                      # SO3H 자리 수 — 네 종 전부 고정

# saIm0583 실측 656원자에서 출발
_BASE = dict(Zn=24, C=240, N=120, O=90, Cl=10, S=14, H=158)


def expect(co, n):
    """공-링커 co 를 n 자리 넣었을 때 기대 원소 수."""
    e = dict(_BASE)
    e["Cl"] -= n
    if co == "mbIm_aryl":        # -CH3 : C1 H3
        e["C"] += n
        e["H"] += 3 * n
    elif co == "fbIm_aryl":      # -F
        e["F"] = e.get("F", 0) + n
    else:
        raise ValueError(co)
    return {k: v for k, v in e.items() if v}


# (태그, 공-링커 키, 표기, 공-링커 자리 수)
GRID = [
    ("sa14me4",  "mbIm_aryl", "-CH3",  4),
    ("sa14me7",  "mbIm_aryl", "-CH3",  7),
    ("sa14me10", "mbIm_aryl", "-CH3", 10),
    ("sa14f7",   "fbIm_aryl", "-F",    7),
]


def fix_tags(path):
    t = open(path, encoding="utf-8").read()
    for o, n in (("_space_group_name_H-M_alt", "_symmetry_space_group_name_H-M"),
                 ("_space_group_IT_number", "_symmetry_Int_Tables_number"),
                 ("_space_group_symop_operation_xyz",
                  "_symmetry_equiv_pos_as_xyz")):
        t = t.replace(o, n)
    open(path, "w", encoding="utf-8").write(t)


def element_counts(cif):
    from ase.io import read
    at = read(cif)
    el = {}
    for s in at.get_chemical_symbols():
        el[s] = el.get(s, 0) + 1
    return el


def main():
    ap = argparse.ArgumentParser(description="삼원 MTV — SO3H 고정 + 소수성 공-링커")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="이미 있는 CIF 를 덮어쓴다 (기본은 거부)")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    if n_sites != N_SITES:
        print(f"  !! 자리 수가 {n_sites} 입니다 (기대 {N_SITES}). 중단합니다.")
        return 2

    print(f"  치환 자리 {n_sites}개, SO3H {SA}자리 고정, 시드 0")
    for tag, co, grp, n in GRID:
        cl = n_sites - SA - n
        el = expect(co, n)
        if cl < 0:
            print(f"  !! {tag}: 자리가 모자랍니다 ({SA}+{n} > {n_sites})")
            return 2
        print(f"    {tag:<10} SO3H {SA} + {grp:<5} {n:>2} + Cl {cl:>2}"
              f"  -> {sum(el.values())}원자")
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows, bad = [], []
    for tag, co, grp, n in GRID:
        out_cif = os.path.join(OUT, f"ZIF69_{tag}.cif")
        if os.path.exists(out_cif) and not a.force:
            print(f"\n=== {tag} — 이미 있습니다. 건너뜁니다(덮으려면 --force) ===")
            continue
        cl = n_sites - SA - n
        print(f"\n=== {tag} (SO3H {SA} + {grp} {n} + Cl {cl}) ===", flush=True)

        # 자리 수를 분모 24 로 정확히 나눠 줍니다. 반올림하면 빌더의
        # "조성 합 = 1" 검사(1e-6)에 밀려 들어갑니다.
        comp = {"saIm_aryl": SA / float(n_sites),
                co: n / float(n_sites)}
        if cl:
            comp["clIm_aryl"] = cl / float(n_sites)

        try:
            generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, out_cif, seed=0)
        except Exception as e:                                   # noqa: BLE001
            print(f"  [빌드 실패] {type(e).__name__}: {e}", flush=True)
            bad.append(tag)
            continue
        fix_tags(out_cif)

        meta = json.load(open(out_cif.replace(".cif", ".meta.json"),
                              encoding="utf-8"))
        el = element_counts(out_cif)
        want_el = expect(co, n)
        el_ok = el == want_el
        got = meta.get("n_substituted")
        want_sub = SA + n
        au = audit(out_cif)
        ck = check(out_cif)
        ok = (got == want_sub and el_ok
              and len(au["orphans"]) + len(au["h_orphans"]) == 0
              and au["detached_atoms"] == 0 and ck["pass"])

        print(f"  [{'통과' if ok else '탈락'}] 치환 {got}/{want_sub} "
              f"원자 {sum(el.values())} 원소일치 {el_ok} "
              f"융합 {ck['fused']} 금지접촉 {ck['forbidden_contacts']} "
              f"고아 {len(au['orphans'])}", flush=True)
        if not el_ok:
            print(f"     기대 {want_el}", flush=True)
            print(f"     실제 {dict(sorted(el.items()))}", flush=True)
        if not ok:
            # 기각은 흔적을 남기지 않습니다 — relax_series_v3 가 이 폴더를
            # 전량 스캔하므로 남기면 그대로 이완에 태워집니다.
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            bad.append(tag)
            continue

        rows.append({"tag": tag, "sub": "saIm_aryl+" + co, "group": "-SO3H+" + grp,
                     "frac": (SA + n) / float(n_sites), "built": True, "pass": True,
                     "n_atoms": sum(el.values()), "seed": 0,
                     "n_substituted": got,
                     "sa_sites": SA, "co_sites": n, "cl_sites": cl,
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "n_conflict_pairs": meta.get("n_conflict_pairs"),
                     "worst_vdw_margin":
                         meta.get("worst_vdw_margin_after_rotation"),
                     "note": "08-26 삼원 MTV. 태그는 자리 수 표기(sa14me7 = SO3H 14 + CH3 7)"})

    old = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []
    seen = {r["tag"] for r in old}
    merged = list(old) + [r for r in rows if r["tag"] not in seen]
    for r in rows:
        if r["tag"] in seen:
            for i, o in enumerate(merged):
                if o["tag"] == r["tag"]:
                    merged[i] = r
    json.dump(merged, open(INDEX, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\n  rebuild_index.json 병합: {len(old)} -> {len(merged)}행")

    if bad:
        print(f"  !! 실패 {len(bad)}종: {' '.join(bad)}")
        print("     이완 / 전하 / GCMC 로 보내지 마세요.")
        return 1
    print(f"  채택 {len(rows)}종: {' '.join(r['tag'] for r in rows)}")
    print("  다음: relax_series_v3.py (기존 구조는 건너뜁니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
