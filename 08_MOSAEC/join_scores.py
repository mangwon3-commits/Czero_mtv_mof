"""평가 지표를 한 표로 — MOSAEC 을 빠진 자리에 넣는다.

[왜 이 파일이 필요한가]
    지금까지의 구조 평가가 세 군데에 흩어져 있었고, **MOSAEC 만 빠져 있었습니다.**

        mof_check (Chen&Manz + MOFChecker 2.0)   04_CoreMOF_Validation/
        MOFClassifier (ML computation-ready)      04_CoreMOF_Validation/
        MOSAEC (금속 산화수)                       (없음)

    그리고 그 셋은 **03_Generated_MTV_ZIFs(초기 MTV-ZIF-8)** 를 대상으로 돌았고,
    08-21 장표에 실제로 들어가는 것은 **21_ZIF69_MTV 의 v3 후보**입니다.
    지표와 대상이 어긋나 있었습니다.

    이 스크립트는 v3 후보를 행으로 놓고, 구할 수 있는 지표를 옆에 붙입니다.
    **없는 칸은 비워 둡니다.** 채워진 것처럼 보이게 만들지 않습니다.

[점수를 매기지 않는 이유]
    지표들은 단위도 방향도 다릅니다. 가중합을 만들면 가중치가 결론을 정하게
    되고, 그 가중치를 정당화할 근거가 우리에게 없습니다. 그래서 **관문의
    통과·탈락과 원 수치를 나란히 보이는 표**까지만 만듭니다.
    순위는 사람이 봅니다.

사용:
    python 08_MOSAEC/join_scores.py
    python 08_MOSAEC/join_scores.py --csv scores.csv
"""
import argparse
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
Z = os.path.join(ROOT, "21_ZIF69_MTV")
RESULTS = os.path.join(HERE, "results")


def load(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:                                        # noqa: BLE001
        return default


def mosaec_rows():
    """라벨별 flags.json 에서 태그 -> 판정. 없으면 빈 dict."""
    out = {}
    for p in sorted(glob.glob(os.path.join(RESULTS, "*", "flags.json"))):
        d = load(p, {})
        label = d.get("label", os.path.basename(os.path.dirname(p)))
        for r in d.get("rows", []):
            # 파일 이름이 태그가 되도록 접두·접미를 벗깁니다.
            t = r["id"]
            for a, b in (("ZIF69_", ""), ("_DDEC6", ""), ("_relaxed", "")):
                t = t.replace(a, b)
            out.setdefault(t, {})[label] = r
    return out


def main():
    ap = argparse.ArgumentParser(description="v3 후보 평가 지표 통합표")
    ap.add_argument("--csv", default=os.path.join(RESULTS, "v3_scores.csv"))
    a = ap.parse_args()

    gcmc = load(os.path.join(Z, "results_v3.json"), {"rows": []})["rows"]
    grid = load(os.path.join(Z, "results_v3grid.json"), {"rows": []})["rows"]
    judged = load(os.path.join(Z, "relax_v3_judged.json"), {"rows": []})["rows"]
    risk = load(os.path.join(Z, "risk_results_v3.json"), {"rows": []})["rows"]
    mos = mosaec_rows()

    jd = {r["name"].replace("ZIF69_", ""): r for r in judged}
    rk = {r.get("tag", r.get("name", "")): r for r in risk}

    rows = []
    for r in list(gcmc) + list(grid):
        tag = r["name"]
        m = mos.get(tag, {})
        # 우선순위: 실제 계산 입력(charged) -> 이완본 -> 빌더 출력
        mm = m.get("v3_charged") or m.get("v3_relaxed") or m.get("v3_built")
        rows.append({
            "tag": tag,
            "Qst": r.get("Qst_CO2"),
            "Qst_err": r.get("Qst_CO2_err"),
            "loading_015bar": r.get("loading_015bar"),
            "PLD": r.get("PLD"), "LCD": r.get("LCD"), "AV": r.get("AV"),
            "relax_pass": jd.get(tag, {}).get("pass"),
            "stability_pass": rk.get(tag, {}).get("pass"),
            "mosaec_source": ("v3_charged" if "v3_charged" in m else
                              "v3_relaxed" if "v3_relaxed" in m else
                              "v3_built" if "v3_built" in m else ""),
            "mosaec_hard": mm.get("hard") if mm else None,
            "mosaec_soft": mm.get("soft") if mm else None,
            "mosaec_state": mm.get("state") if mm else "",
        })

    rows.sort(key=lambda x: -(x["Qst"] or 0))
    cols = list(rows[0].keys()) if rows else []
    os.makedirs(RESULTS, exist_ok=True)
    with open(a.csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    def cell(v):
        if v is None or v == "":
            return "—"
        if v is True:
            return "Y"
        if v is False:
            return "n"
        return f"{v:.2f}" if isinstance(v, float) else str(v)

    print(f"{'태그':<10} {'Qst':>7} {'로딩':>7} {'PLD':>6} "
          f"{'이완':>5} {'안정성':>6} {'MOSAEC 굳은':>11} {'확률':>5} {'출처':<11}")
    print("-" * 82)
    for r in rows:
        print(f"{r['tag']:<10} {cell(r['Qst']):>7} "
              f"{cell(r['loading_015bar']):>7} {cell(r['PLD']):>6} "
              f"{cell(r['relax_pass']):>5} {cell(r['stability_pass']):>6} "
              f"{cell(r['mosaec_hard']):>11} {cell(r['mosaec_soft']):>5} "
              f"{r['mosaec_source']:<11}")

    n_m = sum(1 for r in rows if r["mosaec_state"])
    print(f"\n{len(rows)}종 중 MOSAEC 판정 {n_m}종.")
    if n_m == 0:
        print("MOSAEC 칸이 비어 있습니다 — CSD Python API 라이선스가 필요합니다.")
        print("  python 08_MOSAEC/preflight.py")
    print(f"[OK] {a.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
