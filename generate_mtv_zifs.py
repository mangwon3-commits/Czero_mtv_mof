import os
import random
import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list

# 1. 경로 설정
WORK_DIR = os.path.expanduser("~/mof_project")
INPUT_CIF = os.path.join(WORK_DIR, "01_CIF_Cleaned", "ZIF-8.cif")
OUTPUT_DIR = os.path.join(WORK_DIR, "03_Generated_MTV_ZIFs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. 생성할 블렌딩 비율 및 앙상블 수 설정
RATIOS = [0.0, 0.25, 0.50, 0.75, 1.0]
ENSEMBLE_SIZE = 3
TARGET_BOND_LEN_CN = 1.47  # C-N(NO2) 표준 결합 길이 (Å)
TARGET_BOND_LEN_NO = 1.22  # N-O(NO2) 표준 결합 길이 (Å)

print("=== ZIF-8 기반 MTV-ZIF (mIm + nIm 블렌딩) 구조 생성 시작 ===")
print(f"원본 모체 구조: {INPUT_CIF}")
print(f"출력 폴더: {OUTPUT_DIR}")
print("-----------------------------------------------------------------")

if not os.path.exists(INPUT_CIF):
    print("[오류] 원본 ZIF-8.cif 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    exit(1)

# 원본 구조 로드
base_atoms = read(INPUT_CIF)
symbols = np.array(base_atoms.get_chemical_symbols())
positions = base_atoms.get_positions()

# 3. 2번 탄소(C2)에 붙은 메틸 탄소(C_me) 타겟 사이트 탐색
# ZIF-8에서 메틸 탄소는 수소 3개와 이미다졸 고리의 탄소 1개와만 결합함
i_idx, j_idx, dists = neighbor_list('ijd', base_atoms, 1.6)

c2_methyl_targets = []
for i in range(len(base_atoms)):
    if symbols[i] == 'C':
        # 주변 결합 원자 확인
        neighbors = [j_idx[k] for k, val in enumerate(i_idx) if val == i]
        n_symbols = [symbols[n] for n in neighbors]
        # 고리 탄소(N 2개와 결합)에 붙은 외곽 탄소가 메틸 탄소임
        if n_symbols.count('N') == 0 and n_symbols.count('C') == 1:
            ring_c_idx = neighbors[n_symbols.index('C')]
            c2_methyl_targets.append((ring_c_idx, i))

c2_methyl_targets = list(set(c2_methyl_targets))
total_sites = len(c2_methyl_targets)
print(f"[안내] 탐색된 총 mIm 치환 가능 사이트: {total_sites}개")
print("-----------------------------------------------------------------")

# 4. 비율별 MTV 구조 생성 루프
generated_count = 0
for ratio in RATIOS:
    num_replace = int(total_sites * ratio)
    current_ensemble = 1 if (ratio == 0.0 or ratio == 1.0) else ENSEMBLE_SIZE
    
    for ens_idx in range(1, current_ensemble + 1):
        atoms_copy = base_atoms.copy()
        selected_targets = random.sample(c2_methyl_targets, num_replace)
        
        atoms_to_remove = []
        new_atoms = []
        
        for ring_c, me_c in selected_targets:
            # 메틸 탄소 및 여기에 붙은 수소 원자들 찾기
            atoms_to_remove.append(me_c)
            for k, val in enumerate(i_idx):
                if val == me_c and symbols[j_idx[k]] == 'H':
                    atoms_to_remove.append(j_idx[k])
            
            # 고리 탄소에서 바깥쪽으로 향하는 백터 계산
            vec_out = positions[me_c] - positions[ring_c]
            unit_vec = vec_out / np.linalg.norm(vec_out)
            
            # NO2 그룹의 중심 질소(N) 위치 계산
            pos_N = positions[ring_c] + unit_vec * TARGET_BOND_LEN_CN
            new_atoms.append(('N', pos_N))
            
            # NO2 그룹의 산소(O) 2개 대칭 배치 (간단한 평면 직교 백터 계산)
            perp_vec = np.array([-unit_vec[1], unit_vec[0], 0.0])
            if np.linalg.norm(perp_vec) < 1e-3:
                perp_vec = np.array([0.0, -unit_vec[2], unit_vec[1]])
            perp_vec = perp_vec / np.linalg.norm(perp_vec)
            
            pos_O1 = pos_N + (unit_vec * 0.5 + perp_vec * 0.866) * TARGET_BOND_LEN_NO
            pos_O2 = pos_N + (unit_vec * 0.5 - perp_vec * 0.866) * TARGET_BOND_LEN_NO
            new_atoms.append(('O', pos_O1))
            new_atoms.append(('O', pos_O2))
            
        # 역순 정렬 후 원본 메틸 그룹 원자 삭제
        for idx_rm in sorted(list(set(atoms_to_remove)), reverse=True):
            del atoms_copy[idx_rm]
            
        # 신규 NO2 작용기 원자 추가
        for sym, pos in new_atoms:
            atoms_copy.append(sym)
            atoms_copy.positions[-1] = pos
            
        # 파일명 지정 및 저장
        out_name = f"MTV_ZIF8_nIm_ratio{int(ratio*100):03d}_ens{ens_idx}.cif"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        write(out_path, atoms_copy, format='cif')
        
        # ASE가 기록하는 신형(mmCIF) 대칭군 태그(_space_group_name_H-M_alt 등)는
        # RASPA의 CIF 파서가 인식하지 못해 "no proper space group definition found" 오류로
        # 조용히(exit 0) 종료되므로, RASPA/Zeo++가 요구하는 구형 태그로 변환한다.
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("_space_group_name_H-M_alt", "_symmetry_space_group_name_H-M")
        content = content.replace("_space_group_IT_number", "_symmetry_Int_Tables_number")
        content = content.replace("_space_group_symop_operation_xyz", "_symmetry_equiv_pos_as_xyz")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        generated_count += 1
        print(f"[생성 완료] {out_name:<32} (치환율: {ratio*100:5.1f}% | 치환 수: {num_replace}/{total_sites})")

print("-----------------------------------------------------------------")
print(f"[최종 완료] 총 {generated_count}개의 신규 MTV-ZIF 후보 구조가 '{OUTPUT_DIR}'에 생성되었습니다.")
