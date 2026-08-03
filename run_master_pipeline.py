import os
import glob
import math
import subprocess
import ast
import re
import shutil
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use("Agg")  # 헤드리스 환경에서 plt.show()가 GUI 이벤트 루프를 기다리며 무한 대기하는 것을 방지
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# 1. 폰트 및 마이너스 기호 방어
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['axes.unicode_minus'] = False 

# =================================================================
# 2. 환경 경로 및 기본 파라미터 설정
# =================================================================
WORK_DIR = os.path.expanduser("~/mof_project")

# 신규 생성한 MTV-ZIF 폴더가 존재하면 우선 적용하고, 없으면 기존 정제 폴더 적용
CIF_DIR = os.path.join(WORK_DIR, "03_Generated_MTV_ZIFs")
if not os.path.exists(CIF_DIR) or len(glob.glob(os.path.join(CIF_DIR, "*.cif"))) == 0:
    CIF_DIR = os.path.join(WORK_DIR, "01_CIF_Cleaned")

RESULTS_DIR = os.path.join(WORK_DIR, "02_HTS_Master_Results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# RASPA Widom 시뮬레이션 설정 (무한 희석 극저압 1e-5 Pa, 298K)
TEMP_WIDOM = 298.0
PRESS_WIDOM = 1e-5
CYCLES_WIDOM = 5000

# [핵심 보완] subprocess가 PATH 상에서 simulate 바이너리를 못 찾는 문제 방지
# (예: czeromof conda 환경이 activate 되지 않은 셸에서 스크립트를 실행하는 경우)
_SIMULATE_FALLBACKS = [
    os.path.expanduser("~/miniconda3/envs/czeromof/bin/simulate"),
    os.path.expanduser("~/anaconda3/envs/czeromof/bin/simulate"),
]
SIMULATE_BIN = shutil.which("simulate")
if not SIMULATE_BIN:
    SIMULATE_BIN = next((p for p in _SIMULATE_FALLBACKS if os.path.isfile(p)), None)

if SIMULATE_BIN:
    print(f"[안내] RASPA simulate 바이너리 확인: {SIMULATE_BIN}")
else:
    print("[경고] 'simulate' 바이너리를 PATH 및 알려진 conda 환경 경로에서 찾을 수 없습니다. "
          "'conda activate czeromof' 후 재실행하거나 SIMULATE_BIN을 직접 지정하세요.")

if not os.environ.get("RASPA_DIR"):
    print("[경고] 환경변수 RASPA_DIR이 설정되어 있지 않습니다. GenericMOFs forcefield를 찾지 못할 수 있습니다.")

print("=== [시작] MOF HTS 기공(Zeo++) 및 열역학(RASPA Widom) 통합 스크리닝 ===")
print(f"대상 CIF 폴더: {CIF_DIR}")
print("-----------------------------------------------------------------")

# =================================================================
# 3. 독립 연산 모듈 함수 정의
# =================================================================
def run_zeopp_full(cif_path, work_dir):
    """Zeo++ CLI 호출을 통해 LCD, PLD, Dif, VF, PV 일괄 연산"""
    mof_name = os.path.splitext(os.path.basename(cif_path))[0]
    res_file = os.path.join(work_dir, f"{mof_name}.res")
    vol_file = os.path.join(work_dir, f"{mof_name}.vol")
    
    lcd, pld, dif = 0.0, 0.0, 0.0
    vf, pv = 0.0, 0.0
    
    # 1. 기공 직경 연산 (-res)
    try:
        subprocess.run(["network", "-ha", "-res", res_file, cif_path], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(res_file):
            with open(res_file, "r") as f:
                parts = f.readline().split()
                if len(parts) >= 4:
                    lcd, pld, dif = float(parts[1]), float(parts[2]), float(parts[3])
            os.remove(res_file)
    except Exception:
        pass

    # 2. 기공 부피 및 비율 연산 (-vol 질소 프로브 1.82 Å 기준)
    try:
        subprocess.run(["network", "-ha", "-vol", "1.82", "1.82", "20000", vol_file, cif_path], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(vol_file):
            with open(vol_file, "r") as f:
                content = f.read()
            # [버그 수정] 설치된 Zeo++ 버전은 구형 태그(PORE_VOLUME/PORE_SPACE) 대신
            # AV_A^3(접근 가능 부피)/AV_Volume_fraction 태그를 출력하므로 이를 파싱한다.
            m_pv = re.search(r"AV_A\^3:\s*([0-9.eE+-]+)", content)
            m_vf = re.search(r"AV_Volume_fraction:\s*([0-9.eE+-]+)", content)
            if m_pv: pv = float(m_pv.group(1))
            if m_vf: vf = float(m_vf.group(1))
            os.remove(vol_file)
    except Exception:
        pass

    # [Priority 4] 호흡효과/게이트오프닝으로 실제로는 열리는 구조가 정적 스냅샷 하나로는
    # PLD가 프로브보다 작게 나와 접근 가능 부피(AV)가 0으로 찍히는 경우가 있다. 이를 "진짜
    # 비다공성 0"과 구분 없이 그대로 스코어링에 흘려보내면 게이트오프닝 후보가 부당하게
    # 최하위로 밀린다. CCDC에 등록된 열린/닫힌 상 재조회는 CSD 접근 권한이 없어 범위 밖이므로,
    # 여기서는 "결측/후속검증필요"로 구분 표시만 한다 (0을 그대로 믿지 말라는 신호).
    # 기준은 문헌상 자주 인용되는 "3.4A"가 아니라 위 -vol 프로브 지름(1.82*2=3.64A)으로 잡는다
    # -- 실측 결과 ZIF-8 자체의 PLD가 3.409A로 나와 3.4A 컷을 쓰면 정작 게이트오프닝의 대표
    # 사례인 ZIF-8이 컷 아래로 빠져버리는 걸 확인했다(3.409 > 3.4). 프로브 지름 기준이 이
    # 파이프라인이 실제로 쓰는 값과 일관되고, ZIF-8도 올바르게 플래그된다(3.409 < 3.64).
    probe_diameter = 1.82 * 2
    if pld == 0.0 and lcd == 0.0:
        porosity_flag = "계산실패"
    elif pv > 0:
        porosity_flag = "정상"
    elif pld < probe_diameter:
        porosity_flag = f"결측_재검증필요(정적구조 폐쇄 가능성, PLD<{probe_diameter:.2f}A)"
    else:
        porosity_flag = "정상(비다공성)"

    return {"dimension": 3, "LCD": round(lcd, 3), "PLD": round(pld, 3),
            "Dif": round(dif, 3), "VF": round(vf, 4), "PV": round(pv, 4),
            "Porosity_Flag": porosity_flag}

def get_unit_cells(cif_path, cutoff=12.0):
    min_box = cutoff * 2.0
    a, b, c = 10.0, 10.0, 10.0
    with open(cif_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "_cell_length_a" in line and not line.strip().startswith("#"):
                vals = [float(s) for s in line.split() if s.replace('.','',1).replace('-','',1).isdigit()]
                if vals: a = vals[0]
            elif "_cell_length_b" in line and not line.strip().startswith("#"):
                vals = [float(s) for s in line.split() if s.replace('.','',1).replace('-','',1).isdigit()]
                if vals: b = vals[0]
            elif "_cell_length_c" in line and not line.strip().startswith("#"):
                vals = [float(s) for s in line.split() if s.replace('.','',1).replace('-','',1).isdigit()]
                if vals: c = vals[0]
    return max(1, math.ceil(min_box/a)), max(1, math.ceil(min_box/b)), max(1, math.ceil(min_box/c))

def run_raspa_widom(cif_path, work_dir, gas_name):
    """Widom Test Particle Insertion을 통한 헨리 상수(KH) 도출 (CIF 복사 및 안전 파싱 적용)"""
    mof_name = os.path.splitext(os.path.basename(cif_path))[0]
    gas_dir = os.path.join(work_dir, f"widom_{gas_name}_{mof_name}")
    os.makedirs(gas_dir, exist_ok=True)
    
    # [핵심 보완 1] RASPA가 실행되는 폴더 안으로 CIF 파일을 반드시 복사
    target_cif_path = os.path.join(gas_dir, f"{mof_name}.cif")
    shutil.copy(cif_path, target_cif_path)
    
    na, nb, nc = get_unit_cells(cif_path)
    
    # [핵심 보완 2] CIF 내부에 부분 전하가 없을 때의 연산 종료 방지를 위해 'no'로 고정
    sim_input = f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES_WIDOM}
NumberOfInitializationCycles  1000
PrintEvery                    1000
RestartFile                   no

Forcefield                    GenericMOFs
CutOff                        12.0
UseChargesFromCIFFile         no

Framework 0
FrameworkName                 {mof_name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP_WIDOM}
ExternalPressure              {PRESS_WIDOM}

Component 0 MoleculeName              {gas_name}
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
"""
    with open(os.path.join(gas_dir, "simulation.input"), "w") as f:
        f.write(sim_input)
        
    kh_val = 0.0

    if not SIMULATE_BIN:
        print(f"\n[오류] {mof_name}/{gas_name}: simulate 바이너리를 찾을 수 없어 실행을 건너뜁니다.")
        return kh_val

    try:
        proc = subprocess.run(
            [SIMULATE_BIN, "simulation.input"],
            cwd=gas_dir,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if proc.returncode != 0:
            print(f"\n[오류] {mof_name}/{gas_name}: simulate 종료 코드 {proc.returncode}")
            if proc.stdout.strip():
                print(f"  --- stdout(tail) ---\n{proc.stdout.strip()[-1500:]}")
            if proc.stderr.strip():
                print(f"  --- stderr(tail) ---\n{proc.stderr.strip()[-1500:]}")
            return kh_val

        out_files = glob.glob(os.path.join(gas_dir, "Output", "System_0", "*.data"))
        if not out_files:
            print(f"\n[오류] {mof_name}/{gas_name}: Output/System_0/*.data 파일이 생성되지 않았습니다.")
            if proc.stdout.strip():
                print(f"  --- stdout(tail) ---\n{proc.stdout.strip()[-1500:]}")
            return kh_val

        with open(out_files[0], "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # [핵심 보완 3] 정규표현식을 이용해 단위([mol/kg/Pa]) 바로 앞의 숫자만 정확하게 추출
                if "average henry coefficient" in line.lower() and "[mol/kg/pa]" in line.lower():
                    match = re.search(r"Average Henry coefficient:\s+([0-9.eE+-]+)\s+\+/-\s+[0-9.eE+-]+\s+\[mol/kg/Pa\]", line, re.IGNORECASE)
                    if match:
                        kh_val = float(match.group(1))

        if kh_val == 0.0:
            print(f"\n[경고] {mof_name}/{gas_name}: Henry coefficient 라인을 파싱하지 못했습니다 ({out_files[0]}).")

    except Exception as exc:
        print(f"\n[예외] {mof_name}/{gas_name}: {type(exc).__name__}: {exc}")

    return kh_val

# =================================================================
# 4. 전체 CIF 시뮬레이션 및 데이터 수집 루프
# =================================================================
cif_files = sorted(glob.glob(os.path.join(CIF_DIR, "*.cif")))
sim_results = []

for idx, cif in enumerate(cif_files, 1):
    name = os.path.splitext(os.path.basename(cif))[0]
    print(f"[{idx:02d}/{len(cif_files):02d}] 연산 중: {name:<30}", end="", flush=True)
    
    # Zeo++ 기공 특성 연산
    zeo_data = run_zeopp_full(cif, RESULTS_DIR)
    
    # RASPA Widom 헨리 상수 연산
    kh_co2 = run_raspa_widom(cif, RESULTS_DIR, "CO2")
    kh_n2 = run_raspa_widom(cif, RESULTS_DIR, "N2")
    
    selectivity = (kh_co2 / kh_n2) if kh_n2 > 0 else 1.0
    gemc_data = {"Widom": [round(kh_co2, 6), round(kh_n2, 6)]}
    
    # 메타데이터 자동 주입
    metal_type = "Co" if "co" in name.lower() or "zif-67" in name.lower() else "Zn"
    metal_data = {"metal_type": metal_type, "has_OMS": False}
    topo_val = "gme" if "gme" in name.lower() or "ratio" in name.lower() else "sod"
    
    # 식별자 구성
    short_id = name.split("_")[0] if "_" in name else name[:6].upper()
    id_data = {"mofid-v1": f"{name};{short_id};{topo_val}"}
    
    sim_results.append({
        "MOF_Name": name,
        "Short_ID": short_id,
        "id": str(id_data),
        "GEMC_data": str(gemc_data),
        "Zeopp": str(zeo_data),
        "metal": str(metal_data),
        "Topology": topo_val,
        "OMS": False,
        "Stability": "Robust" if metal_type == "Zn" else "Core",
        "CO2_Affinity": kh_co2,
        "Selectivity": round(selectivity, 3),
        "Dimension": zeo_data["dimension"],
        "LCD": zeo_data["LCD"],
        "PLD": zeo_data["PLD"],
        "VF": zeo_data["VF"],
        "PV": zeo_data["PV"],
        "Porosity_Flag": zeo_data["Porosity_Flag"],
        "Base_Group": "High-Flux (Wide)" if zeo_data["PLD"] >= 3.8 else "N2-Sieving (Narrow)"
    })
    
    print(f"\r[성공] {name:<30} | PLD: {zeo_data['PLD']:<6} | KH(CO2): {kh_co2:<8.4e} | Sel: {selectivity:<6.2f}")

df_sim = pd.DataFrame(sim_results)

# =================================================================
# 5. RACs 및 원본 메타데이터 100% 병합 (Data Preservation)
# =================================================================
print("\n[안내] RACs 및 원본 데이터 병합 프로세스 시작...")
racs_files = glob.glob(os.path.join(WORK_DIR, "*Sieving*.csv")) + glob.glob(os.path.join(WORK_DIR, "*Flux*.csv"))

if racs_files:
    df_racs_list = []
    for r_file in racs_files:
        try:
            df_temp = pd.read_csv(r_file)
            df_racs_list.append(df_temp)
        except Exception:
            pass
            
    if df_racs_list:
        df_racs_merged = pd.concat(df_racs_list, ignore_index=True)
        merge_key = 'MOF_Name' if 'MOF_Name' in df_racs_merged.columns else 'id'
        
        # 중복 연산 컬럼 제거 후 외부 조인으로 RACs 열 완벽 보존
        cols_to_drop = [c for c in ['GEMC_data', 'Zeopp', 'metal', 'CO2_Affinity', 'Selectivity'] if c in df_racs_merged.columns]
        df_racs_clean = df_racs_merged.drop(columns=cols_to_drop, errors='ignore')
        
        df_valid = pd.merge(df_sim, df_racs_clean, left_on='MOF_Name', right_on=merge_key, how='left')
        print(f"[안내] 기존 RACs 파일({len(racs_files)}개)과 성공적으로 병합되었습니다.")
    else:
        df_valid = df_sim
else:
    print("[안내] 병합할 RACs 원본 파일이 없어 시뮬레이션 도출 열을 모두 출력합니다.")
    df_valid = df_sim

# =================================================================
# 6. 스코어링 연산: 기공 부피(PV) 상한선 하드코딩(clip) 제거
# =================================================================
df_valid['Log_K_H'] = np.log10(df_valid['CO2_Affinity'] + 1e-9)
df_valid['K_H_Norm'] = (df_valid['Log_K_H'] - df_valid['Log_K_H'].min()) / (df_valid['Log_K_H'].max() - df_valid['Log_K_H'].min() + 1e-9) * 100

# [Priority 4] Porosity_Flag가 "정상" 계열이 아닌 행(정적 구조가 닫혀 PV=0으로 찍힌
# 게이트오프닝 의심 후보, 계산 실패)이 min-max 정규화에 섞이면 스케일 자체가 왜곡되고
# PV_Norm=0 -> DAC/FlueGas 점수 최하위로 부당하게 깔린다. 정규화 기준은 신뢰 가능한
# 행으로만 잡고, 플래그 붙은 행은 PV_Norm을 NaN(미확정)으로 남겨 0점이 아니라
# "후속 검증 필요"로 구분되게 한다(값이 NaN이면 아래 점수도 자동으로 NaN이 됨).
trustworthy = df_valid['Porosity_Flag'].isin(['정상', '정상(비다공성)'])
pv_ref = df_valid.loc[trustworthy, 'PV'] if trustworthy.any() else df_valid['PV']
pv_min, pv_max = pv_ref.min(), pv_ref.max()
df_valid['PV_Norm'] = np.where(
    trustworthy,
    (df_valid['PV'] - pv_min) / (pv_max - pv_min + 1e-9) * 100,
    np.nan,
)

def calculate_scores(row):
    kh, pv, has_oms = row['K_H_Norm'], row['PV_Norm'], row['OMS']
    flue_score = (kh * 0.5) + (pv * 0.5)
    dac_score = (kh * 0.8) + (pv * 0.2)
    if has_oms: dac_score *= 1.3 
    return pd.Series([flue_score, dac_score])

df_valid[['FlueGas_Score', 'DAC_Score']] = df_valid.apply(calculate_scores, axis=1)

# =================================================================
# 7. 3종 CSV 독립 추출 (전체 / N2-Sieving / High-Flux)
# =================================================================
primary_cols = [
    'MOF_Name', 'Short_ID', 'id', 'Base_Group', 'Metal', 'Topology', 'OMS', 'Stability',
    'FlueGas_Score', 'DAC_Score', 'CO2_Affinity', 'Selectivity',
    'Dimension', 'LCD', 'PLD', 'VF', 'PV', 'Porosity_Flag', 'K_H_Norm', 'PV_Norm'
]
primary_cols = [col for col in primary_cols if col in df_valid.columns]
remaining_cols = [col for col in df_valid.columns if col not in primary_cols]
full_export_cols = primary_cols + remaining_cols

# [출력 1] 전체 통합 성능 표
df_export_all = df_valid[full_export_cols].sort_values(by='DAC_Score', ascending=False)
file_all = os.path.join(RESULTS_DIR, "MOF_Comprehensive_Performance_Scores.csv")
df_export_all.to_csv(file_all, index=False, encoding='utf-8-sig')
print(f"[안내] 1. 전체 통합 표 저장 완료: {file_all} ({len(df_export_all)}개 구조)")

# [출력 2] N2-Sieving (Narrow) 그룹 전용 표
df_export_n2 = df_export_all[df_export_all['Base_Group'] == 'N2-Sieving (Narrow)']
file_n2 = os.path.join(RESULTS_DIR, "MOF_N2_Sieving_Performance_Scores.csv")
df_export_n2.to_csv(file_n2, index=False, encoding='utf-8-sig')
print(f"[안내] 2. N2-Sieving 전용 표 저장 완료: {file_n2} ({len(df_export_n2)}개 구조)")

# [출력 3] High-Flux (Wide) 그룹 전용 표
df_export_flux = df_export_all[df_export_all['Base_Group'] == 'High-Flux (Wide)']
file_flux = os.path.join(RESULTS_DIR, "MOF_High_Flux_Performance_Scores.csv")
df_export_flux.to_csv(file_flux, index=False, encoding='utf-8-sig')
print(f"[안내] 3. High-Flux 전용 표 저장 완료: {file_flux} ({len(df_export_flux)}개 구조)")
print(f"[안내] 포함된 전체 열(Column) 수: {len(full_export_cols)}개 (RACs 및 원본 메타데이터 100% 보존)")

# =================================================================
# 8. 4대 그룹 프론티어 그래프 개별 출력
# =================================================================
# 금속(metal_type)만으로는 같은 금속 노드를 공유하는 구조들을 구분할 수 없으므로,
# 구조(MOF_Name) 단위로 고유 색상을 부여하고, 색상-이름 인덱스를 그래프 옆에 표기한다.
unique_names = sorted(df_valid['MOF_Name'].unique())
name_color_map = dict(zip(unique_names, sns.color_palette("husl", n_colors=len(unique_names))))

global_xlim = (df_valid['CO2_Affinity'].min() * 0.5, df_valid['CO2_Affinity'].max() * 2.0)
global_ylim = (df_valid['Selectivity'].min() * 0.5, df_valid['Selectivity'].max() * 2.0)

def draw_quadrant_frontier(df, stability_type, process_type, score_col, filename):
    if len(df) == 0: return

    fig, ax = plt.subplots(figsize=(14, 9))
    sns.set_theme(style="whitegrid")

    for _, row in df.iterrows():
        ax.scatter(row['CO2_Affinity'], row['Selectivity'],
                   color=name_color_map[row['MOF_Name']], marker='o',
                   s=350, alpha=0.85, edgecolor='black', linewidth=1.2, zorder=3)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(global_xlim)
    ax.set_ylim(global_ylim)

    # 점이 밀집되어 있어 전체 라벨링은 겹침을 유발하므로 상위 3개만 직접 표기하고,
    # 나머지 구조 식별은 우측 색상-이름 인덱스(범례)로 처리한다.
    top_targets = df.nlargest(3, score_col)
    for _, row in top_targets.iterrows():
        label_name = row['MOF_Name'].replace('MTV_ZIF8_nIm_', '')
        ax.annotate(label_name, (row['CO2_Affinity'], row['Selectivity']),
                     xytext=(8, 8), textcoords='offset points', fontsize=13, fontweight='bold')

    title = f"MOF Frontier: {stability_type} Materials evaluated for {process_type}"
    ax.set_title(title, fontsize=20, fontweight='bold', pad=18)
    ax.set_xlabel('CO$_2$ Affinity (Widom $K_H$)', fontsize=15)
    ax.set_ylabel('Selectivity (CO$_2$ / N$_2$)', fontsize=15)
    ax.grid(True, which="both", ls="--", alpha=0.4)
    ax.tick_params(labelsize=13)

    # 이름-색상 인덱스(범례)를 그래프 우측에 배치
    df_names = sorted(df['MOF_Name'].unique())
    legend_handles = [
        Line2D([0], [0], marker='o', linestyle='', markersize=10,
               markerfacecolor=name_color_map[n], markeredgecolor='black', label=n)
        for n in df_names
    ]
    ax.legend(handles=legend_handles, title='MOF (Color Index)', bbox_to_anchor=(1.04, 1),
              loc='upper left', fontsize=9, title_fontsize=13,
              ncol=1 if len(df_names) <= 18 else 2,
              labelspacing=0.8, handletextpad=0.8, borderpad=1.0)

    plt.tight_layout()
    plt.savefig(filename, dpi=600, bbox_inches='tight')
    plt.show()
    plt.close(fig)

plot_configs = [
    ('Core', 'DAC', 'DAC_Score', os.path.join(RESULTS_DIR, 'Frontier_Core_DAC.png')),
    ('Core', 'Flue Gas', 'FlueGas_Score', os.path.join(RESULTS_DIR, 'Frontier_Core_FlueGas.png')),
    ('Robust', 'DAC', 'DAC_Score', os.path.join(RESULTS_DIR, 'Frontier_Robust_DAC.png')),
    ('Robust', 'Flue Gas', 'FlueGas_Score', os.path.join(RESULTS_DIR, 'Frontier_Robust_FlueGas.png'))
]

for idx, (stab, proc, score_col, fname) in enumerate(plot_configs, 1):
    print(f"[{idx}/4] [{stab} - {proc}] 타겟 프론티어 맵 출력 중...")
    sub_df = df_valid[df_valid['Stability'] == stab]
    draw_quadrant_frontier(sub_df, stab, proc, score_col, fname)

print("[완료] 4대 그룹 개별 그래프 및 3종 성능 CSV 추출이 완벽하게 완료되었습니다.")
