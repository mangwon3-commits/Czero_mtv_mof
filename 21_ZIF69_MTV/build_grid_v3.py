"""조성 격자 세분 — saIm 62.5% / 87.5% 구조를 만든다.

[왜 이 스크립트가 따로 있는가]
    `rebuild_structures.py` 는 인자를 받지 않고, 부르는 즉시 structures_v2/ 를
    통째로 다시 씁니다. 2026-08-19 00:20 에 `--help` 를 준 것만으로 전체
    재빌드가 시작됐습니다(고정 시드라 바이트가 같아 피해는 없었습니다).
    그래서 격자 두 종만 만드는 일에 그 스크립트를 쓰지 않습니다.

    이 스크립트는
      (1) argparse 가 있어 --help / --dry-run 이 아무것도 만들지 않고,
      (2) **이미 있는 CIF 를 절대 덮지 않으며**(--force 로만),
      (3) 만든 직후 08-14 결함을 잡았던 검사 두 개를 그대로 돌리고,
      (4) 요청한 치환 자리 수와 실제 치환 자리 수가 **정확히** 같은지 봅니다.
    하나라도 어긋나면 0 이 아닌 값으로 끝납니다 — 다음 단계로 흘려보내지
    않습니다.

[왜 62.5 / 87.5 인가]
    v3 에서 목표대(30~40 kJ/mol)에 든 것은 saIm075(31.42)와 saIm100(34.01)
    둘뿐이고, 바로 아래 saIm050 은 29.51 로 문턱 밑입니다. 25% 간격으로는
    **목표대에 들어가는 지점을 짚을 수 없습니다.**

    그리고 08-19 안정성 관문 v3 에서 saIm075 와 saIm100 이 둘 다 탈락했습니다
    (mslm075 포함 3종). 통과한 마지막 saIm 은 saIm050 입니다. 즉 흡착이 문턱을
    넘는 지점과 구조가 무너지는 지점이 **둘 다 50~75% 사이**에 있습니다.
    62.5% 는 그 두 질문의 답이 동시에 걸려 있는 유일한 조성입니다.

[자리 수는 나누어떨어진다]
    site_map_zif69_bicyclic.json 의 치환 가능 자리는 24개입니다.
    빌더는 n = int(round(frac * 24)) 로 고릅니다.

        0.625 * 24 = 15.0   (정확)
        0.875 * 24 = 21.0   (정확)

    반올림으로 조성이 조용히 바뀌지 않습니다. 그래도 아래에서 확인합니다.

[태그 표기]
    기존 3자리는 백분율입니다(saIm075 = 75%). 격자의 4자리는 **백분율 × 10**
    입니다(saIm0625 = 62.5%, saIm0875 = 87.5%). 자릿수로 구별됩니다.

[출력 — 새 러너를 만들지 않는 이유]
    structures_v2/ 에 **새 파일만** 추가합니다. 기존 30종은 건드리지 않습니다.
    그래야 이어지는 relax_series_v3 → judge_relax_v3 → charge_v3 →
    run_gcmc_v3 를 **한 줄도 새로 쓰지 않고** 그대로 쓸 수 있습니다.
    세 러너 모두 "이미 결과가 있으면 건너뛴다" 라서 새 두 종만 계산합니다.

    검증된 러너를 그대로 쓰는 쪽이, 무인 실행에 새 wrapper 를 태우는 것보다
    안전합니다 — risk_screen_v3 의 대입문이 main() 안에 있어 자식이 v1 을
    읽던 일(08-18)이 정확히 그 위험이었습니다.

    rebuild_index.json 에는 **태그 기준으로 병합**합니다. 기존 행을 지우지
    않습니다.

사용:
    python3 build_grid_v3.py --dry-run     무엇을 만들지만 보여준다
    python3 build_grid_v3.py               만든다
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

# (태그, 라이브러리 키, 표기, 치환율, 기대 자리수)
#
# 앞의 둘이 본 목표입니다. 뒤의 둘은 **대기조**입니다 — 62.5% 가 애매하게
# 나왔을 때(흡착은 넘는데 안정성이 걸리거나 그 반대) 절벽 위치를 좁히는 데
# 씁니다. 만들어 두는 값은 몇 초이고, 사람이 없는 창에서 구조를 만들지 않기로
# 한 이상 **지금 만들어 두지 않으면 그때는 못 만듭니다.**
GRID = [
    ("saIm0625", "saIm_aryl", "-SO3H", 15 / 24.0, 15),   # 62.5%  1순위
    ("saIm0875", "saIm_aryl", "-SO3H", 21 / 24.0, 21),   # 87.5%  2순위
    ("saIm0583", "saIm_aryl", "-SO3H", 14 / 24.0, 14),   # 58.3%  대기
    ("saIm0667", "saIm_aryl", "-SO3H", 16 / 24.0, 16),   # 66.7%  대기
    # [2026-08-24] 절벽 위치 찾기. 랩탑 12작업이 87.5% 를 74.2 pp 로 재
    # "아직 고원 안"이라고 답했고, 100% 는 60.6% 로 꺾여 있습니다. 절벽은
    # 87.5~100% 사이인데 **그 구간에 점이 하나도 없습니다.** 24 자리 중
    # 그 사이의 격자점은 22·23 자리 둘뿐이라 이 둘이 구간을 전부 채웁니다.
    ("saIm0917", "saIm_aryl", "-SO3H", 22 / 24.0, 22),   # 91.7%  절벽
    ("saIm0958", "saIm_aryl", "-SO3H", 23 / 24.0, 23),   # 95.8%  절벽
]


def fix_tags(path):
    t = open(path, encoding="utf-8").read()
    for o, n in (("_space_group_name_H-M_alt", "_symmetry_space_group_name_H-M"),
                 ("_space_group_IT_number", "_symmetry_Int_Tables_number"),
                 ("_space_group_symop_operation_xyz",
                  "_symmetry_equiv_pos_as_xyz")):
        t = t.replace(o, n)
    open(path, "w", encoding="utf-8").write(t)


def main():
    ap = argparse.ArgumentParser(description="saIm 62.5 / 87.5% 격자 구조 생성")
    ap.add_argument("--dry-run", action="store_true",
                    help="만들 대상과 경로만 찍고 끝낸다")
    ap.add_argument("--force", action="store_true",
                    help="이미 있는 CIF 를 덮어쓴다 (기본은 거부)")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    print("  치환 가능 자리 %d개, 출력 %s" % (n_sites, OUT))
    for tag, full, group, frac, want in GRID:
        exact = frac * n_sites
        print("    %-10s %s %6.1f%%  자리 %g (기대 %d)  -> ZIF69_%s.cif"
              % (tag, group, frac * 100, exact, want, tag))
        if abs(exact - want) > 1e-9:
            print("      !! %s x %d 가 정수가 아닙니다. 중단합니다."
                  % (frac, n_sites))
            return 2
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows, bad = [], []
    for tag, full, group, frac, want in GRID:
        out_cif = os.path.join(OUT, "ZIF69_%s.cif" % tag)
        if os.path.exists(out_cif) and not a.force:
            print("\n=== %s — 이미 있습니다. 건너뜁니다(덮으려면 --force) ==="
                  % tag)
            continue
        print("\n=== %s (%s, %.1f%%, 자리 %d/%d) ==="
              % (tag, group, frac * 100, want, n_sites), flush=True)
        # 1 - frac 을 반올림하지 않습니다. 14/24 같은 무한소수에서 반올림하면
        # 빌더의 "조성 합 = 1" 검사(1e-6)에 3e-7 씩 밀려 들어갑니다.
        comp = {"clIm_aryl": 1.0 - frac, full: frac}
        try:
            generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, comp, out_cif, seed=0)
        except Exception as e:                                   # noqa: BLE001
            print("  [빌드 실패] %s: %s: %s" % (tag, type(e).__name__, e),
                  flush=True)
            bad.append(tag)
            continue
        fix_tags(out_cif)

        meta = json.load(open(out_cif.replace(".cif", ".meta.json"),
                              encoding="utf-8"))
        got = meta.get("n_substituted")
        ach = meta.get("achieved_fraction")
        # 조성이 조용히 낮춰지는 것을 여기서 잡는다. 08-14 결함의 사촌이다.
        if got != want:
            print("  [조성 불일치] 기대 %s 자리, 실제 %s 자리 (달성 %s)"
                  % (want, got, ach), flush=True)
            bad.append(tag)
            continue

        # 두 검사는 서로 다른 것을 잡는다 — audit 은 고아/분리 원자,
        # check_substituent_clash 는 치환기끼리의 관통.
        au = audit(out_cif)
        ck = check(out_cif)
        ok = (len(au["orphans"]) + len(au["h_orphans"]) == 0
              and au["detached_atoms"] == 0 and ck["pass"])
        rows.append({"tag": tag, "sub": full, "group": group, "frac": frac,
                     "built": True, "pass": ok,
                     "n_atoms": au["n"], "orphan": len(au["orphans"]),
                     "detached": au["detached_atoms"],
                     "fused_linkers": ck["fused"],
                     "forbidden_contacts": ck["forbidden_contacts"],
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "n_conflict_pairs": meta.get("n_conflict_pairs"),
                     "n_substituted": got,
                     "worst_vdw_margin":
                         meta.get("worst_vdw_margin_after_rotation"),
                     "note": "08-19 조성 격자. 태그 4자리 = 백분율 x 10"})
        verdict = "통과" if ok else "탈락"
        print("  [%s] 치환 %s/%d / 융합 %s / 금지접촉 %s / 고아 %d / 최소거리 %s"
              % (verdict, got, n_sites, ck["fused"], ck["forbidden_contacts"],
                 len(au["orphans"]), meta.get("min_pairwise_distance")),
              flush=True)
        if not ok:
            bad.append(tag)

    # 태그 기준 병합. 기존 행을 지우지 않는다.
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
    print("\n  rebuild_index.json 병합: %d -> %d행" % (len(old), len(merged)))

    if bad:
        print("  !! 실패 %d종: %s" % (len(bad), " ".join(bad)))
        print("     이완 / 전하 / GCMC 로 보내지 마세요.")
        return 1
    print("  다음: relax_series_v3.py (이미 있는 30종은 건너뜁니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
