"""v4 혼합 치환 3종 생성 — G0 관문 내장 (V4_DESIGN_BRIEF.md 사전 등록분).

build_grid_v3.py 의 골격을 그대로 따르되 두 가지가 다르다.
  (1) 치환기 2종 혼합 — 빌더가 이 경우 충돌 회피를 건너뛰고 무작위 배치로
      떨어진다(코드 확인됨). 그래서 시드 0..7 을 돌며 검사를 통과하는 첫
      시드를 채택하고, 전부 실패하면 그 조성은 탈락시킨다.
  (2) 원소별 원자 수를 **정확히** 검산한다. 조성이 조용히 섞이거나 낮춰지는
      것을 원소 수준에서 잡는다(08-14 결함의 교훈).
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
BASE_CIF = os.path.join(os.path.dirname(HERE), "05_MTV_Ligand_Library",
                        "ZIF69_base.cif")
SITE_MAP = os.path.join(LIGLIB, "site_map_zif69_bicyclic.json")
OUT = os.path.join(HERE, "structures_v2")
INDEX = os.path.join(HERE, "rebuild_index.json")

# tag, 조성, 기대 원소 수 (Zn C N O S Cl H)
MIX = [
    ("sa50nb50", {"saIm_aryl": 0.5, "nbIm_aryl": 0.5},
     dict(Zn=24, C=240, N=132, O=108, S=12, Cl=0, H=156)),   # 672
    ("sa25nb75", {"saIm_aryl": 0.25, "nbIm_aryl": 0.75},
     dict(Zn=24, C=240, N=138, O=102, S=6, Cl=0, H=150)),    # 660
    ("ms50nb50", {"mslm_aryl": 0.5, "nbIm_aryl": 0.5},
     dict(Zn=24, C=252, N=132, O=96, S=12, Cl=0, H=180)),    # 696
]
MAX_SEED = 8


def elements(cif):
    from ase.io import read
    from collections import Counter
    a = read(cif)
    return dict(Counter(a.get_chemical_symbols())), len(a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check
    from build_grid_v3 import fix_tags

    for tag, comp, want in MIX:
        tot = 600 + sum(want.values()) - 600  # noqa: F841
        print(f"  {tag:<10} {comp}  기대 {sum(want.values())}원자")
    if a.dry_run:
        print("  --dry-run: 아무것도 만들지 않음")
        return 0

    bad, rows = [], []
    for tag, comp, want in MIX:
        out_cif = os.path.join(OUT, f"ZIF69_{tag}.cif")
        if os.path.exists(out_cif) and not a.force:
            print(f"\n=== {tag} — 이미 있음. 건너뜀 ===")
            continue
        print(f"\n=== {tag} — 시드 탐색 (0..{MAX_SEED-1}) ===", flush=True)
        okseed = None
        for seed in range(MAX_SEED):
            tmp = os.path.join(OUT, f"ZIF69_{tag}__s{seed}.cif")
            try:
                generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, tmp,
                                            seed=seed)
            except Exception as e:                              # noqa: BLE001
                print(f"  seed {seed}: 빌드 예외 {type(e).__name__}: {e}")
                continue
            fix_tags(tmp)
            el, n = elements(tmp)
            el_ok = all(el.get(k, 0) == v for k, v in want.items()) \
                and n == sum(want.values())
            au = audit(tmp)
            ck = check(tmp)
            ok = (el_ok and len(au["orphans"]) + len(au["h_orphans"]) == 0
                  and au["detached_atoms"] == 0 and ck["pass"])
            print(f"  seed {seed}: 원자 {n} 원소일치 {el_ok} "
                  f"융합 {ck['fused']} 금지접촉 {ck['forbidden_contacts']} "
                  f"고아 {len(au['orphans'])} -> {'통과' if ok else '탈락'}",
                  flush=True)
            mp = tmp[:-4] + ".meta.json"
            if ok:
                os.replace(tmp, out_cif)
                if os.path.exists(mp):
                    os.replace(mp, out_cif[:-4] + ".meta.json")
                okseed = seed
                break
            for pth in (tmp, mp):
                if os.path.exists(pth):
                    os.remove(pth)
        if okseed is None:
            print(f"  !! {tag}: {MAX_SEED}개 시드 전부 실패 — G0 탈락")
            bad.append(tag)
            continue
        el, n = elements(out_cif)
        rows.append({"tag": tag, "sub": "+".join(sorted(comp)), "group": "v4mix",
                     "frac": comp, "built": True, "pass": True,
                     "n_atoms": n, "elements": el, "seed": okseed,
                     "note": "v4 델타-균형 혼합. V4_DESIGN_BRIEF.md G0 통과"})
        print(f"  [채택] seed {okseed}, {n}원자")

    old = json.load(open(INDEX, encoding="utf-8"))
    seen = {r["tag"] for r in old}
    merged = list(old) + [r for r in rows if r["tag"] not in seen]
    json.dump(merged, open(INDEX, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\n  rebuild_index 병합: {len(old)} -> {len(merged)}행")
    if bad:
        print(f"  !! G0 탈락 {len(bad)}종: {' '.join(bad)} — 다음 단계로 보내지 마세요")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
