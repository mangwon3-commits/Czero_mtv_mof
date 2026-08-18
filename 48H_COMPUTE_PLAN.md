# MTV-ZIF: next 48-hour execution plan

**Created:** 2026-08-18 KST
**Authority:** this plan is the execution contract for desktop, laptop, and
external-helper work through 2026-08-20 KST.  Any Claude session must read this
file, `CLAUDE.md`, and `SESSION_LOG.md` before launching, editing, deleting, or
ranking a calculation.

## 1. What has been learned from the committed history

The project has passed three distinct structure generations.  They are not
interchangeable.

| Generation | Meaning | Use status |
|---|---|---|
| v1 | Wrong fixed attachment atom and non-exact linker fractions | **Invalid for all substituted structures** |
| v2 | Correct attachment and exact composition | Valid geometry control; unrelaxed parent geometry |
| v3 | v2 structures after fixed-cell GFN-FF atomic relaxation and fresh PACMAN charges | **Current production generation** |

The commits `952573b` through `a10be20` establish the critical chain: detect
the defect -> rebuild/audit -> relax only atoms while retaining experimental
cell -> recompute charges -> smoke test -> GCMC production.  Do not quote a v1
number as a candidate result.  Do not combine a v2 water result with a v3
adsorption result as if they are one material assessment.

Locked calculation protocol: UFF_MOF host; PACMAN DDEC6 charges; 2x2x2 cells;
12 A cutoff; Ewald 1e-6; 5,000 initialization + 15,000 production cycles;
TIP5P-Ew five-site water; CO2 geometry from TraPPE but Garcia-Sanchez 2009
non-bonded parameters from UFF_MOF.  Differences below 1.5 sigma are not
ranked.

Already complete and preserved:

- v3 GCMC: `21_ZIF69_MTV/results_v3.json` (31 structures)
- v3 fixed-cell relaxation: `relax_v3_results.json`, `relax_v3_judged.json`
- v2 water control: `v2_water/water_results.json` (20/20); saIm100 is eligible
  under the unchanged 50% rule at 58.5 +/- 2.2%, but remains the lowest-margin
  and highest-water composition.
- ZIF-67 preparation, exact-fraction candidate structures, and IR/Raman
  validation protocol.  This remains an experimental incorporation project,
  not a substitute for the ZIF-69 flue-gas decision.

## 2. Running work at the time of this plan

| Machine | Work | Output that defines completion | Rule |
|---|---|---|---|
| Desktop | v3 humid working capacity: base/saIm050/saIm075/saIm100 x ads/TSA/VSA | `v3_humid_wc/humid_working_capacity.json` | Running with 7 RASPA workers; never start Zeo++ concurrently |
| Laptop | v3 density maps: five structures x charge ON/OFF | `density_v3/density_results.json` + retained VTK grids | 8 physical RASPA workers; `LAPTOP_DENSITY_V3.md` |
| External helper | v3 water competition: five saIm compositions x RH 0/25/50/90 | `v3_water/water_results.json` | 16 physical RASPA workers; `EXTERNAL_WATER_V3.md` |

The desktop must not duplicate laptop or helper work.  RASPA jobs are
job-resumable: rerunning the same *unchanged* runner is safe; changing its
settings requires a new run directory.

## 3. Execution order and gates

### Hours 0-12: finish the present RASPA wave

1. Let desktop humid working capacity finish.  Do not change its runner while
   worker children exist.  Validate all 12 component outputs, neutral charge,
   and propagated working-capacity uncertainty before accepting JSON.
2. Laptop dry-WC was received, hash-verified, and archived as a raw result.
   Its interpretation correction is recorded in
   `21_ZIF69_MTV/V3_WC_LAPTOP_VALIDATION.md`.
3. External helper runs water-v3.  Laptop runs independent v3 density maps.
   A missing helper result is a scheduling event, not grounds to reuse v2 water
   data in a v3 conclusion.  Do not launch duplicate water jobs unless the
   external run explicitly fails.
4. After each accepted result: write a concise result note, make one focused
   Git commit, push `master`, and update Notion Part 3/Part 6 only with the
   matching-generation result.  Mark the source JSON and calculation version.

### Hours 12-30: structural gate, only after RASPA is idle

5. Audit a v3-specific LAMMPS stability input before production.  The existing
   `risk_screen.py` must not quietly read the old `structures/` directory.  The
   input list must point to the v3 relaxed CIFs and retain the fixed-cell
   policy.  Run one smoke structure first; check its source CIF hash, output
   `min_*.data`, and Zeo++ metrics.
6. Only if the smoke test is valid, run the v3 stability screen with
   `RISK_WORKERS=4` maximum.  Zeo++ needs about 3.2 GB/job; it is prohibited
   while a substantial RASPA wave is active.  Preserve partially completed
   `min_*.data` files for resume.
7. Do not start DAC, a new parent topology, or a full v3 density-map grid in
   this period.  Those are downstream only after the wet regeneration decision
   is defensible.

### Hours 30-42: rank only the supported candidates

8. Build the v3 evidence table combining GCMC, dry WC, humid WC, water-v3,
   and stability.  Apply the pre-registered water rule, PLD/LCD stability
   gate, and 1.5-sigma non-ranking rule.  A high Qst alone cannot win.
9. Recalculate the process-level regeneration budget from the accepted v3 WC
   and humid result.  This is a lightweight post-processing step, not a new
   molecular simulation.
10. Select at most two candidates for v3 charge-on/off density maps.  Run only
    after selection, with RASPA idle, and retain raw VTK grids.  The density map
    explains a chosen result; it is not a screening shortcut.

### Hours 42-48: report package and controlled next decision

11. Update Notion Part 0-D (relaxation basis), Part 3 (water/working capacity),
    and Part 6 (gme candidate decision).  Explicitly retire v1 values instead
    of overwriting their history.
12. Commit/push data, validation notes, and the decision table.  Generate the
    21 August submission figures only from accepted v3 data.
13. Hold DAC execution.  The DAC plan remains a design document until the
    flue-gas v3 decision, experimental synthesis feedback, and institutional
    compute decision are available.

## 4. Non-negotiable resource and integrity constraints

- Physical-core budget is eight.  RASPA may use up to eight workers; leave no
  Zeo++ process running with it.
- Never run `get_all_distances(mic=True)` over a relaxed supercell.  Use the
  neighbor-list geometry gate.
- Keep at least 4 GB free on C:.  If C: falls below 2 GB, do not launch a new
  heavy job; report first.  Do not delete `density_v2/` raw VTK grids.
- Do not run `wsl --shutdown`, compact the VHDX, or alter Fast Startup while a
  calculation exists.
- Launch background work with `setsid nohup ... < /dev/null &`; do not edit a
  live shell script in place.  Make an atomic replacement and restart only at
  a defined gate.
- Before changing a runner, record the old SHA256 and clear only the affected
  run directory after confirming there is no desired unharvested output.

## 5. Laptop-session instructions (superseded after dry-WC completion)

The laptop must first let the existing v3 dry-WC batch finish.  It must **not**
run `git pull`, `git rebase`, `git clean`, or delete `wc_runs_v3/` during work.

```bash
cd ~/mof_project/21_ZIF69_MTV
pgrep -x simulate | wc -l
tail -n 40 wc_v3.log
test -s v3_wc/working_capacity.json && echo 'RESULT_JSON_READY'
```

When `RESULT_JSON_READY` appears, validate and package only the result payload:

```bash
cd ~/mof_project/21_ZIF69_MTV
python - <<'PY'
import json
p = 'v3_wc/working_capacity.json'
x = json.load(open(p))
need = {'base','saIm025','saIm050','saIm075','mslm075','saIm100'}
have = set(x)
print('targets:', sorted(have))
assert need <= have, (need - have)
print('VALID: six targets present')
PY
mkdir -p ~/mof_export
tar czf ~/mof_export/zif69_v3_wc_laptop.tar.gz \
  v3_wc/working_capacity.json wc_v3.log wc_v3_status.log
sha256sum ~/mof_export/zif69_v3_wc_laptop.tar.gz \
  > ~/mof_export/zif69_v3_wc_laptop.sha256
```

Send those two files to the desktop session (or attach them in chat).  Do not
merge the laptop branch into `master`: its history diverged before the current
desktop production commits.  The desktop will verify the hash, place the JSON
in the canonical path, commit it, and update Notion.

If the runner died *without any code/configuration change*, resume exactly:

```bash
cd ~/mof_project/21_ZIF69_MTV
export RASPA_DIR=$HOME/RASPA/simulations
export PATH=$HOME/miniconda3/envs/czeromof/bin:$PATH
WC_V3_WORKERS=6 python run_wc_v3.py 2>&1 | tee -a wc_v3.log
```

The dry-WC batch is now complete.  The active next instruction is
`21_ZIF69_MTV/LAPTOP_DENSITY_V3.md`; water-v3 is assigned to the external
16-core machine.

## 6. Mandatory read order for every Claude session

1. `CLAUDE.md`
2. `SESSION_LOG.md`
3. This file
4. `21_ZIF69_MTV/STRUCTURE_DEFECT.md`
5. `21_ZIF69_MTV/AUDIT_20260814.md`

Then run `bash bgstate.sh` and add a dated entry to `SESSION_LOG.md` before
starting any process.  This rule is deliberate: this project has repeatedly
encountered failures that looked like scientific results.
