# Laptop assignment: v3 charge-on/off density maps

**Role:** laptop 8 physical cores, after its dry-WC hand-off.
**Why this work:** the 16-core external machine is assigned to the long water
competition gate.  This batch is independent, produces the VTK evidence needed
for the presentation, and does not duplicate any production number.

## Scope

Five corrected-and-relaxed ZIF-69 structures (`base`, `saIm025`, `saIm050`,
`saIm075`, `saIm100`) each run with framework charges ON and OFF: 10 RASPA
jobs.  The normalized ON-OFF density difference cancels the Lennard-Jones term
and maps the spatial electrostatic redistribution of CO2.  It is not an
additional adsorption ranking calculation.

## Resource/time envelope

- Use `DENSITY_V3_WORKERS=8`: one single-threaded RASPA job per physical core.
- Allow 8-16 hours, then reserve the remaining 32+ hours for extraction,
  validation, and a water-v3 backup only if the external run fails.
- Require at least 5 GB local free disk before start.  VTK grids are retained;
  do not delete them to make a progress counter look tidy.
- Do not run this together with a local water batch, LAMMPS, or Zeo++.

## Start command

```bash
cd ~/mof_project/21_ZIF69_MTV
pgrep -x simulate && { echo '다른 RASPA 작업 실행 중 — 시작하지 않음'; exit 1; }
df -h .
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
setsid nohup env DENSITY_V3_WORKERS=8 \
  python -u run_density_v3.py > density_v3.log 2>&1 < /dev/null &
```

## Validation and hand-off

Completion requires `density_v3/density_results.json` and at least one
`*DensityProfile*` VTK file in each of ten `density_v3/<tag>__q_on|q_off/`
folders.  Package the JSON, log, and `density_v3/` directory.  VTK is a primary
result, so do not send only a screenshot or only the JSON.

```bash
cd ~/mof_project/21_ZIF69_MTV
test -s density_v3/density_results.json && echo 'RESULT_JSON_READY'
find density_v3 -type f -name '*DensityProfile*' | wc -l
mkdir -p ~/mof_export
tar czf ~/mof_export/zif69_v3_density_laptop.tar.gz density_v3 density_v3.log
sha256sum ~/mof_export/zif69_v3_density_laptop.tar.gz \
  > ~/mof_export/zif69_v3_density_laptop.sha256
```
