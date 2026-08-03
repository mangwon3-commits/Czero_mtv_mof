import os
import glob
import re
from pymatgen.io.cif import CifParser, CifWriter
import warnings
warnings.filterwarnings("ignore")

# 1. 입출력 폴더 경로 설정
input_dir = os.path.expanduser("~/mof_project/01_CIF_Data")
output_dir = os.path.expanduser("~/mof_project/01_CIF_Cleaned")
os.makedirs(output_dir, exist_ok=True)

def remove_empty_loops(cif_text):
    """데이터 행 없이 헤더만 존재하는 텅 빈 loop_ 블록을 정규식으로 제거"""
    pattern = r"loop_\s*(?:_[^\s]+\s*)+(?=(?:loop_|_|#|\Z))"
    return re.sub(pattern, "", cif_text)

cif_files = glob.glob(os.path.join(input_dir, "*.cif"))
print(f"=== 총 {len(cif_files)}개 CIF 파일 전처리 및 P1 변환 시작 ===")

success_count = 0
for filepath in cif_files:
    filename = os.path.basename(filepath)
    outpath = os.path.join(output_dir, filename)
    
    try:
        # 1단계: 텍스트 수준에서 빈 loop_ 및 구문 충돌 요소 1차 정제
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
        cleaned_text = remove_empty_loops(raw_text)
        
        temp_path = filepath + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        # 2단계: pymatgen 파서로 구조 읽기 (점유율 오차 허용치 상향)
        parser = CifParser(temp_path, occupancy_tolerance=100.0)
        structure = parser.get_structures()[0]
        
        # 3단계: symprec=None 옵션으로 대칭성을 P1으로 풀어서 표준 양식 작성
        writer = CifWriter(structure, symprec=None)
        writer.write_file(outpath)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
        success_count += 1
        print(f"[성공] {filename} -> P1 변환 완료")
        
    except Exception as e:
        if os.path.exists(filepath + ".tmp"):
            os.remove(filepath + ".tmp")
        print(f"[실패] {filename}: {e}")

print(f"\n=== 완료: {success_count}/{len(cif_files)}개 파일 성공 ===")
print(f"정제된 파일 경로: {output_dir}")


