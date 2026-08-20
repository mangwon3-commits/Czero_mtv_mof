#!/usr/bin/env bash
# Produce two small, immutable hand-off packages without touching a live run.
#
# Usage: bash prepare_split_raspa_packages.sh 20260818
# Output: D:\MTV-ZIF_water_v3_<tag> and D:\MTV-ZIF_density_v3_<tag>
set -euo pipefail

TAG="${1:-$(date +%Y%m%d)}"
P="$(cd "$(dirname "$0")" && pwd)"
RASPA_SHARE="${HOME}/RASPA/simulations/share/raspa"
OUT="/mnt/d"
WATER="${OUT}/MTV-ZIF_water_v3_${TAG}"
DENSITY="${OUT}/MTV-ZIF_density_v3_${TAG}"

for d in "$WATER" "$DENSITY"; do
    if [ -e "$d" ]; then
        echo "[STOP] existing package is never overwritten: $d" >&2
        exit 2
    fi
done

need() { [ -e "$1" ] || { echo "[STOP] missing: $1" >&2; exit 1; }; }
for t in base saIm025 saIm050 saIm075 saIm100; do
    need "$P/21_ZIF69_MTV/charged_v3/${t}_DDEC6.cif"
done
need "$RASPA_SHARE/forcefield/UFF_MOF"
need "$P/19_WaterCompetition/water.def"

copy_common() {
    local dest="$1"
    mkdir -p "$dest/21_ZIF69_MTV/charged_v3" "$dest/raspa_share/forcefield"
    for t in base saIm025 saIm050 saIm075 saIm100; do
        cp "$P/21_ZIF69_MTV/charged_v3/${t}_DDEC6.cif" \
           "$dest/21_ZIF69_MTV/charged_v3/"
    done
    cp -a "$RASPA_SHARE/forcefield/UFF_MOF" "$dest/raspa_share/forcefield/"
    # [2026-08-20] 소스 빌드 RASPA 에는 molecules/TraPPE 가 아예 없습니다.
    # conda 배포본만 가정하고 분자 정의를 빼면, 소스 빌드 기기는
    # "Cannot open .../molecules/TraPPE/CO2.def" 로 즉시 죽습니다(지인 실측).
    # 반드시 TraPPE/ 하위에 놓아야 읽힙니다 -- molecules/ 바로 밑은 안 읽힙니다.
    mkdir -p "$dest/raspa_share/molecules/TraPPE"
    for m in CO2.def N2.def; do
        cp "$RASPA_SHARE/molecules/TraPPE/$m" "$dest/raspa_share/molecules/TraPPE/"
    done
}

copy_common "$WATER"
mkdir -p "$WATER/19_WaterCompetition"
cp "$P/21_ZIF69_MTV/run_water.py" "$WATER/21_ZIF69_MTV/"
cp "$P/21_ZIF69_MTV/run_water_v3.py" "$WATER/21_ZIF69_MTV/"
cp "$P/19_WaterCompetition/water.def" "$WATER/19_WaterCompetition/"
cp "$P/21_ZIF69_MTV/EXTERNAL_WATER_V3.md" "$WATER/README.md"

copy_common "$DENSITY"
mkdir -p "$DENSITY/10_DensityMap"
cp "$P/21_ZIF69_MTV/run_density_map.py" "$DENSITY/21_ZIF69_MTV/"
cp "$P/21_ZIF69_MTV/run_density_v3.py" "$DENSITY/21_ZIF69_MTV/"
cp "$P/10_DensityMap/export_diff_vtk.py" "$DENSITY/10_DensityMap/"
cp "$P/21_ZIF69_MTV/LAPTOP_DENSITY_V3.md" "$DENSITY/README.md"

for d in "$WATER" "$DENSITY"; do
    (cd "$d" && find . -type f -print0 | sort -z | xargs -0 sha256sum) > "$d/CHECKSUMS.txt"
done

echo "[OK] water:   $WATER"
echo "[OK] density: $DENSITY"
