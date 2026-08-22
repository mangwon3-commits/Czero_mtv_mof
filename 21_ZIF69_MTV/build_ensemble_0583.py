"""자리 배치 앙상블 — saIm0583 을 다른 시드 5개로 다시 만든다.

[왜]
    지금까지의 모든 v3 결과는 seed=0 의 단일 실현이다. 같은 14/24 조성에서
    어느 14자리를 고르느냐가 흡착을 얼마나 흔드는지 잰 적이 없다
    (ENSEMBLE_0583_PROTOCOL.md — 판정 기준은 계산 전에 등록돼 있다).

[규약]
    build_grid_v3.py 의 안전장치를 그대로 가져온다:
      argparse(--dry-run/--force), 기존 CIF 불가침, 조성 개수 검증,
      audit + 치환기 관통 검사, rebuild_index 태그 병합.
    여기에 build_v4mix.py 의 원소 정확 일치 검사(G0)를 더한다 — 시드에
    따라 빌더가 원자 수를 조용히 바꾼 전력이 있다(08-21, 656/658/688...).

[태그]
    saIm0583e{seed} — e 뒤 숫자가 빌더 시드다. seed=0(생산)은 만들지 않는다.
    시드 1부터 올려가며 검사 통과분 5개를 채운다.

사용:
    python3 build_ensemble_0583.py --dry-run
    python3 build_ensemble_0583.py
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
N_TARGET = 5           # 채택할 실현 수
MAX_SEED = 13          # 1..12 안에서 5개를 못 채우면 실패로 끝낸다

# 656 = 600 + 4*14. Cl+S = 24 가 자리 보존의 독립 검산이다.
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


def main():
    ap = argparse.ArgumentParser(description="saIm0583 자리 배치 앙상블 생성")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    print(f"  치환 자리 {n_sites}개, 조성 {FRAC*100:.1f}% (자리 {WANT}), "
          f"목표 {N_TARGET}실현, 시드 1..{MAX_SEED-1}")
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows, taken = [], []
    for seed in range(1, MAX_SEED):
        if len(taken) >= N_TARGET:
            break
        tag = f"saIm0583e{seed}"
        out_cif = os.path.join(OUT, f"ZIF69_{tag}.cif")
        if os.path.exists(out_cif) and not a.force:
            print(f"  [{tag}] 이미 있음 — 기존 실현으로 계수")
            taken.append(tag)
            continue
        comp = {"clIm_aryl": 1.0 - FRAC, "saIm_aryl": FRAC}
        try:
            generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, out_cif,
                                        seed=seed)
        except Exception as e:                                   # noqa: BLE001
            print(f"  [{tag}] 빌드 예외 {type(e).__name__}: {e} -> 기각")
            continue
        fix_tags(out_cif)
        meta = json.load(open(out_cif.replace(".cif", ".meta.json"),
                              encoding="utf-8"))
        got = meta.get("n_substituted")
        el = element_counts(out_cif)
        el_ok = el == EXPECT_EL
        au = audit(out_cif)
        ck = check(out_cif)
        ok = (got == WANT and el_ok
              and len(au["orphans"]) + len(au["h_orphans"]) == 0
              and au["detached_atoms"] == 0 and ck["pass"])
        n = sum(el.values())
        print(f"  [{tag}] 자리 {got}/{WANT} 원자 {n} 원소일치 {el_ok} "
              f"융합 {ck['fused']} 금지접촉 {ck['forbidden_contacts']} "
              f"고아 {len(au['orphans'])} -> {'채택' if ok else '기각'}",
              flush=True)
        if not ok:
            # 기각 시드는 흔적을 남기지 않는다 — relax_series_v3 가
            # structures_v2 를 전량 스캔하므로, 남기면 그대로 계산에 태워진다.
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            continue
        taken.append(tag)
        rows.append({"tag": tag, "sub": "saIm_aryl", "group": "-SO3H",
                     "frac": FRAC, "built": True, "pass": True,
                     "n_atoms": n, "seed": seed,
                     "n_substituted": got,
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "n_conflict_pairs": meta.get("n_conflict_pairs"),
                     "note": "08-22 자리 배치 앙상블. e 뒤 숫자 = 빌더 시드. "
                             "ENSEMBLE_0583_PROTOCOL.md 참조"})

    if len(taken) < N_TARGET:
        print(f"  !! 시드 1..{MAX_SEED-1} 에서 {len(taken)}개밖에 못 채움. 중단.")
        return 1

    old = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []
    seen = {r["tag"] for r in old}
    merged = list(old) + [r for r in rows if r["tag"] not in seen]
    json.dump(merged, open(INDEX, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\n  rebuild_index 병합: {len(old)} -> {len(merged)}행")
    print(f"  채택 {N_TARGET}실현: {' '.join(taken)}")
    print("  다음: relax_series_v3.py (기존 37종은 건너뜁니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
