"""§5 옛 물 결과에 `WARN_forcefield` 표기 (WATER_FIX_20260906 §5).

**측정값은 절대 안 건드린다.** 키를 더할 뿐이다.

형태가 둘이라 둘 다 다룬다:
    리스트형 60개  ->  **RH > 0 인 행에만** 키 추가 (RH0 은 물 분자 0 이라 무관)
    dict 형 9개    ->  최상단에 키 추가 (rows 가 있으면 그 안의 RH>0 행에도)

**사이드카**(`<파일>.WARN_forcefield.json`)를 함께 둔다 — 행이 다른 파일로
복사돼도 표기가 따라가도록 행에 찍고, 파일 단위 이력은 사이드카에 둔다
(랩탑 `run_water_v3w.stamp()` 와 같은 방침).

`--apply` 없이 돌리면 **무엇을 바꿀지만 보여 주고 아무것도 안 쓴다.**
"""
import json, glob, os, sys, hashlib, datetime

os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")

MSG = ("수소결합이 없는 물로 계산한 값(Hw→H_, 2026-09-05 발견, 09-06 수정)")
TAG = {
    "WARN_forcefield": MSG,
    "defect": "UFF_MOF force_field_mixing_rules.def 에 Hw/Lw 항이 없어 "
              "RASPA 앞자리 일치로 Hw 가 H_(UFF 수소) LJ 를 물려받음",
    "effect": "이합체 우물 -22.9 -> -10.0 kJ/mol, 최소 위치 2.70 -> 3.60 A "
              "(랩탑 실측). 액체에서 첫 껍질 없음",
    "fixed_md5": "8e8ec933f9013c7e932da04dc256efd3",
    "ref": "WATER_FIX_20260906.md · WATER_FF_DEFECT_20260905.md",
    "scope": "RH > 0 인 행에만 해당. RH0 은 물 분자가 0 이라 무관",
}

PATS = ["v3_water*/water_results*.json", "v3_water*/*.json",
        "humid_wc*/*.json", "v4_water*/*.json", "water_results*.json"]
APPLY = "--apply" in sys.argv


def rh_of(row):
    for k in ("RH", "rh", "RH_pct", "relative_humidity"):
        if k in row:
            try:
                return float(row[k])
            except (TypeError, ValueError):
                return None
    return None


files = sorted({f for p in PATS for f in glob.glob(p)})
n_list = n_dict = n_rows = n_side = n_skip = 0
report = []

for f in files:
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        n_skip += 1
        continue
    if "WARN_forcefield" in open(f, encoding="utf-8").read():
        report.append((f, "이미 표기됨", 0))
        continue

    touched = 0
    if isinstance(d, list):
        for r in d:
            if not isinstance(r, dict):
                continue
            rh = rh_of(r)
            if rh is not None and rh > 0:
                r["WARN_forcefield"] = MSG
                touched += 1
        if touched:
            n_list += 1
    elif isinstance(d, dict):
        d["WARN_forcefield"] = MSG
        touched = 1
        for r in d.get("rows", []) if isinstance(d.get("rows"), list) else []:
            if isinstance(r, dict):
                rh = rh_of(r)
                if rh is not None and rh > 0:
                    r["WARN_forcefield"] = MSG
                    touched += 1
        n_dict += 1

    if not touched:
        report.append((f, "RH>0 행 없음 — 건너뜀", 0))
        continue
    n_rows += touched
    report.append((f, "표기", touched))

    if APPLY:
        json.dump(d, open(f, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        side = f + ".WARN_forcefield.json"
        json.dump({**TAG, "file": f,
                   "rows_tagged": touched,
                   "stamped_at": datetime.datetime.now().isoformat(timespec="seconds"),
                   "file_md5_after": hashlib.md5(
                       open(f, "rb").read()).hexdigest()},
                  open(side, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        n_side += 1

print(f"{'적용' if APPLY else '예행(--apply 없음)'} — 후보 {len(files)}개")
for f, what, k in report[:12]:
    print(f"  {what:<18} {k:>4}행  {f}")
if len(report) > 12:
    print(f"  ... 외 {len(report)-12}개")
print()
print(f"  리스트형 {n_list} · dict 형 {n_dict} · 표기 행 **{n_rows}** · "
      f"사이드카 {n_side} · 파싱실패 {n_skip}")
print(f"  이미 표기됨 {sum(1 for _,w,_ in report if w=='이미 표기됨')} · "
      f"RH>0 없어 건너뜀 {sum(1 for _,w,_ in report if '건너뜀' in w)}")
