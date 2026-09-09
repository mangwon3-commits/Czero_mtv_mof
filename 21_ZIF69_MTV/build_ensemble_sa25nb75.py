"""`sa50nb50` 앙상블 — **군 B(무작위 배치) K_H 배치 산포**를 재기 위한 5실현.

[사전 등록] `ASSIGN_36H_20260826.md` 12절. 배치 대조군 판정(null) 뒤 배정.

[왜 필요한가 — 대조군의 부수 관찰이 −OH 결론을 흔든다]
    대조군 판정은 null 이지만 부수 관찰로 **무작위 팔의 산포가 1.47배**로
    나왔습니다(F 검정 미유의 — 그러나 "같다" 가 아니라 "모른다" 입니다).
    v4 혼합 셋은 **전부 무작위 배치**라 그 배수가 직접 실립니다:

        ms50nb50 -> sa50nb50 (−OH 대조)
          산포 같다고 볼 때   1.65 단위   검출
          군 B 1.40배         1.18 단위   **미검출**

    즉 −OH 대조가 **가정의 방향에 뒤집힙니다.** 군 B 산포를 직접 재야
    닫힙니다. 랩탑이 08-26 19:2x 에 자기 결론을 스스로 내리며 짚었습니다.

[대조군 값을 옮겨 쓸 수 없는 이유 — 구조 상황이 다르다]
        대조군이 잰 상황   24자리 중 14자리를 **한 치환기**로   (빈 자리 10)
        혼합 조성의 상황   24자리 **전부**를 두 치환기로        (빈 자리 0)

    빈 자리가 없으면 "충돌 회피" 라는 개념 자체가 다르게 작동합니다 —
    어느 자리를 비울지가 아니라 어느 치환기를 놓을지만 고릅니다.
    **1.47배를 옮기는 것은 다른 구조 상황으로의 외삽**이라 크기는커녕
    방향도 보장되지 않습니다.

[함정 둘 — `build_ensemble_0583.py` 를 복제하면 전 시드가 기각됩니다]

    ① `build_ensemble_0583.py:111` 이 `meta.get("n_substituted")` 로 판정합니다.
       그런데 **무작위 경로는 그 키를 안 씁니다** — `mtv_cif_builder.py:826`
       이 `conflict_info = {"conflict_aware": False}` 만 넣습니다. `None == 24`
       가 False 라 **모든 시드가 기각**됩니다.
       -> 그래서 이 파일은 **`build_placement_control.py` 를 본**으로 삼아
          `el_ok` 만으로 판정하고 `n_substituted` 는 나중에 손으로 박습니다.

    ② `sa50nb50` 은 **24자리 전부 치환이라 `Cl` 키가 아예 없습니다.**
       `saIm*` 판(`Cl: 10` 또는 `Cl: 12`)을 복제하고 S 만 고치면 Cl 때문에
       또 전량 기각됩니다.

    둘 다 랩탑이 08-26 19:4x 에 미리 잡았고 데스크탑이 실측으로 확인했습니다.

[조성은 이미 통제돼 있습니다 — 확인함]
    다항 추출이라 실현마다 조성이 흔들릴 것 같지만, `build_v4mix.py:80-86`
    이 **원소 수가 목표와 정확히 맞을 때까지 시드를 탐색**합니다. 실제로
    `sa50nb50` `ms50nb50` 이 S=12, `sa25nb75` 가 S=6 으로 전부 정확합니다.
    이 파일도 같은 기각 표집을 써서 **조성 고정, 배열만 다름**을 지킵니다.

사용:
    python3 build_ensemble_sa50nb50.py --dry-run
    python3 build_ensemble_sa50nb50.py
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

COMP = {"saIm_aryl": 0.25, "nbIm_aryl": 0.75}     # build_v4mix 의 sa25nb75 와 동일
WANT = 24                   # 24자리 전부 치환 (SO3H 12 + NO2 12)
N_TARGET = int(os.environ.get("ENS_N_TARGET", 5))   # 09-07: 8 로 늘려 e6~e8 (§G-4 (ㄴ) 대비)
PROD_SEED = 3               # 생산 sa25nb75 가 쓴 시드 (rebuild_index)
MAX_SEED = 80               # 다항 추출이라 정확히 12/12 가 드물다

# 🔴 **이미 채택된 실현의 시드도 제외해야 합니다** (09-07 랩탑, 착수 전 발견).
# `PROD_SEED` 하나만 빼는 것으로는 부족합니다 — 태그가 `e{len(taken)+1}` 로 **자리 순서**에서
# 나오는데, 재실행 때 기존 e1~e5 파일이 앞쪽 시드(0,1,3,4,5)를 소진해 버립니다. 그래서
# `N_TARGET` 을 8 로 올리면 **시드 16 이 e6 으로 다시 뽑히고, 그것은 e1 과 같은 배열**입니다.
# 같은 구조가 두 이름으로 앙상블에 들어가면 **실현 SD 가 가짜로 줄어듭니다** — 이 계산은
# 바로 그 SD 를 재려는 것이므로 치명적입니다. 채택된 시드는 `rebuild_index.json` 에 있습니다.
def _used_seeds():
    try:
        d = json.load(open(INDEX, encoding="utf-8"))
    except Exception:                                            # noqa: BLE001
        return set()
    rows = d if isinstance(d, list) else d.get("rows", d.get("entries", []))
    return {r["seed"] for r in rows
            if isinstance(r, dict) and str(r.get("tag", "")).startswith("sa25nb75e")
            and r.get("seed") is not None}

# charged_v3/sa50nb50_DDEC6.cif 실측 (08-26). **Cl 키가 없습니다.**
EXPECT_EL = {"C": 240, "H": 150, "N": 138, "O": 102, "S": 6, "Zn": 24}   # structures_v2/ZIF69_sa25nb75.cif 실측 (09-09)


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
    """이미 있는 CIF 가 완성품인지 확인한다 (meta 존재·원소 수·검사 3종).

    `build_placement_control.py` 의 같은 이름 함수와 같은 취지입니다 —
    중단된 실행이 남긴 반쪽 파일을 완성품으로 세지 않기 위한 것입니다.
    08-26 에 실제로 그런 사고가 났습니다.
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
    ap = argparse.ArgumentParser(description="sa25nb75 앙상블 (ASSIGN §Q ② 자 확보, 09-09)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    from mtv_cif_builder import generate_mtv_cif_zif69_aryl
    from audit_orphans import audit
    from check_substituent_clash import check

    n_sites = len(json.load(open(SITE_MAP, encoding="utf-8")))
    print(f"  치환 자리 {n_sites}개, 조성 {COMP}, **무작위 배치**(2종이라 강제)")
    print(f"  목표 {N_TARGET}실현, 시드 0..{MAX_SEED-1} 중 {PROD_SEED}(생산) 제외")
    print(f"  기대 원소 {EXPECT_EL}  총 {sum(EXPECT_EL.values())}")
    print("  주의: n_substituted 로 판정하지 않습니다 — 무작위 경로는 그 키를 "
          "안 씁니다(mtv_cif_builder.py:826)")
    if a.dry_run:
        print("  --dry-run 이므로 아무것도 만들지 않았습니다.")
        return 0

    os.makedirs(OUT, exist_ok=True)
    used = _used_seeds()
    print(f"  이미 채택된 시드 {sorted(used)} + 생산 {PROD_SEED} 를 제외합니다 "
          f"(같은 배열이 다른 이름으로 들어가면 실현 SD 가 가짜로 줄어듭니다)")
    rows, taken, tried = [], [], 0
    for seed in range(MAX_SEED):
        if len(taken) >= N_TARGET:
            break
        if seed == PROD_SEED:
            continue                    # 생산 실현과 같은 배열을 다시 만들지 않는다
        tag = f"sa25nb75e{len(taken) + 1}"
        # 기존 실현은 파일 존재로 계수되고 그 시드는 아래 `used` 로 막힙니다.
        # 둘을 같이 걸어야 합니다 — 파일만 보면 시드가 재사용되고, 시드만 보면
        # 기존 실현이 계수되지 않아 태그가 밀립니다.
        if seed in used and not os.path.exists(
                os.path.join(OUT, f"ZIF69_{tag}.cif")):
            continue
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
        try:
            generate_mtv_cif_zif69_aryl(BASE_CIF, SITE_MAP, COMP, out_cif,
                                        seed=seed, conflict_aware=False)
        except Exception as e:                                   # noqa: BLE001
            print(f"  [시드 {seed}] 빌드 예외 {type(e).__name__}: {e} -> 기각")
            continue
        fix_tags(out_cif)

        el = element_counts(out_cif)
        if el != EXPECT_EL:
            # 조성이 안 맞는 시드. 흔적을 남기지 않는다 — relax_series_v3 가
            # structures_v2 를 전량 스캔하므로 남기면 이완에 태워집니다.
            diff = {k: (el.get(k, 0), v) for k, v in EXPECT_EL.items()
                    if el.get(k, 0) != v}
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
        print(f"  [{tag}] 시드 {seed}  S={el.get('S',0)} Cl={el.get('Cl',0)} 원소일치  융합 {ck['fused']} "
              f"금지접촉 {ck['forbidden_contacts']} 고아 {len(au['orphans'])} "
              f"-> {'채택' if ok else '기각'}", flush=True)
        if not ok:
            for p in (out_cif, out_cif.replace(".cif", ".meta.json")):
                os.path.exists(p) and os.remove(p)
            continue

        taken.append(tag)
        rows.append({"tag": tag, "sub": "saIm_aryl+nbIm_aryl", "group": "-SO3H/-NO2",
                     "frac": {"saIm_aryl": 0.25, "nbIm_aryl": 0.75}, "built": True, "pass": True,
                     "n_atoms": sum(el.values()), "seed": seed,
                     # 무작위 경로가 meta 에 안 넣으므로 여기서 박습니다.
                     "n_substituted": WANT,
                     "conflict_aware": False,
                     "min_pairwise_distance": meta.get("min_pairwise_distance"),
                     "worst_vdw_margin":
                         meta.get("worst_vdw_margin_after_rotation"),
                     "note": "08-26 군 B(무작위 배치) K_H 배치 산포용 앙상블. "
                             "ASSIGN_36H_20260826.md 12절 참조"})

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
    print("  다음: 이완 -> 판정 -> 전하 -> **랩탑에 인계** (저압 15작업)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
