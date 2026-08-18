"""MOSAEC 일괄 실행 — 금속 산화수 자동 오류 검사.

MOSAEC (Metal Oxidation State Automated Error Checker)
    White, Gibaldi, Burner, Mayo, Woo, JACS 2025, 147, 17579-17583
    https://doi.org/10.1021/jacs.5c04914 | https://github.com/uowoolab/MOSAEC

[이 검사가 담당하는 것]
    `validate_coremof.py` 가 이미 두 가지를 봅니다 — Chen&Manz 결합차수와
    MOFChecker 2.0(원자 겹침·배위수), 그리고 MOFClassifier(ML 판별).
    MOSAEC 은 그 셋이 못 잡는 것을 봅니다: **화학적으로 불가능한 산화수 조합**.
    우리 구조는 스크립트가 치환기를 갈아 끼워 만든 것이므로, 금속 자리의
    화학이 성립하는지는 별도로 확인해야 합니다.

[여덟 개 깃발]
    impossible / unknown / zero_valence / noint_flag  <- 굳은 실패
    low_prob_1 / low_prob_2 / low_prob_3 / low_prob_multi  <- 확률적 경고

    앞의 넷은 "그런 산화수는 없다" 류이고, 뒤의 넷은 "가능하지만 드물다"
    입니다. **이 구분은 우리가 읽는 방식이고 MOSAEC 이 정한 합격선이 아닙니다.**
    논문은 깃발을 그대로 보고하며, 무엇을 탈락으로 볼지는 쓰는 쪽이 정합니다.
    그래서 아래 표는 여덟 개를 전부 남기고, 요약에만 둘로 나눠 적습니다.

[상류 `CoREMOF.mosaec.run()` 의 함정 — 두 가지]
    (1) `check()` 는 금속이 없거나 읽기에 실패하면 **빈 dict** 를 돌려주고,
        `worker()` 가 그것을 문자열 "unknown" 으로 채웁니다. 그러면 요약 루프의
        `for metal in data[col]` 이 문자열을 글자 단위로 돌다가
        `data[col][metal]` 에서 TypeError 로 죽습니다. **CIF 한 개 때문에
        폴더 전체 요약이 날아갑니다.**
        -> 금속이 있는 CIF 만 골라 staging 폴더에 넣고 돌립니다.

    (2) 그래도 죽을 수 있으므로, 요약은 상류 반환값을 믿지 않고 **per-CIF
        JSON 에서 우리가 다시 만듭니다.** 그 JSON 은 요약 루프보다 먼저
        기록되므로, 요약이 터져도 결과는 남아 있습니다.

[평가판 시계]
    CSD Python API 는 30일 평가판입니다. 활성화되면 **대상 전체를 한 번에**
    돌리도록 목록을 우선순위대로 미리 모아 두었습니다. v3 후보가 맨 위입니다.

사용:
    conda activate coremof_tools
    python 08_MOSAEC/run_mosaec.py                  우선순위 전체
    python 08_MOSAEC/run_mosaec.py --only v3_charged
    python 08_MOSAEC/run_mosaec.py --list
    python 08_MOSAEC/run_mosaec.py --dry-run        대상만 세고 끝낸다
"""
import argparse
import glob
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, "results")

HARD = ["impossible", "unknown", "zero_valence", "noint_flag"]
SOFT = ["low_prob_1", "low_prob_2", "low_prob_3", "low_prob_multi"]
FLAGS = HARD + SOFT

# 금속으로 볼 원소. MOSAEC 은 금속 자리가 없으면 아무것도 판정하지 않습니다.
METALS = set(
    "Li Be Na Mg Al K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Rb Sr Y Zr Nb Mo Tc "
    "Ru Rh Pd Ag Cd In Sn Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu "
    "Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Th U".split()
)

# 검사 대상 — **우선순위 순서**. 위가 08-21 장표에 실제로 들어가는 구조입니다.
TARGETS = [
    ("v3_charged",     "21_ZIF69_MTV/charged_v3",
     "v3 최종 계산 입력 (이완 + PACMAN DDEC6). GCMC 가 실제로 읽은 파일."),
    ("v3_relaxed",     "21_ZIF69_MTV/relax_v3",
     "GFN-FF 셀 고정 이완 직후. 전하 부여 전."),
    ("v3_built",       "21_ZIF69_MTV/structures_v2",
     "빌더 출력(이완 전). 이완이 판정을 바꾸는지 보는 대조군."),
    ("v3_parent",      "21_ZIF69_MTV/relax_fixcell",
     "이완된 무치환 모체. 기준선."),
    ("aryl_zif69",     "21_ZIF69_MTV/structures",
     "v1 구조. 08-14 에 결함으로 폐기된 판본 — 대조로만."),
    ("generated_zif8", "03_Generated_MTV_ZIFs",
     "초기 MTV-ZIF-8 생성물."),
    ("bracketed",      "07_Bracketed_MTV",
     "괄호 조성 쌍."),
    ("ligand_library", "05_MTV_Ligand_Library",
     "모체·라이브러리 원본 (전부 금속 포함 구조)."),
    ("zif8_sources",   "06_ZIF8_Sources",
     "ZIF-8 실험 구조 출처."),
    ("source_cifs",    "01_CIF_Cleaned",
     "정리된 원본 CIF."),
]


def cif_symbols(path):
    """CIF 의 원자 자리 원소 기호 집합. **ASE 로 읽지 않습니다** — 대칭 전개까지
    하느라 600원자 구조 하나에 1초씩 걸려서, 160개를 세는 데만 몇 분이 갑니다.
    여기서 필요한 것은 '금속이 하나라도 있나' 뿐이므로 텍스트로 셉니다."""
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except Exception:                                        # noqa: BLE001
        return set()
    syms, i, n = set(), 0, len(lines)
    while i < n:
        if lines[i].strip() != "loop_":
            i += 1
            continue
        i += 1
        hdr = []
        while i < n and lines[i].strip().startswith("_"):
            hdr.append(lines[i].strip())
            i += 1
        if not any(h.startswith("_atom_site_") for h in hdr):
            continue
        col = next((k for k, h in enumerate(hdr)
                    if h == "_atom_site_type_symbol"), None)
        if col is None:
            col = next((k for k, h in enumerate(hdr)
                        if h == "_atom_site_label"), None)
        if col is None:
            continue
        # CSD 가 내려주는 CIF 는 머리글과 데이터 사이에 **빈 줄과 주석**을
        # 넣습니다. 빈 줄에서 바로 끊으면 데이터를 한 줄도 못 읽고, 금속이
        # 있는 구조가 '금속 없음' 으로 분류됩니다(01_CIF_Cleaned 의 Co-MOF
        # 네 개가 실제로 그랬습니다).
        while i < n and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
            i += 1
        while i < n:
            s = lines[i].strip()
            if not s or s.startswith("_") or s.startswith("loop_") \
                    or s.startswith("#") or s.startswith("data_"):
                break
            f = s.split()
            if len(f) > col:
                # 라벨이면 숫자를 떼어 냅니다 (Zn1 -> Zn). 두 글자가 원소면
                # 두 글자로, 아니면 한 글자로 읽습니다 — H1A 의 "Ha" 를
                # 원소로 착각하지 않기 위해서입니다.
                t = "".join(c for c in f[col] if c.isalpha())
                if t:
                    two = t[:2].capitalize()
                    syms.add(two if two in METALS else t[:1].upper())
            i += 1
    return syms


def has_metal(path):
    """CIF 에 금속 자리가 있는가. 없으면 MOSAEC 이 빈 결과를 돌려주고,
    상류 요약 루프가 그것 때문에 폴더 전체에서 죽습니다."""
    return bool(cif_symbols(path) & METALS)


def stage(folder, out):
    """금속이 있는 CIF 만 staging 폴더에 모은다. 원본은 건드리지 않는다."""
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "*.cif")):
        os.remove(f)
    kept, skipped = [], []
    for cif in sorted(glob.glob(os.path.join(folder, "*.cif"))):
        (kept if has_metal(cif) else skipped).append(cif)
    for cif in kept:
        shutil.copyfile(cif, os.path.join(out, os.path.basename(cif)))
    return kept, skipped


def collect(save_path):
    """per-CIF JSON 에서 요약을 우리가 다시 만든다. 상류 반환값을 믿지 않는다."""
    rows = []
    for p in sorted(glob.glob(os.path.join(save_path, "*.json"))):
        if os.path.basename(p) in ("flags.json",):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                    # noqa: BLE001
            continue
        if "name" not in d:
            continue
        row = {"id": d["name"]}
        state = "ok"
        for col in FLAGS:
            v = d.get(col, "unknown")
            if isinstance(v, dict):
                # 금속 자리별 판정. GOOD 이 아닌 것이 하나라도 있으면 깃발.
                row[col] = any(x != "GOOD" for x in v.values())
            else:
                row[col] = None
                state = "error" if v == "error" else "no_verdict"
        row["state"] = state
        row["hard"] = any(row[c] for c in HARD if row[c] is not None)
        row["soft"] = any(row[c] for c in SOFT if row[c] is not None)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser(description="MOSAEC 일괄 실행")
    ap.add_argument("--only", nargs="*", default=None, help="라벨 몇 개만")
    ap.add_argument("--list", action="store_true", help="대상 목록만 보여준다")
    ap.add_argument("--dry-run", action="store_true",
                    help="CIF 수만 세고 MOSAEC 은 부르지 않는다")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()

    targets = [t for t in TARGETS if not a.only or t[0] in a.only]
    if a.only and not targets:
        print(f"  --only {a.only} 에 맞는 라벨이 없습니다.")
        print("  있는 것:", " ".join(t[0] for t in TARGETS))
        return 1

    if a.list or a.dry_run:
        print(f"{'라벨':<16} {'CIF':>5} {'금속없음':>8}  폴더")
        total = 0
        for label, rel, _ in targets:
            folder = os.path.join(ROOT, rel)
            cifs = sorted(glob.glob(os.path.join(folder, "*.cif")))
            nom = 0 if a.list else sum(1 for c in cifs if not has_metal(c))
            total += len(cifs)
            print(f"{label:<16} {len(cifs):>5} {nom if not a.list else '-':>8}  {rel}")
        print(f"\n합계 {total} CIF")
        if a.dry_run:
            print("  --dry-run 이므로 MOSAEC 을 부르지 않았습니다.")
        return 0

    try:
        from CoREMOF.curate import run_MOSAEC
        import CoREMOF.mosaec                                 # noqa: F401
    except Exception as e:                                    # noqa: BLE001
        print(f"MOSAEC 백엔드를 쓸 수 없습니다: {type(e).__name__}: {e}")
        print("먼저 실행: python", os.path.join(HERE, "preflight.py"))
        return 1

    os.makedirs(RESULTS, exist_ok=True)
    summary = {}
    for label, rel, why in targets:
        folder = os.path.join(ROOT, rel)
        if not os.path.isdir(folder):
            print(f"[건너뜀] {label}: 폴더 없음 ({rel})")
            continue
        out = os.path.join(RESULTS, label)
        stg = os.path.join(out, "_in")
        kept, skipped = stage(folder, stg)
        if not kept:
            print(f"[건너뜀] {label}: 금속을 가진 CIF 가 없습니다")
            continue
        print(f"[실행] {label:<16} CIF {len(kept)}개"
              + (f" (금속 없어 제외 {len(skipped)}개)" if skipped else ""))
        err = None
        try:
            run_MOSAEC(stg, save_path=out, max_workers=a.workers)
        except Exception as e:                                # noqa: BLE001
            # 상류 요약 루프가 죽어도 per-CIF JSON 은 이미 쓰여 있습니다.
            err = f"{type(e).__name__}: {e}"
            print(f"  [상류 요약 실패] {err}")
            print("  per-CIF JSON 에서 직접 요약합니다.")

        rows = collect(out)
        hard = [r["id"] for r in rows if r["hard"]]
        soft = [r["id"] for r in rows if r["soft"] and not r["hard"]]
        odd = [r["id"] for r in rows if r["state"] != "ok"]
        print(f"  판정 {len(rows)}종 — 굳은 깃발 {len(hard)} / "
              f"확률 경고만 {len(soft)} / 판정불가 {len(odd)}")
        if hard:
            print(f"  !! {' '.join(hard[:10])}{' ...' if len(hard) > 10 else ''}")

        with open(os.path.join(out, "flags.json"), "w", encoding="utf-8") as f:
            json.dump({"label": label, "folder": rel, "why": why,
                       "n_cifs": len(kept), "n_skipped_no_metal": len(skipped),
                       "upstream_error": err, "rows": rows},
                      f, indent=1, ensure_ascii=False)
        summary[label] = {"folder": rel, "n": len(rows), "hard": hard,
                          "soft_only": soft, "no_verdict": odd,
                          "upstream_error": err}
        shutil.rmtree(stg, ignore_errors=True)

    path = os.path.join(RESULTS, "mosaec_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[OK] 요약 저장: {path}")
    print("다음: python 08_MOSAEC/join_scores.py  (mof_check / MOFClassifier 와 합침)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
