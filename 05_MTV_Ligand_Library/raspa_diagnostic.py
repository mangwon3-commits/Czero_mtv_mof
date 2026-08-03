#!/usr/bin/env python3
"""
RASPA Widom Insertion 실패 진단 스크립트
사용법: python3 raspa_diagnostic.py <simulation_dir>
<simulation_dir> 안에는 simulation.input, 대상 CIF 파일이 있어야 함.
"""

import os
import re
import shutil
import subprocess
import sys

def check_env():
    print("=== 1. 환경 변수 확인 ===")
    raspa_dir = os.environ.get("RASPA_DIR")
    path = os.environ.get("PATH")
    print(f"RASPA_DIR: {raspa_dir}")
    print(f"PATH에 simulate 존재 여부: {shutil.which('simulate')}")
    if raspa_dir:
        ff_dir = os.path.join(raspa_dir, "share", "raspa", "forcefield")
        print(f"Forcefield 디렉토리 존재: {os.path.isdir(ff_dir)} ({ff_dir})")
        if os.path.isdir(ff_dir):
            print("사용 가능한 forcefield 목록:", os.listdir(ff_dir))
    else:
        print("[경고] RASPA_DIR이 설정되어 있지 않습니다. .bashrc 또는 실행 환경변수 확인 필요.")
    print()

def check_simulate_binary():
    print("=== 2. simulate 바이너리 실행 가능 여부 ===")
    path = shutil.which("simulate")
    if not path:
        print("[치명적] simulate 바이너리를 PATH에서 찾을 수 없습니다.")
        return False
    print(f"경로: {path}, 실행권한: {os.access(path, os.X_OK)}")
    try:
        result = subprocess.run(["simulate", "--help"], capture_output=True, text=True, timeout=10)
        print(f"--help 실행 returncode: {result.returncode}")
        if result.returncode != 0:
            print("STDERR:", result.stderr[:500])
    except Exception as e:
        print(f"[치명적] simulate 실행 자체가 실패: {e}")
        return False
    print()
    return True

def check_input_files(sim_dir):
    print("=== 3. simulation.input 및 Framework 파일 매칭 확인 ===")
    input_path = os.path.join(sim_dir, "simulation.input")
    if not os.path.exists(input_path):
        print("[치명적] simulation.input 파일이 없습니다.")
        return None
    with open(input_path) as f:
        content = f.read()
    print(content)

    m = re.search(r"FrameworkName\s+(\S+)", content)
    ff_m = re.search(r"Forcefield\s+(\S+)", content)
    framework_name = m.group(1) if m else None
    forcefield_name = ff_m.group(1) if ff_m else None

    if framework_name:
        cif_path = os.path.join(sim_dir, framework_name + ".cif")
        print(f"기대되는 CIF 경로: {cif_path}, 존재 여부: {os.path.exists(cif_path)}")
        if not os.path.exists(cif_path):
            print("[치명적] FrameworkName과 실제 CIF 파일명이 일치하지 않습니다.")
    else:
        print("[경고] simulation.input에서 FrameworkName을 찾지 못했습니다.")

    return framework_name, forcefield_name

def check_forcefield_atom_types(sim_dir, framework_name, forcefield_name):
    print("=== 4. CIF 원자 타입 vs Forcefield 정의 매칭 확인 (가장 흔한 원인) ===")
    if not framework_name:
        print("Framework 정보 부족으로 스킵")
        return

    cif_path = os.path.join(sim_dir, framework_name + ".cif")
    if not os.path.exists(cif_path):
        print("CIF 없음, 스킵")
        return

    cif_atoms = set()
    with open(cif_path) as f:
        in_loop = False
        for line in f:
            if line.strip().startswith("_atom_site_label") or line.strip().startswith("_atom_site_type_symbol"):
                in_loop = True
                continue
            if in_loop:
                parts = line.split()
                if len(parts) >= 1 and not line.strip().startswith("_") and not line.strip().startswith("loop_"):
                    cif_atoms.add(parts[0])
                elif line.strip().startswith("_") or line.strip() == "":
                    if len(cif_atoms) > 0:
                        break
    print(f"CIF에서 발견된 원자 라벨: {sorted(cif_atoms)}")

    raspa_dir = os.environ.get("RASPA_DIR")
    if raspa_dir and forcefield_name:
        pseudo_path = os.path.join(raspa_dir, "share", "raspa", "forcefield", forcefield_name, "pseudo_atoms.def")
        if os.path.exists(pseudo_path):
            with open(pseudo_path) as f:
                defined = set(re.findall(r"^\s*([A-Za-z0-9_]+)\s", f.read(), re.MULTILINE))
            missing = cif_atoms - defined
            print(f"pseudo_atoms.def에 정의되지 않은 CIF 원자 타입: {missing if missing else '없음'}")
            if missing:
                print("[유력한 원인] 위 원자 타입들이 forcefield에 정의되어 있지 않아 RASPA가 즉시 크래시했을 가능성이 높습니다.")
                print("특히 nIm 치환에 사용된 N, O(nitro group) 원자 타입이 GenericMOFs에 기본 정의되어 있지 않을 수 있습니다.")
        else:
            print(f"[경고] pseudo_atoms.def를 찾을 수 없음: {pseudo_path}")
    print()

def run_actual_simulation(sim_dir):
    print("=== 5. 실제 시뮬레이션 실행 (전체 stdout/stderr 캡처) ===")
    try:
        result = subprocess.run(
            ["simulate", "simulation.input"],
            cwd=sim_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )
        print(f"Return code: {result.returncode}")
        print("--- STDOUT (마지막 2000자) ---")
        print(result.stdout[-2000:])
        print("--- STDERR (마지막 2000자) ---")
        print(result.stderr[-2000:])
        if result.returncode != 0:
            print("[치명적] 0이 아닌 return code. 위 STDERR을 확인하세요.")
    except subprocess.TimeoutExpired:
        print("[치명적] 시뮬레이션이 타임아웃됨 (무한루프 또는 행업 가능성)")
    except FileNotFoundError:
        print("[치명적] simulate 실행파일을 찾을 수 없음 (PATH 문제)")
    print()

if __name__ == "__main__":
    sim_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_env()
    ok = check_simulate_binary()
    framework_name, forcefield_name = (None, None)
    result = check_input_files(sim_dir)
    if result:
        framework_name, forcefield_name = result
    check_forcefield_atom_types(sim_dir, framework_name, forcefield_name)
    if ok:
        run_actual_simulation(sim_dir)
