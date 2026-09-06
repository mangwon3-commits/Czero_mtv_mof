"""건너뛴 파일이 정말 물 0 인가 — **이름이 아니라 값으로** 확인한다.

앞선 점검은 물 관련 **키 이름**을 보고 43개를 의심했는데, 실제 값은 RH=0 ·
H2O=0 이었다. 이름 검사가 너무 성겼다. 값으로 다시 본다.
"""
import json, glob, os

os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
PATS = ["v3_water*/water_results*.json", "v3_water*/*.json",
        "humid_wc*/*.json", "v4_water*/*.json", "water_results*.json"]
files = sorted({f for p in PATS for f in glob.glob(p)})


def num(r, *keys):
    for k in keys:
        for kk in (k, k.upper(), k.lower()):
            if kk in r:
                try:
                    return float(r[kk])
                except (TypeError, ValueError):
                    pass
    return None


bad = []      # RH=0 이라 건너뛰는데 물이 실제로 들어 있는 것
ok0 = 0       # RH=0 이고 물도 0 — 건너뛰어 맞음
tag = 0       # 표기 대상
for f in files:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if "WARN_forcefield" in open(f, encoding="utf-8").read():
        continue
    rows = d if isinstance(d, list) else (
        d.get("rows") if isinstance(d, dict) and isinstance(d.get("rows"), list) else [])
    if not rows:
        continue
    for r in rows:
        if not isinstance(r, dict):
            continue
        rh = num(r, "RH", "rh_pct", "relative_humidity")
        h2o = num(r, "H2O_molkg", "h2o", "water_molkg")
        if rh is None:
            continue
        if rh > 0:
            tag += 1
        elif h2o is not None and h2o > 0:
            bad.append((f, r.get("name"), rh, h2o))     # 모순: RH0 인데 물이 있다
        else:
            ok0 += 1

print(f"표기 대상 행 (RH>0)          **{tag}**")
print(f"건조 행 (RH=0 이고 물도 0)   **{ok0}**  -> 건너뛰어 맞음")
print(f"⚠ 모순 행 (RH=0 인데 물>0)   **{len(bad)}**")
for b in bad[:10]:
    print(f"    {b}")
print()
print("  -> 모순이 0 이면 건너뛴 것이 전부 진짜 건조 실행이고,")
print("     결함 힘장은 그 값에 영향이 없다(물 분자가 계에 없음).")
