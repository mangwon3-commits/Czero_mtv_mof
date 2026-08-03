import glob
import math
import os
import re
import subprocess

# 1. 경로 설정
clean_dir = os.path.expanduser("~/mof_project/01_CIF_Cleaned")
raspa_dir = os.path.expanduser("~/mof_project/03_RASPA_CO2")
os.makedirs(raspa_dir, exist_ok=True)

# 2. TOP 4 타깃 파일명 리스트
target_names = [
    "ZIF-69-crystal",
    "Co-MOF-9_1_a_sq_CCDC2",
    "Co-MOF-10_CUK-1Co_300mpa",
    "ZIF-8",
    "ZIF_8",  # 파일명 표기차이 대비
]

print("=== [Step 2] TOP 4 황금 후보군 RASPA CO2 흡착 시뮬레이션 시작 ===\n")
print(f"🌡️  실험 조건: 온도 298.0 K (상온) | 압력 1.0 bar (100,000 Pa)")
print(f"🧪  타깃 가스: CO2 (TraPPE 역장 적용)\n" + "-" * 60)

# CIF 검색
all_cifs = glob.glob(os.path.join(clean_dir, "*.cif"))
target_cifs = [
    c
    for c in all_cifs
    if os.path.splitext(os.path.basename(c))[0] in target_names
]


# 3. 단위 격자(Unit Cell) 자동 계산 함수 (CutOff 12.0 Å 에러 원천 차단)
def get_unit_cells(cif_path, cutoff=12.0):
    min_box = cutoff * 2.0  # 최소 24.0 Å 필요
    a, b, c = 10.0, 10.0, 10.0
    with open(cif_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "_cell_length_a" in line and not line.strip().startswith("#"):
                a = float(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
            elif "_cell_length_b" in line and not line.strip().startswith("#"):
                b = float(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
            elif "_cell_length_c" in line and not line.strip().startswith("#"):
                c = float(re.findall(r"[-+]?\d*\.\d+|\d+", line)[0])
    return (
        max(1, math.ceil(min_box / a)),
        max(1, math.ceil(min_box / b)),
        max(1, math.ceil(min_box / c)),
    )


# 4. 시뮬레이션 설정 및 실행
results = []

for cif_path in sorted(target_cifs):
    mof_name = os.path.splitext(os.path.basename(cif_path))[0]
    work_dir = os.path.join(raspa_dir, mof_name)
    os.makedirs(work_dir, exist_ok=True)

    # CIF 복사
    with open(cif_path, "r", encoding="utf-8") as rf, open(
        os.path.join(work_dir, f"{mof_name}.cif"), "w", encoding="utf-8"
    ) as wf:
        wf.write(rf.read())

    # 단위 격자 계산
    na, nb, nc = get_unit_cells(cif_path)
    print(f"🚀 [{mof_name:<25}] 격자 확장: {na}x{nb}x{nc} | GCMC 계산 진행 중...", end="", flush=True)

    # simulation.input 작성 (초기화 2000회, 본계산 5000회 고속 스크리닝)
    sim_input = f"""SimulationType                MonteCarlo
NumberOfCycles                5000
NumberOfInitializationCycles  2000
PrintEvery                    1000
RestartFile                   no

Forcefield                    GenericMOFs
CutOff                        12.0
UseChargesFromCIFFile         no

Framework 0
FrameworkName                 {mof_name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           298.0
ExternalPressure              100000.0

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            TranslationProbability    1.0
            RotationProbability       1.0
            ReinsertionProbability    1.0
            SwapProbability           1.0
            CreateNumberOfMolecules   0
"""
    with open(os.path.join(work_dir, "simulation.input"), "w") as f:
        f.write(sim_input)

    # RASPA 실행
    try:
        subprocess.run(
            ["simulate"],
            cwd=work_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"\n    실행 실패 (RASPA 설치 확인 필요)")
        continue

    # 결과 파일에서 CO2 흡착량(mol/kg) 및 (cm^3/g) 파싱
    output_dir = os.path.join(work_dir, "Output", "System_0")
    uptake_mol = "N/A"
    uptake_cm3 = "N/A"

    if os.path.exists(output_dir):
        out_files = glob.glob(os.path.join(output_dir, "*.data"))
        if out_files:
            latest_out = max(out_files, key=os.path.getctime)
            with open(
                latest_out, "r", encoding="utf-8", errors="ignore"
            ) as out_f:
                for line in out_f:
                    if "average loading absolute [mol/kg framework]" in line:
                        uptake_mol = line.split()[5]
                    elif (
                        "average loading absolute [cm^3 (STP)/gr framework]"
                        in line
                    ):
                        uptake_cm3 = line.split()[6]

    print(f"\r [{mof_name:<25}] CO2 흡착량: {uptake_mol:<7} mol/kg  ({uptake_cm3} cm³/g)")
    results.append((mof_name, uptake_mol, uptake_cm3))

# 5. 최종 CSV 요약표 생성
csv_path = os.path.join(raspa_dir, "top4_co2_uptake_results.csv")
with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write("MOF_Name,CO2_Uptake_mol_per_kg,CO2_Uptake_cm3_per_g\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]}\n")

print("-" * 60)
print(f" 2단계 GCMC 시뮬레이션 완료 - 최종 요약표 생성: {csv_path}")
