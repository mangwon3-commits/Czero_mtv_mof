# Laptop: 48-hour v3 water-comparison allocation

**Allocation:** 8 physical cores, one RASPA `simulate` per core.
**Priority:** highest outstanding evidence gap for the v3 candidate decision.

The dry working-capacity batch is complete.  The next laptop allocation is the
v3 CO2/H2O competition run, not a duplicate GCMC run and not LAMMPS.  Water
competition is the required gate for the apparently strong dry-TSA saIm100
result.  `run_water_v3.py` uses the corrected, fixed-cell-relaxed `charged_v3`
structures and the five-site TIP5P-Ew water definition.

## Time allocation

| Window | Cores | Work | Completion criterion |
|---|---:|---|---|
| 0-42 h | 8 | 5 structures x RH 0/25/50/90 = 20 water-competition jobs | `v3_water/water_results.json`, 20/20 rows |
| 42-48 h | 0-8 | Validate/package results; resume only incomplete jobs | JSON, log, status, and SHA-256 archive |

The 42-hour value is conservative.  Do not fill unused time with Zeo++,
LAMMPS, DAC, or another parent topology.  If the water batch finishes early,
stop after packaging and wait for the desktop-side humid/stability gates; a
second unplanned simulation would weaken rather than strengthen the decision.

## Start command (run in the laptop WSL terminal)

```bash
cd ~/mof_project/21_ZIF69_MTV
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
WATER_V3_WORKERS=8 python run_water_v3.py 2>&1 | tee water_v3.log
```

Before starting, confirm no other RASPA process is active on the laptop:

```bash
pgrep -x simulate || true
```

## Resume and safety

- Do not change code, force field, charge CIF, worker setting, or run path
  while jobs exist.
- If WSL/PC restarts without a configuration change, repeat exactly the same
  start command.  Completed jobs are recovered and incomplete jobs use the
  checkpoint/fallback logic.
- Do not run `git pull`, `rebase`, `clean`, or delete `water_runs_v3/` while
  the batch runs.
- Do not run LAMMPS/Zeo++ alongside this batch.  It is unnecessary here and
  previously caused a WSL-level OOM cascade.

## Completion hand-off

```bash
cd ~/mof_project/21_ZIF69_MTV
test -s v3_water/water_results.json && echo 'RESULT_JSON_READY'
mkdir -p ~/mof_export
tar czf ~/mof_export/zif69_v3_water_laptop.tar.gz \
  v3_water/water_results.json water_v3.log
sha256sum ~/mof_export/zif69_v3_water_laptop.tar.gz \
  > ~/mof_export/zif69_v3_water_laptop.sha256
```

Send the archive and `.sha256` file to the desktop.  Do not merge the laptop
branch into `master`; the desktop verifies, commits, and updates Notion.
