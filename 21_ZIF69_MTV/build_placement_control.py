"""배치 규약 대조군 — saIm0583 을 **무작위 배치**로 5실현 만든다.

[사전 등록] 21_ZIF69_MTV/PLACEMENT_CONTROL_20260826.md — 계산 전에 작성됨.

[무엇을 시험하는가]
    `mtv_cif_builder.py:819-825` 가 치환기 2종 이상이면 충돌 회피 배치를
    건너뛰고 무작위로 자리를 고릅니다. 그래서 저장소 구조가 두 계열로
    갈립니다 — 이원(saIm*)은 `conflict_aware=True`, 다원(sa50nb50 등)은
    `False` 입니다.

    v4 의 헤드라인이 그 두 계열을 가로질러 비교하는데, 08-25 에 **배치가
    성질을 크게 흔든다**는 것이 측정됐습니다(건조 로딩 배치 SD 0.0963,
    통계 오차의 5배). 배치 규약 차이가 그 비교에 섞여 있습니다.

    이 대조군은 **조성을 고정하고 배치 알고리즘만 바꿔** 그 효과를 직접
    잽니다. 비교 상대(충돌 회피 6실현)는 이미 측정돼 있으므로 **건조
    로딩만으로 판정**됩니다.

[왜 시드 재시도가 편향이 아닌가]
    무작위 경로는 조성을 다항 추출로 뽑아 정확히 14/24 가 안 나옵니다.
    S 원자 수가 14 인 시드만 채택합니다. 우리가 원하는 것이 **"같은 조성,
    다른 배치"** 이므로 조성으로 조건부화하는 것이 정확히 맞는 표집입니다.
    (조성을 안 맞추면 조성 효과와 배치 효과가 다시 섞입니다.)

[왜 meta 가 아니라 원소 수로 세는가]
    무작위 경로는 `conflict_info` 에 `n_substituted` 를 넣지 않습니다
    (`{"conflict_aware": False}` 뿐). meta 를 믿으면 `None` 이 나오므로
    **CIF 에서 원소를 직접 세어** 확인합니다.

사용:
    python3 build_placement_control.py --dry-run
    python3 build_placement_control.py
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

FRAC = 14 / 24.0
WANT = 14
N_TARGET = 5            # 채택할 실현 수
MAX_SEED = 60           # 다항 추출이라 정확히 14 가 나올 확률이 낮다

# saIm0583 실측과 **동일**해야 한다. 하나라도 다르면 조성이 다른 것이다.
EXPECT_EL = {"Zn": 24, "C": 240, "N": 120, "O": 90, "Cl": 10, "S": 14, "H": 158}


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


def _validated(cif):
    """이미 있는 CIF 가 완성품인지 확인한다. meta 존재·원소 수·검사 3종.

    중단된 실행이 남긴 반쪽 파일을 완성품으로 세지 않기 위한 것입니다.
    """
    meta = cif.replace(".cif", ".meta.json")
    if not os.path.exists(meta):
        return False
    try:
        json.load(open(meta, encoding="utf-8"))
        if element_counts(cif) != EXPECT_EL:
            return False
        from audit_orphans import audit
        from check_substituent_clash import check
        au = audit(cif)
        ck = check(cif)
        return (len(au["orphans"]) + len(au["h_orphans"]) == 0
                and au["detached_atoms"] == 0 and ck["pass"])
    except Exception:                                            # noqa: BLE001
        return False


def main():
    ap = argparse.ArgumentParser(description="배치 규약 대조군 (무작위 배치)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    print(f"  치환 자리 {n_sites}개, 조성 {FRAC*100:.1f}% (자리 {WANT}), "
          f"**무작위 배치**, 목표 {N_TARGET}실현, 시드 1..{MAX_SEED-1}")
    print(f"  비교 상대: saIm0583 충돌 회피 6실현 (이미 측정됨)")
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows, taken, tried = [], [], 0
    for seed in range(1, MAX_SEED):
        if len(taken) >= N_TARGET:
            break
        tag = f"saIm0583r{len(taken) + 1}"
        out_cif = os.path.join(OUT, f"ZIF69_{tag}.cif")
        if os.path.exists(out_cif) and not a.force:
            # [2026-08-26] "있으면 계수" 로 두면 **잘린 파일을 완성품으로
            # 셉니다.** 실제로 그랬습니다 — 이 스크립트의 첫 실행이 2분
            # 타임아웃으로 죽으면서 meta 없는 45 KB 짜리 CIF 를 남겼고,
            # 다음 실행이 그것을 "이미 있음 — 기존 실현으로 계수" 로
            # 받아들였습니다. 검증 없는 건너뛰기가 만든 사고입니다.
            #
            # build_grid_v3.py 와 build_ensemble_*.py 도 같은 형태입니다.
            # 그쪽은 중단된 적이 없어 안 물렸을 뿐입니다.
            if _validated(out_cif):
                print(f"  [{tag}] 이미 있음 — 검증 통과, 기존 실현으로 계수")
                taken.append(tag)
                continue
            print(f"  [{tag}] 이미 있으나 **검증 실패** — 지우고 다시 만듭니다")
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
        tried += 1
        comp = {"clIm_aryl": 1.0 - FRAC, "saIm_aryl": FRAC}
        try:
            generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, out_cif,
                                        seed=seed, conflict_aware=False)
        except Exception as e:                                   # noqa: BLE001
            print(f"  [시드 {seed}] 빌드 예외 {type(e).__name__}: {e} -> 기각")
            continue
        fix_tags(out_cif)

        el = element_counts(out_cif)
        el_ok = el == EXPECT_EL
        if not el_ok:
            # 조성이 안 맞는 시드. 흔적을 남기지 않는다 — relax_series_v3 가
            # structures_v2 를 전량 스캔하므로 남기면 이완에 태워진다.
            print(f"  [시드 {seed}] S={el.get('S')} (기대 14) -> 조성 불일치, 기각")
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            continue

        meta = json.load(open(out_cif.replace(".cif", ".meta.json"),
                              encoding="utf-8"))
        au = audit(out_cif)
        ck = check(out_cif)
        ok = (len(au["orphans"]) + len(au["h_orphans"]) == 0
              and au["detached_atoms"] == 0 and ck["pass"])
        print(f"  [{tag}] 시드 {seed}  S=14 원소일치  융합 {ck['fused']} "
              f"금지접촉 {ck['forbidden_contacts']} 고아 {len(au['orphans'])} "
              f"-> {'채택' if ok else '기각'}", flush=True)
        if not ok:
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            continue

        taken.append(tag)
        rows.append({"tag": tag, "sub": "saIm_aryl", "group": "-SO3H",
                     "frac": FRAC, "built": True, "pass": True,
                     "n_atoms": sum(el.values()), "seed": seed,
                     "n_substituted": WANT,
                     "conflict_aware": False,
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "worst_vdw_margin":
                         meta.get("worst_vdw_margin_after_rotation"),
                     "note": "08-26 배치 규약 대조군. 무작위 배치. "
                             "PLACEMENT_CONTROL_20260826.md 참조"})

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
    print(f"\n  시드 {tried}개 시도, 채택 {len(taken)}실현")
    print(f"  rebuild_index.json 병합: {len(old)} -> {len(merged)}행")

    if len(taken) < N_TARGET:
        print(f"  !! {N_TARGET}실현을 못 채웠습니다 ({len(taken)}). "
              f"MAX_SEED 를 올리거나 중단하세요.")
        return 1
    print(f"  채택: {' '.join(taken)}")
    print("  다음: 이완 -> 판정 -> 전하 -> 건조 GCMC (results_v3pctl.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
