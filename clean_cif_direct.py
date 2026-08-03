import glob
import os
import re

input_dir = os.path.expanduser("~/mof_project/01_CIF_Data")
output_dir = os.path.expanduser("~/mof_project/01_CIF_Cleaned")
os.makedirs(output_dir, exist_ok=True)

cif_files = glob.glob(os.path.join(input_dir, "*.cif"))
print(f"=== 총 {len(cif_files)}개 CIF 파일 고속 정제 및 분할 시작 ===")

total_saved = 0

for filepath in cif_files:
    filename = os.path.basename(filepath)
    # 1. 파일명 공백 및 특수문자 제거
    clean_filename = re.sub(r"\s+", "_", filename).replace("_-_", "_").replace("-_-", "_")
    base_name = os.path.splitext(clean_filename)[0]

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    # 2. 줄 단위로 빠르게 읽으면서 Zeo++ 에러를 일으키는 대칭성 따옴표만 100% 안전하게 제거
    new_lines = []
    in_sym_loop = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("_symmetry_equiv_pos_as_xyz") or stripped.startswith("_space_group_symop_operation_xyz"):
            in_sym_loop = True
            new_lines.append(line)
            continue
            
        if in_sym_loop:
            if stripped.startswith("_") or stripped.startswith("loop_") or stripped.startswith("data_"):
                in_sym_loop = False
            elif stripped and not stripped.startswith("#"):
                # 'x, y, z' -> x, y, z (따옴표 벗기기)
                line = line.replace("'", "").replace('"', "")
                
        new_lines.append(line)

    text = "".join(new_lines)

    # 3. 한 파일에 여러 실험 조건(data_)이 뭉쳐 있는 경우 개별 파일로 분할
    data_blocks = re.split(r"(^data_[^\r\n]+)", text, flags=re.MULTILINE)

    if len(data_blocks) > 3:
        header = data_blocks[0]
        for i in range(1, len(data_blocks), 2):
            data_title = data_blocks[i].strip()
            data_content = data_blocks[i + 1]

            sub_name = re.sub(r"^data_", "", data_title).strip()
            sub_name = re.sub(r"[^a-zA-Z0-9_-]", "_", sub_name)

            out_name = f"{base_name}_{sub_name}.cif"
            out_path = os.path.join(output_dir, out_name)

            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(header + "\n" + data_title + data_content)
            total_saved += 1
            print(f"[분할 완료] {out_name}")
    else:
        out_path = os.path.join(output_dir, clean_filename)
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(text)
        total_saved += 1
        print(f"[정제 완료] {clean_filename}")

print(f"\n=== 최종 완료: 총 {total_saved}개의 완벽한 시뮬레이션용 CIF 파일 생성 ===")
