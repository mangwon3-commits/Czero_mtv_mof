"""`saIm075` 앙상블 5실현 — 안정성 관문 2단계용 구조 생성.

[왜 2단계가 발동했는가]
    `JUNSEOK_20260827.md` 3절이 **수를 보기 전에** 세 갈래를 등록했고,
    Junseok 1단계 실측이 **`s_LCD` = 3.2326 %p** 로 나왔습니다.

        s_LCD < 0.30      -> 관문이 분해한다. 2단계 없음
        0.30 ~ 1.0        -> 경계 셋 미해결
        **s_LCD >= 1.0    -> 관문이 이 구간을 분해하지 못한다. 2단계 착수**

    `saIm075` 의 문턱 초과 폭이 **0.26 %p** 인데 산포가 그 **12.4배**입니다.

[1단계가 왜 끝이 아닌가 — 빌려온 산포이기 때문입니다]
    3.2326 은 `saIm0583`(LCD 감소 15.71%)에서 쟀습니다. 그것을
    `saIm075`(20.26%)에 적용하는 것은 **빌려오는 것**이고, 08-27 에 하루
    종일 잡은 바로 그 형태입니다. 조성이 다르면 산포도 다를 수 있습니다.
    그래서 2단계는 **`saIm075` 에서 직접** 잽니다.

[배치 규약 — 생산판과 **같게** 맞춥니다]
    생산 `saIm075` 는 치환기 1종이라 `mtv_cif_builder.py:798` 의
    `conflict_aware=True` 경로로 만들어졌습니다(시드 0). 앙상블도 **같은
    경로, 시드 1~5** 로 만듭니다.

    `PLACEMENT_CONTROL_20260826.md` 8절이 46개 구조 전부에서
    `n_conflict_pairs = 0` 임을 보였으므로 두 경로는 **같은 분포**로
    귀착합니다. 그래도 규약을 맞추는 이유는 통계가 아니라 **변수를 하나만
    바꾸기 위해서**입니다 — 조성만 다르고 나머지는 같아야 합니다.

[왜 meta 가 아니라 원소 수로 세는가 — 랩탑이 잡은 함정 둘]
    (가) `build_ensemble_0583.py:111` 은 `meta.get("n_substituted")` 로
         판정하는데 무작위 경로는 그 키를 안 넣어 `None` 이 나옵니다.
    (나) 같은 파일의 `EXPECT_EL` 에 **`Cl` 키가 없습니다.** 24/24 치환을
         가정한 것인데 `saIm075` 는 **18/24** 라 Cl 이 6개 남습니다.

    그래서 `build_placement_control.py` 를 본으로 삼고, 판정은 **원소 수
    일치**로만 합니다.

[EXPECT_EL 은 유도하지 않고 **실측에서 가져왔습니다**]
    모체와 생산 `saIm075` 를 직접 세어 확인했습니다(08-28):

        base(0/24)       C 240  Cl 24  H 144  N 120  O  48  Zn 24
        saIm075(18/24)   C 240  Cl  6  H 162  N 120  O 102  S 18  Zn 24

    치환 1건마다 Cl -1, S +1, O +3, H +1. 18건이면 위와 정확히 맞습니다.
    **유도값과 실측이 일치**하는 것을 확인하고 실측을 씁니다.

사용:
    python3 build_ensemble_075.py --dry-run
    python3 build_ensemble_075.py
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

# relax_series_v3.py:47 이 여기를 전량 스캔합니다. 폴더 이름이 v2 지만
# v3 이완의 입력입니다 — 바꾸지 마십시오.
OUT = os.path.join(HERE, "structures_v2")
BASE_CIF = os.path.join(LIGLIB, "ZIF69_base.cif")
SITE_MAP = os.path.join(LIGLIB, "site_map_zif69_bicyclic.json")
INDEX = os.path.join(HERE, "rebuild_index.json")

FRAC = 18 / 24.0
WANT = 18
N_TARGET = 5
MAX_SEED = 40

# 08-28 실측. 생산 saIm075 와 **한 원소도 달라서는 안 됩니다.**
EXPECT_EL = {"Zn": 24, "C": 240, "N": 120, "O": 102, "Cl": 6, "S": 18, "H": 162}

# Junseok 감시자(stage2_watch.sh:111-115)가 받는 접미사 형태입니다.
# `saIm0750` 처럼 자릿수가 늘어난 것은 **다른 조성으로 보고 배제**하므로
# 접미사는 반드시 `e1`..`e5` 형태여야 합니다.
TAGS = [f"saIm075e{i}" for i in range(1, N_TARGET + 1)]


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
    """이미 있는 CIF 가 완성품인지 확인한다 (build_placement_control 과 동일).

    08-26 에 2분 타임아웃으로 죽은 실행이 meta 없는 45 KB 짜리 CIF 를 남겼고
    다음 실행이 그것을 완성품으로 셌습니다. 검증 없는 건너뛰기가 만든 사고라
    여기에도 같은 관문을 둡니다.
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
    ap = argparse.ArgumentParser(description="saIm075 앙상블 5실현 (관문 2단계)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    print(f"  치환 자리 {n_sites}개, 조성 {FRAC*100:.2f}% (자리 {WANT}), "
          f"**충돌 회피**(생산판과 동일), 목표 {N_TARGET}실현")
    print(f"  기대 원소  {EXPECT_EL}")
    print(f"  출력       {OUT}")
    print(f"  태그       {' '.join(TAGS)}")
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    rows, taken, tried = [], [], 0
    for seed in range(1, MAX_SEED):
        if len(taken) >= N_TARGET:
            break
        tag = TAGS[len(taken)]
        out_cif = os.path.join(OUT, f"ZIF69_{tag}.cif")
        if os.path.exists(out_cif) and not a.force:
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
                                        seed=seed, conflict_aware=True)
        except Exception as e:                                   # noqa: BLE001
            print(f"  [시드 {seed}] 빌드 예외 {type(e).__name__}: {e} -> 기각")
            continue
        fix_tags(out_cif)

        el = element_counts(out_cif)
        if el != EXPECT_EL:
            # 흔적을 남기지 않습니다 — relax_series_v3 가 이 폴더를 전량
            # 스캔하므로 남기면 조성이 틀린 구조가 이완에 태워집니다.
            diff = {k: (el.get(k), EXPECT_EL.get(k))
                    for k in set(el) | set(EXPECT_EL) if el.get(k) != EXPECT_EL.get(k)}
            print(f"  [시드 {seed}] 원소 불일치 {diff} -> 기각")
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            continue

        meta = json.load(open(out_cif.replace(".cif", ".meta.json"),
                              encoding="utf-8"))
        au = audit(out_cif)
        ck = check(out_cif)
        ok = (len(au["orphans"]) + len(au["h_orphans"]) == 0
              and au["detached_atoms"] == 0 and ck["pass"])
        print(f"  [{tag}] 시드 {seed}  S=18 원소일치  융합 {ck['fused']} "
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
                     "conflict_aware": True,
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "worst_vdw_margin":
                         meta.get("worst_vdw_margin_after_rotation"),
                     "note": "08-28 안정성 관문 2단계. saIm075 배치 산포 직접 측정. "
                             "STAGE2_SAIM075_20260828.md 참조"})

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
    print("  다음: relax_series_v3 -> relax_v3/*_relaxed.cif 5개를 "
          "**한 번에** 푸시 (Junseok 감시자가 5개 미만이면 안 걸고 기다립니다)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
