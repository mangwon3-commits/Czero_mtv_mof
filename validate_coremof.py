import os
import glob
import json
import pandas as pd
from CoREMOF.curate import mof_check, run_mofclassifier

WORK_DIR = os.path.expanduser("~/mof_project")
CIF_DIR = os.path.join(WORK_DIR, "03_Generated_MTV_ZIFs")
OUT_DIR = os.path.join(WORK_DIR, "04_CoreMOF_Validation")
os.makedirs(OUT_DIR, exist_ok=True)

print("=== [시작] CoRE-MOF-Tools 구조 검증 (mof_check + MOFClassifier) ===")
print(f"대상 CIF 폴더: {CIF_DIR}")
print("-----------------------------------------------------------------")

cif_files = sorted(glob.glob(os.path.join(CIF_DIR, "*.cif")))

# 1. mof_check: Chen&Manz 결합차수 검사 + MOFChecker 2.0 구조 결함 검사
rows = []
for cif in cif_files:
    name = os.path.splitext(os.path.basename(cif))[0]
    print(f"[검사 중] {name}")
    mof_check(cif, output_folder=OUT_DIR)
    json_path = os.path.join(OUT_DIR, f"{name}_Chen_Manz_mofchecker.json")
    with open(json_path, "r") as f:
        result = json.load(f)
    rows.append({
        "MOF_Name": name,
        "Chen_Manz": ", ".join(result.get("Chen_Manz", ["unknown"])),
        "MOFChecker": ", ".join(result.get("mofchecker", ["unknown"])),
    })

df_struct = pd.DataFrame(rows)
struct_csv = os.path.join(OUT_DIR, "structural_validity_summary.csv")
df_struct.to_csv(struct_csv, index=False, encoding="utf-8-sig")
print(f"\n[안내] 구조 검증 요약 저장 완료: {struct_csv}")
print(df_struct.to_string(index=False))

# 2. MOFClassifier: ML 기반 Computation-Ready MOF 판별
print("\n=== MOFClassifier 실행 중 ===")
mofcls_path = os.path.join(OUT_DIR, "mofclassifier_results.json")
mofcls_result = run_mofclassifier(CIF_DIR, save_path=mofcls_path, model="core")
print(f"[안내] MOFClassifier 결과 저장 완료: {mofcls_path}")
for k, v in mofcls_result.items():
    print(f"  {k}: {v}")

print("\n[완료] CoRE-MOF-Tools 구조 검증 완료.")
