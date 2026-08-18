# External 16-core assignment: v3 water competition

**Assigned work:** five ZIF-69 v3 structures x RH 0/25/50/90 = 20 binary
CO2/H2O GCMC jobs. This is the decisive humidity gate and is expected to take
about 24 hours on 16 physical cores.

Use only the prepared `MTV-ZIF_계산지원` package.  Its `charged_v3` CIFs carry
fresh PACMAN charges for fixed-cell GFN-FF-relaxed structures.  Do not replace
the supplied five-site `19_WaterCompetition/water.def` with a RASPA default
three-site water file.

```bash
cd ~/mof_project/21_ZIF69_MTV
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
cp -r ../raspa_share/* "$RASPA_DIR/share/raspa/"
WATER_V3_WORKERS=16 python run_water_v3.py 2>&1 | tee water_v3.log
```

Completion file: `v3_water/water_results.json`.  Return that JSON plus
`water_v3.log` in a `.tar.gz` archive with a SHA-256 sidecar.  If the host
restarts, rerun the exact same command: completed jobs are cached and active
jobs use the checkpoint/fallback logic.
