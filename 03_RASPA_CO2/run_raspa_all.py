import glob
import math
import os
import re
import shutil
import subprocess

clean_dir = os.path.expanduser("~/mof_project/01_CIF_Cleaned")
raspa_dir = os.path.expanduser("~/mof_project/03_RASPA_CO2")
os.makedirs(raspa_dir, exist_ok=True)

all_cifs = sorted(glob.glob(os.path.join(clean_dir, "*.cif")))

print(f"=== 총 {len(all_cifs)}개 구조 대상 RASPA CO2 흡착 시뮬레이션 ===")
print("실험 조건: 온도 298.0 K | 압력 1.0 bar (100,000 Pa)")
print("-----------------------------------------------------------------")


def sanitize_cif_for_raspa(input_path, output_path):
    cell_lines = []
    atom_lines = []
    in_atom_loop = False
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for line in lines:
        l_strip = line.strip()
        if l_strip.startswith("_cell_length_") or l_strip.startswith(
            "_cell_angle_"
        ):
            cell_lines.append(line)
        elif l_strip.startswith("_atom_site_"):
            if not in_atom_loop:
                in_atom_loop = True
                atom_lines.append("loop_\n")
            atom_lines.append(line)
        elif in_atom_loop:
            if (
                l_strip.startswith("_")
                and not l_strip.startswith("_atom_site_")
            ) or (
                l_strip.startswith("loop_")
                and not l_strip.startswith("_atom_site_")
            ):
                in_atom_loop = False
            elif l_strip != "" and not l_strip.startswith("#"):
                atom_lines.append(line)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("data_RASPA_clean\n")
        for cl in cell_lines:
            f.write(cl)
        f.write("_symmetry_space_group_name_Hall 'P 1'\n")
        f.write("_symmetry_space_group_name_H-M 'P 1'\n")
        f.write("_symmetry_Int_Tables_number 1\n\n")
        for al in atom_lines:
            f.write(al)


def get_unit_cells(cif_path, cutoff=12.0):
    min_box = cutoff * 2.0
    a, b, c = 10.0, 10.0, 10.0
    with open(cif_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "_cell_length_a" in line and not line.strip().startswith("#"):
                vals = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if vals:
                    a = float(vals[0])
            elif "_cell_length_b" in line and not line.strip().startswith("#"):
                vals = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if vals:
                    b = float(vals[0])
            elif "_cell_length_c" in line and not line.strip().startswith("#"):
                vals = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if vals:
                    c = float(vals[0])
    return (
        max(1, math.ceil(min_box / a)),
        max(1, math.ceil(min_box / b)),
        max(1, math.ceil(min_box / c)),
    )


def parse_output_file(filepath):
    uptake_mol = "N/A"
    uptake_cm3 = "N/A"
    if not os.path.exists(filepath):
        return uptake_mol, uptake_cm3
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_lower = line.lower()
            if "average loading absolute [mol/kg framework]" in line_lower:
                parts = line.split()
                if len(parts) >= 6:
                    uptake_mol = parts[5]
            elif (
                "average loading absolute [cm^3 (stp)/gr framework]"
                in line_lower
            ):
                parts = line.split()
                if len(parts) >= 7:
                    uptake_cm3 = parts[6]
    return uptake_mol, uptake_cm3


results = []

for idx, cif_path in enumerate(all_cifs, 1):
    mof_name = os.path.splitext(os.path.basename(cif_path))[0]
    work_dir = os.path.join(raspa_dir, mof_name)
    os.makedirs(work_dir, exist_ok=True)

    output_dir = os.path.join(work_dir, "Output", "System_0")
    data_files = (
        glob.glob(os.path.join(output_dir, "*.data"))
        if os.path.exists(output_dir)
        else []
    )

    # 1. 기존 데이터 파일 유효성 검증
    valid_file = None
    for df in data_files:
        mol, cm3 = parse_output_file(df)
        if mol != "N/A" and cm3 != "N/A":
            valid_file = df
            break

    # 2. 유효한 데이터가 없으면 불완전 폴더 삭제 후 시뮬레이션 실행
    if not valid_file:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        clean_cif_path = os.path.join(work_dir, f"{mof_name}.cif")
        sanitize_cif_for_raspa(cif_path, clean_cif_path)
        na, nb, nc = get_unit_cells(clean_cif_path)

        print(
            f"[{idx:02d}/{len(all_cifs):02d}] {mof_name:<28} | 계산 실행 중...",
            end="",
            flush=True,
        )

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

        try:
            subprocess.run(
                ["simulate"],
                cwd=work_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            print("\r  [실패] 시스템 실행 오류                           ")
            continue

        data_files = (
            glob.glob(os.path.join(output_dir, "*.data"))
            if os.path.exists(output_dir)
            else []
        )
        for df in data_files:
            mol, cm3 = parse_output_file(df)
            if mol != "N/A" and cm3 != "N/A":
                valid_file = df
                break

    uptake_mol, uptake_cm3 = (
        parse_output_file(valid_file) if valid_file else ("N/A", "N/A")
    )

    print(
        f"\r[{idx:02d}/{len(all_cifs):02d}] {mof_name:<28} | CO2: {uptake_mol:<8} mol/kg ({uptake_cm3} cm³/g)"
    )
    results.append((mof_name, uptake_mol, uptake_cm3))

csv_path = os.path.join(raspa_dir, "all_mofs_co2_uptake_results.csv")
with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write("MOF_Name,CO2_Uptake_mol_per_kg,CO2_Uptake_cm3_per_g\n")
    for r in results:
        f.write(f"{r[0]},{r[1]},{r[2]}\n")

print("-----------------------------------------------------------------")
print(f"전체 연산 및 파싱 완료. 결과 표 저장: {csv_path}")
