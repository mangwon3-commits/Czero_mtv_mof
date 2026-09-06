"""등록 분모를 **내가 직접 확인**하고, 글롭 함정이 실재하는지 재현한다.

전언을 자료로 쓰지 않는다(09-05 28% 건). 그리고 함정은 **재현해 봐야** 안다.
"""
import json, glob, os
import collections

os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")

REG = {          # RH90_DENOMINATORS_20260906.md §5 등록값
    "base":     (0.5839, "v3_water/water_results.json"),
    "saIm0875": (1.3031, "v3_water_grid/water_results_laptop.json"),
    "saIm0917": (1.3249, "v3_water_grid_cliff/water_results.json"),
    "saIm0958": (1.5205, "v3_water_grid_cliff/water_results.json"),
    "saIm100":  (1.5410, "v3_water/water_results.json"),
    "mslm050":  (1.2438, "v3_water_mslm050/water_results.json"),
    "sa50nb50": (1.1257, "v4_water_mix/water_results.json"),
}

print("=== ① 등록값이 그 파일에 정말 있나 ===")
for name, (val, path) in REG.items():
    found = None
    if os.path.exists(path):
        for r in json.load(open(path, encoding="utf-8")):
            if r.get("name") == name and float(r.get("RH", -1)) == 0.0:
                found = r.get("CO2_molkg")
                break
    ok = found is not None and abs(found - val) < 5e-4
    print(f"  {name:<9} 등록 {val:.4f}  파일값 "
          f"{'%.4f' % found if found is not None else '없음':>8}  "
          f"{'**일치**' if ok else '**어긋남**'}")

print()
print("=== ② 글롭 함정 재현 — 순진하게 찾으면 무엇이 잡히나 ===")
allf = sorted(glob.glob("*water*/water_results*.json"))
for name in ("base", "saIm100"):
    hits = []
    for f in allf:
        try:
            rows = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for r in rows:
            if isinstance(r, dict) and r.get("name") == name \
                    and float(r.get("RH", -1)) == 0.0:
                hits.append((f, r.get("CO2_molkg")))
                break
    print(f"  {name}: 후보 {len(hits)}개 — **정렬 첫 번째 = {hits[0][0]}"
          f" ({hits[0][1]:.4f})**" if hits else f"  {name}: 없음")
    for f, v in hits:
        mark = "  <- **등록 정본**" if f == REG[name][1] else ""
        warn = "  ⚠ **v2 — 쓰면 안 됨**" if "v2_" in f else ""
        print(f"      {v:.4f}  {f}{mark}{warn}")
    reg = REG[name][0]
    if hits and abs(hits[0][1] - reg) > 5e-4:
        d = 100 * (1 - reg / hits[0][1])
        print(f"      -> 순진한 글롭은 **{d:+.1f}%** 큰 분모를 잡는다 "
              f"= 유지율이 그만큼 **작게** 나온다")
