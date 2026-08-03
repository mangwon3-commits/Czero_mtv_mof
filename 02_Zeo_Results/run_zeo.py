import glob
import os
import subprocess

clean_dir = os.path.expanduser("~/mof_project/01_CIF_Cleaned")
results_dir = os.path.expanduser("~/mof_project/02_Zeo_Results")
os.makedirs(results_dir, exist_ok=True)
csv_path = os.path.join(results_dir, "mof_screening_results.csv")

cif_files = sorted(glob.glob(os.path.join(clean_dir, "*.cif")))
print(f"=== 총 {len(cif_files)}개 MOF 기공 크기(Zeo++) 일괄 계산 시작 ===\n")

results = []

for cif in cif_files:
    name = os.path.splitext(os.path.basename(cif))[0]
    temp_res = os.path.join(results_dir, "temp_calc.res")
    
    if os.path.exists(temp_res):
        os.remove(temp_res)
        
    # Zeo++ 실행
    cmd = f"network -res {temp_res} {cif}"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(temp_res):
        with open(temp_res, "r", encoding="utf-8") as f:
            line = f.read().strip()
        parts = line.split()
        
        # parts 구조: [파일명, LCD, PLD, Dif]
        if len(parts) >= 4:
            lcd, pld, dif = parts[1], parts[2], parts[3]
            results.append((name, lcd, pld, dif))
            print(f"[성공] {name:<32} | LCD: {lcd:<8} | PLD: {pld:<8}")
        else:
            print(f"[데이터 누락] {name}")
        os.remove(temp_res)
    else:
        print(f"[실패] {name} (계산 에러)")

# 윈도우 엑셀 호환성(BOM)을 위해 utf-8-sig로 저장
with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write("MOF_Name,Di_LCD,Df_PLD,Dif\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")

print(f"\n=== 완료! 총 {len(results)}개 구조 계산 및 표 작성 성공 ===")
print(f"📁 생성된 엑셀 파일: {csv_path}")
